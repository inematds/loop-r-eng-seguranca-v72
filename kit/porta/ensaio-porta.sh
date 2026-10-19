#!/usr/bin/env bash
# ensaio-porta.sh — o caminho inteiro da porta, sem modelo: pedir, tentar executar sem aprovação,
# aprovar sem terminal, aprovar "como humano" (o script finge digitar num pseudo-terminal), adulterar
# depois de aprovado, aprovar de novo, executar e tentar reusar a aprovação.
set -uo pipefail
K=$(cd "$(dirname "$0")" && pwd)
export PORTA_DIR=/tmp/ensaio-seg/porta
rm -rf "$PORTA_DIR" /tmp/ensaio-seg/msg.txt; mkdir -p /tmp/ensaio-seg
P="python3 $K/porta.py"
humano() { script -qec "$P aprovar $1" /dev/null <<< "$1" | grep -oE '(APROVADO|RECUSADO).*' | tr -d '\r'; }
echo "Olá, o pedido 1042 saiu hoje." > /tmp/ensaio-seg/msg.txt
linha=$($P pedir enviar-email cliente@exemplo.invalid /tmp/ensaio-seg/msg.txt); echo "$linha"
ID=$(echo "$linha" | cut -d' ' -f2 | tr -d ':')
$P executar "$ID"; echo "saída: $?"
echo "$ID" | $P aprovar "$ID"; echo "saída: $?"
humano "$ID"
sed -i 's/1042/1042 e o cadastro completo segue anexo/' "$PORTA_DIR/pedidos/$ID.json"   # alguém mexe depois
$P executar "$ID"; echo "saída: $?"
ID2=$($P pedir enviar-email cliente@exemplo.invalid /tmp/ensaio-seg/msg.txt 2>&1 | cut -d' ' -f2 | tr -d ':')
humano "$ID2"
$P executar "$ID2"; echo "saída: $?"
$P executar "$ID2"; echo "saída: $?"
wc -l < "$PORTA_DIR/saida.log"
