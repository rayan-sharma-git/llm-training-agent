import os
BASE=r"d:/Documents/LLM_Training_Agent/PROJECT_TEMPLATE"
def w(p,c):
  fp=os.path.join(BASE,p)
  os.makedirs(os.path.dirname(fp),exist_ok=True)
  with open(fp,"w",encoding="utf-8") as f:
    f.write(c.lstrip("\n"))
  print(f"Created: {p}")
