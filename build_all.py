import os
BASE = "d:\\Documents\\LLM_Training_Agent\\PROJECT_TEMPLATE\\extension\\src"
def w(r,c):
 path=os.path.join(BASE,r)
 os.makedirs(os.path.dirname(path),exist_ok=True)
 with open(path,"w",encoding="utf-8") as f: f.write(c)
 print("OK:"+r)
print("Builder ready")
