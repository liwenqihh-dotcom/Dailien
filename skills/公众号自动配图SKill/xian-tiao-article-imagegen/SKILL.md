---
name: xian-tiao-article-imagegen
description: Generate exactly three Chinese article illustrations with APIMart's gemini-3-pro-image-preview model. Use when Codex needs to create content-platform article images after an article is written, especially requests for "文章配图", "线条插画配图", "手绘线条漫画", or generating one image for the opening 30%, middle 30%, and ending 30% of an article.
---

# 线条插画配图生成skill

## Workflow

1. Accept a completed article as a text file or pasted content.
2. Create exactly three images:
   - `01-opening`: the first 30% of the article.
   - `02-middle`: a centered 30% window around the article midpoint.
   - `03-ending`: the final 30% of the article.
3. Keep the visual style fixed: hand-drawn line comic illustration, warm, cute, narrative, clean composition, clear subject, suitable for Chinese content platforms. Do not drift into realistic, cyberpunk, 3D render, dark sci-fi, busy collage, or poster-heavy styles.
4. If any visible text appears inside an image, it must be simplified Chinese. Prefer no text unless the article clearly benefits from a short Chinese label, sign, note, or speech bubble.
5. Use APIMart with model `gemini-3-pro-image-preview` through the helper script. Never hardcode API keys in skill files, prompts, or committed artifacts.

## Quick Start

Set the API key in the shell before running:

```bash
export APIMART_API_KEY="..."
```

Generate images from an article:

```bash
python3 scripts/generate_article_illustrations.py path/to/article.txt --output-dir ./article-images
```

Preview prompts without calling the API:

```bash
python3 scripts/generate_article_illustrations.py path/to/article.txt --output-dir ./article-images --dry-run
```

The script writes:

- `01-opening.png`, `02-middle.png`, `03-ending.png` when downloads succeed.
- `manifest.json` with segment windows, prompts, task ids, result URLs, and output paths.

## Prompt Rules

Use the script's generated prompts by default. If editing prompts manually, preserve these constraints:

- Output language: Chinese for any in-image text.
- Style: hand-drawn line comic, warm soft colors, cute but not childish, story-like, clean background, clear main subject.
- Composition: horizontal or square; choose horizontal for narrative scenes and square for social-feed covers.
- Negative constraints: no photorealism, no cyberpunk, no 3D render, no English words, no watermark, no logo, no cluttered text blocks.
- Content fidelity: summarize the selected article segment into one concrete visual scene instead of illustrating abstract keywords.

## APIMart Reference

Read `references/apimart.md` when changing the script, debugging API behavior, or checking request/response assumptions.
