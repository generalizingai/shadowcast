#!/bin/zsh
# Compile the Apple Vision subject-lift tool (macOS 14+). Output: ~/.config/shadowcast/bin/cutout
set -e
OUT="$HOME/.config/shadowcast/bin"; mkdir -p "$OUT"
swiftc -O "$(dirname "$0")/cutout.swift" -o "$OUT/cutout"
echo "built $OUT/cutout"
