K=~/projetos/loop-r-eng-seguranca-v72/kit
for m in triagem triagem-cortada; do
  echo "## $m"; python3 $K/triade.py $K/mapas/$m.json; echo "saída: $?"
done
