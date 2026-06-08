import re

with open('memory-maze.html', 'r', encoding='utf-8') as f:
    content = f.read()

style_match = re.search(r'(<style>)(.*?)(</style>)', content, re.DOTALL)
if not style_match:
    print("ERROR: No style block found")
    exit(1)

css = style_match.group(2)

replacements = [
    ('color:rgba(255,255,255,0.9)', 'color:var(--text)'),
    ('color:rgba(255,255,255,0.8)', 'color:var(--text-dim)'),
    ('color:rgba(255,255,255,0.7)', 'color:var(--text-dim)'),
    ('color:rgba(255,255,255,0.6)', 'color:var(--text-dimmer)'),
    ('color:rgba(255,255,255,0.5)', 'color:var(--text-dimmer)'),
    ('color:rgba(255,255,255,0.4)', 'color:var(--text-faint)'),
    ('color:rgba(255,255,255,0.35)', 'color:var(--text-faint)'),
    ('color:rgba(255,255,255,0.3)', 'color:var(--text-faint)'),
    ('color:rgba(255,255,255,0.25)', 'color:var(--text-faint)'),
    ('color:rgba(255,255,255,0.2)', 'color:var(--text-faintest)'),
    ('color:rgba(255,255,255,0.15)', 'color:var(--text-faintest)'),
    ('color:#fff', 'color:var(--text)'),
    ('color:#ffffff', 'color:var(--text)'),

    ('border:2px solid rgba(255,255,255,0.8)', 'border:2px solid var(--border-strong)'),
    ('border:2px solid rgba(255,255,255,0.6)', 'border:2px solid var(--border)'),
    ('border:1px solid rgba(255,255,255,0.6)', 'border:1px solid var(--border-strong)'),
    ('border:1px solid rgba(255,255,255,0.5)', 'border:1px solid var(--border-btn)'),
    ('border:1px solid rgba(255,255,255,0.4)', 'border:1px solid var(--border)'),
    ('border:1px solid rgba(255,255,255,0.3)', 'border:1px solid var(--border)'),
    ('border:1px solid rgba(255,255,255,0.25)', 'border:1px solid var(--border-light)'),
    ('border:1px solid rgba(255,255,255,0.2)', 'border:1px solid var(--border-light)'),
    ('border:1px solid rgba(255,255,255,0.15)', 'border:1px solid var(--border-light)'),
    ('border:1px solid rgba(255,255,255,0.1)', 'border:1px solid var(--border-lighter)'),
    ('border:1px solid rgba(255,255,255,0.08)', 'border:1px solid var(--border-lighter)'),
    ('border:1px solid rgba(255,255,255,0.04)', 'border:1px solid var(--border-lighter)'),

    ('border-bottom:1px solid rgba(255,255,255,0.1)', 'border-bottom:1px solid var(--border-lighter)'),
    ('border-bottom:1px solid rgba(255,255,255,0.08)', 'border-bottom:1px solid var(--border-lighter)'),
    ('border-bottom:1px solid rgba(255,255,255,0.04)', 'border-bottom:1px solid var(--border-lighter)'),

    ('border-color:rgba(255,255,255,0.6)', 'border-color:var(--border-strong)'),
    ('border-color:rgba(255,255,255,0.5)', 'border-color:var(--border-btn)'),
    ('border-color:rgba(255,255,255,0.4)', 'border-color:var(--border)'),
    ('border-color:rgba(255,255,255,0.3)', 'border-color:var(--border)'),
    ('border-color:rgba(255,255,255,0.25)', 'border-color:var(--border-light)'),
    ('border-color:rgba(255,255,255,0.2)', 'border-color:var(--border-light)'),
    ('border-color:rgba(255,255,255,0.15)', 'border-color:var(--border-light)'),
    ('border-color:rgba(255,255,255,0.1)', 'border-color:var(--border-lighter)'),
    ('border-color:#fff', 'border-color:var(--text)'),

    ('background:rgba(17,17,17,0.95)', 'background:var(--bg-panel)'),
    ('background:rgba(17,17,17,0.9)', 'background:var(--bg-panel)'),
    ('background:rgba(17,17,17,0.85)', 'background:var(--bg-panel)'),

    ('background:rgba(0,0,0,0.8)', 'background:var(--overlay-strong)'),
    ('background:rgba(0,0,0,0.7)', 'background:var(--overlay-strong)'),
    ('background:rgba(0,0,0,0.6)', 'background:var(--overlay-bg)'),
    ('background:rgba(0,0,0,0.5)', 'background:var(--overlay-bg)'),
    ('background:rgba(0,0,0,0.4)', 'background:var(--overlay-light)'),
    ('background:rgba(0,0,0,0.3)', 'background:var(--overlay-light)'),

    ('background:rgba(0,0,0,0.6);color:rgba(255,255,255,0.8)', 'background:var(--bg-input);color:var(--text-dim)'),
    ('background:rgba(0,0,0,0.4)', 'background:var(--bg-inv)'),
    ('background:rgba(0,0,0,0.1)', 'background:var(--bg-hover)'),

    ('background:rgba(255,255,255,0.06)', 'background:var(--bg-card-done)'),
    ('background:rgba(255,255,255,0.04)', 'background:var(--bg-card-done)'),
    ('background:rgba(255,255,255,0.03)', 'background:var(--bg-hover)'),
    ('background:rgba(255,255,255,0.02)', 'background:var(--bg-card)'),
    ('background:rgba(255,255,255,0.1)', 'background:var(--border)'),
    ('background:rgba(255,255,255,0.15)', 'background:var(--border)'),

    ('border-color:rgba(255,255,255,0.15);color:rgba(255,255,255,0.25)', 'border-color:var(--border-light);color:var(--text-faintest)'),
    ('border-color:rgba(255,255,255,0.1);color:rgba(255,255,255,0.2)', 'border-color:var(--border-lighter);color:var(--text-faintest)'),
    ('border-color:rgba(255,255,255,0.5);color:#fff', 'border-color:var(--border-btn);color:var(--text)'),

    ('background:rgba(0,0,0,0.5)', 'background:var(--overlay-bg)'),
]

for pattern, replacement in replacements:
    css = css.replace(pattern, replacement)

new_content = content[:style_match.start(1)+7] + css + content[style_match.end(2):]

with open('memory-maze.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done! Replacements applied.")
