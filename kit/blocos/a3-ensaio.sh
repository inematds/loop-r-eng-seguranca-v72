K=~/projetos/loop-r-eng-seguranca-v72/kit/injecao
for modo in ingenuo sem-saida separado; do
  bash $K/ensaio-injecao.sh > /dev/null
  echo "## $modo"; python3 $K/agente-falso.py $modo /tmp/ensaio-seg/inj
  python3 $K/canario.py /tmp/ensaio-seg/inj; echo "saída: $?"
done
