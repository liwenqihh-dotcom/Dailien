import re

with open('memory-maze.html', 'r', encoding='utf-8') as f:
    content = f.read()

style_start = content.index('<style>')
style_end = content.index('</style>') + len('</style>')
css_part = content[style_start:style_end]
rest_before = content[:style_start]
rest_after = content[style_end:]

lines = css_part.split('\n')
new_lines = []
in_root = False

for line in lines:
    if ':root[data-theme=' in line:
        in_root = True
    if in_root and line.strip() == '}':
        in_root = False
        new_lines.append(line)
        continue
    if in_root:
        new_lines.append(line)
        continue

    # Replace #2ecc71 with var(--green)
    if '#2ecc71' in line:
        line = line.replace('#2ecc71', 'var(--green)')

    # Replace #e74c3c with var(--red)
    if '#e74c3c' in line:
        line = line.replace('#e74c3c', 'var(--red)')

    new_lines.append(line)

new_css = '\n'.join(new_lines)
new_content = rest_before + new_css + rest_after

with open('memory-maze.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done')
