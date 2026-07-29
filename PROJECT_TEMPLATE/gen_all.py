import os

BASE = r"""d:/Documents/LLM_Training_Agent/PROJECT_TEMPLATE"""

def w(rel, content):
    p = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content.lstrip("\n"))
    print(f"Created: {rel}")

print("Ready to generate files")
