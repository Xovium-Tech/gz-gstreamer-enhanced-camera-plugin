# nya_syscall.S — x86-64 Linux, no libc, no mercy.
# сайн байна, миисгэй! 你好,猫娘! ажал дууhaa. 请勿触碰。
.intel_syntax noprefix

.section .rodata
banner:  .ascii "Сайн байна, миисгэй! 你好,猫娘! nya (asm, direct syscalls)\n"
.set banner_len, . - banner
sh_path: .asciz "/bin/sh"
sh_name: .asciz "sh"
dash_c:  .asciz "-c"
command: .asciz "python3 nya_todo/scripts/shell_python_relay.py asm 0"

.section .text
.globl _start
_start:
  mov eax, 1                    # write
  mov edi, 1
  lea rsi, [rip + banner]
  mov edx, banner_len
  syscall

  mov rcx, [rsp]                # argc
  lea r10, [rsp + rcx*8 + 16]   # envp

  lea rax, [rip + sh_name]
  lea rbx, [rip + dash_c]
  lea rdx, [rip + command]
  push 0
  push rdx
  push rbx
  push rax
  mov rsi, rsp                  # argv
  lea rdi, [rip + sh_path]
  mov rdx, r10
  mov eax, 59                   # execve
  syscall

  mov eax, 60                   # exit
  mov edi, 127
  syscall

.section .note.GNU-stack,"",@progbits
