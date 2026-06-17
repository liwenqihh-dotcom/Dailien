#!/usr/bin/env python3
"""Generate three warm line-comic illustrations for a Chinese article via APIMart."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.apimart.ai"
MODEL = "gemini-3-pro-image-preview"
DEFAULT_STYLE = (
    "手绘线条漫画风格，温暖、可爱、有故事感，适合中文内容平台配图；"
    "画面干净，主体清晰，柔和暖色，轻盈线稿，不写实，不赛博朋克，不做3D渲染。"
)
NEGATIVE_STYLE = (
    "不要照片写实，不要赛博朋克，不要英文，不要水印，不要logo，不要密集文字，"
    "不要阴暗科幻感，不要过度复杂背景。"
)
SEGMENTS = (
    ("01-opening", "前30%", 0.00, 0.30, "开篇配图，需要像故事入口，让读者愿意继续读。"),
    ("02-middle", "中间30%", 0.35, 0.65, "中段配图，需要承接主要冲突、方法、观察或情绪转折。"),
    ("03-ending", "最后30%", 0.70, 1.00, "结尾配图，需要呈现收束、余味、行动感或温柔结论。"),
)
TERMINAL_SUCCESS = {"completed", "succeeded", "success", "done"}
TERMINAL_FAILURE = {"failed", "error", "cancelled", "canceled", "timeout"}


def https_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate exactly three article illustrations with APIMart Nano Banana 2."
    )
    parser.add_argument("article", help="Path to a UTF-8 article text/markdown file.")
    parser.add_argument("--output-dir", default="article-images", help="Directory for images and manifest.")
    parser.add_argument("--api-key", default=None, help="APIMart API key. Prefer APIMART_API_KEY.")
    parser.add_argument("--api-base", default=API_BASE, help="APIMart API base URL.")
    parser.add_argument(
        "--aspect",
        choices=("horizontal", "square"),
        default="horizontal",
        help="Composition preference. Use horizontal for article body images, square for feed covers.",
    )
    parser.add_argument("--poll-interval", type=float, default=5.0, help="Seconds between task polls.")
    parser.add_argument("--timeout", type=float, default=300.0, help="Seconds to wait for each task.")
    parser.add_argument("--dry-run", action="store_true", help="Write prompts/manifest without API calls.")
    parser.add_argument(
        "--max-segment-chars",
        type=int,
        default=1400,
        help="Maximum characters from each article segment to include in the image prompt.",
    )
    return parser.parse_args()


def read_article(path: Path) -> str:
    raw = path.read_bytes()
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError as exc:
            last_error = exc
    else:
        raise SystemExit(f"Could not decode article as UTF-8 or UTF-16: {path}: {last_error}")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise SystemExit(f"Article is empty: {path}")
    return text


def compact_text(text: str, limit: int) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    if len(text) <= limit:
        return text
    head = text[: max(0, limit - 20)].rstrip()
    return head + "\n（片段已截断）"


def segment_article(article: str, max_chars: int) -> list[dict[str, Any]]:
    total = len(article)
    items: list[dict[str, Any]] = []
    for slug, label, start_ratio, end_ratio, role in SEGMENTS:
        start = int(total * start_ratio)
        end = max(start + 1, int(total * end_ratio))
        raw = article[start:end]
        items.append(
            {
                "slug": slug,
                "label": label,
                "start_ratio": start_ratio,
                "end_ratio": end_ratio,
                "start_char": start,
                "end_char": end,
                "role": role,
                "excerpt": compact_text(raw, max_chars),
            }
        )
    return items


def build_prompt(segment: dict[str, Any], aspect: str) -> str:
    composition = "横向构图，适合作为文章段落配图" if aspect == "horizontal" else "方形构图，适合作为内容平台信息流配图"
    return f"""请根据下面这段中文文章内容，生成一张配图。

用途：{segment["label"]}，{segment["role"]}
固定风格：{DEFAULT_STYLE}
构图：{composition}，主体明确，留白舒适，背景简洁。
文字规则：如果画面中出现文字、标牌、便签、对话气泡，必须全部使用简体中文；除非必要，尽量不放文字。
避免：{NEGATIVE_STYLE}

请把文章片段转化为一个具体、温暖、有叙事感的生活化漫画场景，而不是关键词拼贴。

