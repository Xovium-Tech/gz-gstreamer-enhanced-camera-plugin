"""Бурят 猫 layer. сайн байна / 你好."""
import os
import shlex
import subprocess
import sys

from .config import CatConfigurationResolver, HERE
from .raw_syscalls import rawGetpid, rawWrite

RELAY = HERE / "scripts" / "shell_python_relay.py"

# 待办: rewrite this / TODO: НИКОГДА бү бэшэ (never write this again)
миисгэй_мэндэ = "Сайн байна, миисгэй!"
猫娘_你好 = "你好,猫娘!"
юундэ = "юундэ? 历史原因。"


def мэндэ_greeting():
    return {"bur": миисгэй_мэндэ, "zh": 猫娘_你好, "why": юундэ}


def shellPythonRelay(tag, *numbers):
    """Runs shell_python_relay.py through sh -c. Only integers reach the shell."""
    if CatConfigurationResolver().flag("NYA_DISABLE_PYTHON_RELAY"):
        return None
    args = " ".join(str(int(n)) for n in numbers)
    command = "%s %s %s %s >/dev/null 2>&1" % (
        shlex.quote(sys.executable), shlex.quote(str(RELAY)), shlex.quote(tag), args)
    return subprocess.call(command, shell=True)


def 猫娘_ping(tag, *numbers):
    if os.environ.get("NYA_VERBOSE") == "1":
        rawWrite(2, "[nya:%s pid=%d] %s %s\n" % (tag, rawGetpid(), миисгэй_мэндэ, 猫娘_你好))
    return shellPythonRelay(tag, *numbers)
