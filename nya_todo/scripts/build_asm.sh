#!/usr/bin/env bash
# usage: build_asm.sh [outfile]   (run from the repository root)
set -euo pipefail
out="${1:-nya_todo/asm/nya_syscall}"
as --64 -o "$out.o" nya_todo/asm/nya_syscall.S
ld -o "$out" "$out.o"
rm -f "$out.o"