文章片段：
{segment["excerpt"]}
""".strip()


def request_json(method: str, url: str, api_key: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60, context=https_context()) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc}") from exc


def extract_task_id(payload: dict[str, Any]) -> str:
    data = payload.get("data")
    candidates = [
        payload.get("task_id"),
        payload.get("id"),
        data.get("task_id") if isinstance(data, dict) else None,
        data.get("id") if isinstance(data, dict) else None,
        data[0].get("task_id") if isinstance(data, list) and data and isinstance(data[0], dict) else None,
        data[0].get("id") if isinstance(data, list) and data and isinstance(data[0], dict) else None,
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate)
    raise RuntimeError(f"Could not find task_id in response: {json.dumps(payload, ensure_ascii=False)}")


def normalize_status(payload: dict[str, Any]) -> str:
    raw_data = payload.get("data")
    if isinstance(raw_data, dict):
        data = raw_data
    elif isinstance(raw_data, list) and raw_data and isinstance(raw_data[0], dict):
        data = raw_data[0]
    else:
        data = payload
    for key in ("status", "state", "task_status"):
        value = data.get(key) if isinstance(data, dict) else None
        if value:
            return str(value).lower()
    return ""


def find_image_values(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        if value.startswith(("http://", "https://")) or len(value) > 200:
            found.append(value)
    elif isinstance(value, list):
        for item in value:
            found.extend(find_image_values(item))
    elif isinstance(value, dict):
        for key in ("url", "image_url", "b64_json", "base64", "content"):
            if key in value:
                found.extend(find_image_values(value[key]))
        for key in ("images", "output", "result", "data"):
            if key in value:
                found.extend(find_image_values(value[key]))
    return found


def submit_generation(api_base: str, api_key: str, prompt: str) -> tuple[str, dict[str, Any]]:
    url = urllib.parse.urljoin(api_base.rstrip("/") + "/", "v1/images/generations")
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "response_format": "url",
    }
    response = request_json("POST", url, api_key, payload)
    return extract_task_id(response), response


def poll_task(api_base: str, api_key: str, task_id: str, interval: float, timeout: float) -> dict[str, Any]:
    url = urllib.parse.urljoin(api_base.rstrip("/") + "/", f"v1/tasks/{urllib.parse.quote(task_id)}")
    deadline = time.time() + timeout
    last_payload: dict[str, Any] | None = None
    while time.time() < deadline:
        payload = request_json("GET", url, api_key)
        last_payload = payload
        status = normalize_status(payload)
        if status in TERMINAL_SUCCESS:
            return payload
        if status in TERMINAL_FAILURE:
            raise RuntimeError(f"Task {task_id} failed with status {status}: {json.dumps(payload, ensure_ascii=False)}")
        time.sleep(interval)
    raise RuntimeError(f"Task {task_id} timed out after {timeout}s. Last payload: {json.dumps(last_payload, ensure_ascii=False)}")


def save_image(value: str, output_path: Path) -> Path:
    if value.startswith(("http://", "https://")):
        request = urllib.request.Request(value, headers={"User-Agent": "CodexArticleImageSkill/1.0"})
        with urllib.request.urlopen(request, timeout=120, context=https_context()) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")
        suffix = mimetypes.guess_extension(content_type.split(";")[0].strip()) or output_path.suffix or ".png"
        output_path = output_path.with_suffix(suffix)
        output_path.write_bytes(data)
        return output_path

    clean_value = value.split(",", 1)[1] if value.startswith("data:") and "," in value else value
    output_path = output_path.with_suffix(".png")
    output_path.write_bytes(base64.b64decode(clean_value))
    return output_path


def main() -> int:
    args = parse_args()
    article_path = Path(args.article).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    article = read_article(article_path)
    segments = segment_article(article, args.max_segment_chars)
    manifest: dict[str, Any] = {
        "article": str(article_path),
        "model": MODEL,
        "api_base": args.api_base,
        "aspect": args.aspect,
        "dry_run": args.dry_run,
        "segments": [],
    }

    api_key = args.api_key or os.environ.get("APIMART_API_KEY")
    if not args.dry_run and not api_key:
        raise SystemExit("Missing API key. Set APIMART_API_KEY or pass --api-key.")

    for segment in segments:
        prompt = build_prompt(segment, args.aspect)
        entry = {k: segment[k] for k in ("slug", "label", "start_ratio", "end_ratio", "start_char", "end_char")}
        entry["prompt"] = prompt

        if not args.dry_run:
            task_id, submit_payload = submit_generation(args.api_base, api_key, prompt)
            final_payload = poll_task(args.api_base, api_key, task_id, args.poll_interval, args.timeout)
            images = find_image_values(final_payload)
            if not images:
                raise RuntimeError(f"No image URL/base64 found for task {task_id}: {json.dumps(final_payload, ensure_ascii=False)}")
            saved_path = save_image(images[0], output_dir / f"{segment['slug']}.png")
            entry.update(
                {
                    "task_id": task_id,
                    "submit_response": submit_payload,
                    "final_response": final_payload,
                    "image_source": images[0] if images[0].startswith(("http://", "https://")) else "[base64]",
                    "output_path": str(saved_path),
                }
            )

        manifest["segments"].append(entry)

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote manifest: {manifest_path}")
    if args.dry_run:
        print("Dry run complete. No API calls were made.")
    else:
        for item in manifest["segments"]:
            print(item.get("output_path", item["slug"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
