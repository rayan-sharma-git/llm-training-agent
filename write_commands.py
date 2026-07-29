import os
path = r"d:\Documents\LLM_Training_Agent\PROJECT_TEMPLATE\extension\src\commands\index.ts"
content = open(r"d:\Documents\LLM_Training_Agent\commands_content.txt","r",encoding="utf-8").read()
with open(path,"w",encoding="utf-8") as f:
    f.write(content)
print("Done")
