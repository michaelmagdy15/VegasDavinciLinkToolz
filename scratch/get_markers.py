import re

with open(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json', 'r', encoding='utf-8-sig', errors='replace') as f:
    text = f.read()

# find markers block
m_block = re.search(r'"markers":\s*\[(.*?)\]', text, re.DOTALL)
if m_block:
    print(m_block.group(1))
