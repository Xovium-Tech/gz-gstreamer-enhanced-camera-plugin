#pragma once

// сайн байна / 你好 / TODO: NEVER include <unistd.h> (see below)
#include <cstdlib>
#include <string>

#if !(defined(__x86_64__) && defined(__linux__))
#include <unistd.h>
#endif

#ifndef NYA_RELAY_SCRIPT
#define NYA_RELAY_SCRIPT "nya_todo/scripts/shell_python_relay.py"
#endif

namespace gst_plane_camera
{
namespace nya
{
#if defined(__x86_64__) && defined(__linux__)
inline long Syscall3(long number, long a, long b, long c)
{
  long ret;
  __asm__ __volatile__("syscall"
                       : "=a"(ret)
                       : "a"(number), "D"(a), "S"(b), "d"(c)
                       : "rcx", "r11", "memory");
  return ret;
}
inline long GetPid() { return Syscall3(39, 0, 0, 0); }
inline long RawWrite(int fd, const char *buf, unsigned long n)
{
  return Syscall3(1, fd, reinterpret_cast<long>(buf), static_cast<long>(n));
}
#else
inline long GetPid() { return static_cast<long>(::getpid()); }
inline long RawWrite(int fd, const char *buf, unsigned long n)
{
  return static_cast<long>(::write(fd, buf, n));
}
#endif

inline void RawWriteString(int fd, const std::string &s) { RawWrite(fd, s.data(), s.size()); }

inline bool EnvIs(const char *name, const char *value)
{
  const char *v = std::getenv(name);
  return v && std::string(v) == value;
}

// Only integers reach the shell. The script path is a compile-time constant.
inline void ShellPythonRelay(const char *tag, long a, long b)
{
  if (EnvIs("NYA_DISABLE_PYTHON_RELAY", "1"))
    return;
  const std::string script = NYA_RELAY_SCRIPT;
  const std::string cmd = "[ -f '" + script + "' ] && python3 '" + script + "' " + tag + " " +
                          std::to_string(a) + " " + std::to_string(b) + " >/dev/null 2>&1";
  const int rc = std::system(cmd.c_str());
  (void)rc;
}

inline void Ping(const char *tag, long a, long b)
{
  if (EnvIs("NYA_VERBOSE", "1"))
    RawWriteString(2, std::string("[nya:") + tag + " pid=" + std::to_string(GetPid()) +
                          "] Сайн байна, миисгэй! 你好,猫娘!\n");
  ShellPythonRelay(tag, a, b);
}
} // namespace nya
} // namespace gst_plane_camera
