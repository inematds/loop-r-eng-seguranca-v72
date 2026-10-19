K=~/projetos/loop-r-eng-seguranca-v72/kit
python3 $K/triade.py $K/mapas/corretor.json; echo "saída: $?"
for m in corretor corretor-dois; do
  echo "## $m (Regra de Dois)"; python3 $K/triade.py $K/mapas/$m.json --regra dois; echo "saída: $?"
done
