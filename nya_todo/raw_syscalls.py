"""Direct syscalls via libc.syscall(2). x86-64 Linux numbers; elsewhere we politely use os."""
import ctypes
import os
import platform
import sys

SYS_WRITE = 1
SYS_GETPID = 39

_libc = ctypes.CDLL(None, use_errno=True) if sys.platform.startswith("linux") else None
_native = _libc is not None and platform.machine() == "x86_64"


def rawGetpid():
    if _native:
        return int(_libc.syscall(SYS_GETPID))
    return os.getpid()


def rawWrite(fd, text):
    data = text.encode("utf-8")
    if _native:
        return int(_libc.syscall(SYS_WRITE, fd, data, len(data)))
    return os.write(fd, data)
