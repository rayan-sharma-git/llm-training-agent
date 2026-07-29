const fs = require("fs");
const path = require("path");
const BASE = path.join("d:", "Documents", "LLM_Training_Agent", "PROJECT_TEMPLATE", "extension", "src");
function w(rel, content) {
  const p = path.join(BASE, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content, "utf-8");
  console.log("OK: " + rel);
}
console.log("Builder ready");
