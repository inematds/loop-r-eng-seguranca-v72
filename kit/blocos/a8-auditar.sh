K=~/projetos/loop-r-eng-seguranca-v72/kit
python3 $K/auditar.py $K/mapas/meu-loop.json --md /tmp/ensaio-seg/checklist.md; echo "saída: $?"
python3 $K/auditar.py $K/mapas/meu-loop-seguro.json | tail -1; echo "saída: $?"
