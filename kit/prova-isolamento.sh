#!/usr/bin/env bash
# prova-isolamento.sh — tenta escapar e diz se a trava segurou. Não confie na flag: confie na prova.
# Uso: bash prova-isolamento.sh [--] [wrapper ...]
#   bash prova-isolamento.sh                                        # sem trava (tem de reprovar)
#   bash prova-isolamento.sh codex sandbox -P :workspace -C "$W" --  # dentro do sandbox do Codex
# Quatro tentativas, rodadas DENTRO do wrapper, a partir da pasta de trabalho W (padrão /tmp/ensaio-seg/iso):
#   escreve-dentro  cria um arquivo na pasta de trabalho        (o loop precisa: tem de funcionar)
#   escreve-fora    cria um arquivo no seu HOME                  (tem de ser BLOQUEADO)
#   rede            HTTP para example.com                        (tem de ser BLOQUEADO)
#   le-segredo      lê um segredo FALSO plantado em ~/.config    (só aviso: a maioria dos sandboxes deixa ler)
# Saída 0: escreve-fora e rede bloqueados. Saída 1: alguma fuga passou. Nada chama modelo.
set -uo pipefail
[ "${1:-}" = "--" ] && shift
W=${W:-/tmp/ensaio-seg/iso}
mkdir -p "$W" "$HOME/.config/prova-iso"
echo "SEGREDO-FALSO-$$" > "$HOME/.config/prova-iso/segredo"
fora="$HOME/.prova-iso-$$"
cd "$W"
sonda='r() { if eval "$2" >/dev/null 2>&1; then echo "$1 ABERTO"; else echo "$1 BLOQUEADO"; fi; }
r escreve-dentro "echo x > '"$W"'/dentro.txt"
r escreve-fora "echo x > '"$fora"'"
r rede "curl -s -m 5 -o /dev/null https://example.com"
r le-segredo "cat '"$HOME"'/.config/prova-iso/segredo"'
saida=$("$@" bash -c "$sonda" 2>/dev/null)
rm -f "$fora" "$W/dentro.txt"
echo "$saida" | sed 's/^/  /'
fugiu=$(echo "$saida" | grep -cE '^(escreve-fora|rede) ABERTO')
echo "$saida" | grep -q '^le-segredo ABERTO' && echo "  aviso: lê arquivos fora da pasta; tire segredos do alcance ou corte a rede"
echo "$saida" | grep -q '^escreve-dentro BLOQUEADO' && echo "  aviso: nem a pasta de trabalho é gravável (bom para revisar, não para executar)"
if [ "$fugiu" -gt 0 ]; then echo "ISOLAMENTO: FURADO ($fugiu fuga(s))"; exit 1; fi
echo "ISOLAMENTO: OK"
