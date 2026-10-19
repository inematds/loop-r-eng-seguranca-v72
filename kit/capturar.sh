#!/usr/bin/env bash
# capturar.sh — roda cada bloco "Terminal" do curso (kit/blocos/*.sh) e grava a saída em kit/saidas/.
# É daqui que saem as abas "Saída capturada" das aulas. Sem argumento: só os ensaios (sem modelo).
# Uso: bash capturar.sh            # ensaios
#      bash capturar.sh a4-real    # um bloco qualquer (os *-real chamam o modelo: saem da cota)
set -uo pipefail
K=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$K/saidas"
alvos=("$@"); [ ${#alvos[@]} -eq 0 ] && alvos=($(cd "$K/blocos" && ls *.sh | grep -v -e '-real' -e 'a6-claude' | sed 's/\.sh$//'))
for b in "${alvos[@]}"; do
  ( cd /tmp && bash "$K/blocos/$b.sh" ) > "$K/saidas/$b.txt" 2>&1
  echo "$b: $(wc -l < "$K/saidas/$b.txt") linhas"
done
