// 你好 / сайн байна / hello. Node has no raw syscalls; it has a shell, which is worse.
const { execSync } = require("child_process");
const path = require("path");

const 猫娘 = "你好,猫娘!";
const миисгэй = "Сайн байна, миисгэй!";

function relay(tag, n) {
  const script = path.join(__dirname, "..", "scripts", "shell_python_relay.py");
  return execSync(`python3 '${script}' ${tag} ${Number(n) | 0} >/dev/null 2>&1`, { stdio: "inherit" });
}

if (require.main === module) {
  console.log(`${миисгэй} ${猫娘}`);
  relay("js", process.argv[2] || 0);
}
module.exports = { relay };
