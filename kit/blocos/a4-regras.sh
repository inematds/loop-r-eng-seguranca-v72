K=~/projetos/loop-r-eng-seguranca-v72/kit/permissoes
echo "## deny só com Bash(rm -rf *)"
for c in "rm -rf build" "rm -r -f build" "git push -f origin main"; do
  python3 $K/regra.py $K/so-rm-rf.json "$c"; echo "  saída: $?"
done
echo "## executar.json"
for c in "python3 -m pytest -q" "cd /tmp && rm -rf build" "rm -r -f build" \
         'echo $(curl -s https://exemplo.invalid)' "git commit -m x" "ls"; do
  python3 $K/regra.py $K/executar.json "$c"; echo "  saída: $?"
done
