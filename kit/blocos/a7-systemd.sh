P=~/projetos/loop-r-eng-seguranca-v72/kit/prova-isolamento.sh
W=/tmp/ensaio-seg/iso; mkdir -p $W
echo "## teto de tempo: RuntimeMaxSec=3 num sleep 10"
systemd-run --user --wait --pipe --quiet -p RuntimeMaxSec=3 sleep 10; echo "saída: $?"
echo "## fora do terminal, com teto E sandbox do Codex dentro"
bash $P systemd-run --user --pipe --wait --quiet -p MemoryMax=1G -p RuntimeMaxSec=60 -- \
  codex sandbox -P :workspace -C $W --
echo "saída: $?"
