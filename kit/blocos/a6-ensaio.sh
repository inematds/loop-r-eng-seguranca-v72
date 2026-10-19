P=~/projetos/loop-r-eng-seguranca-v72/kit/prova-isolamento.sh
W=/tmp/ensaio-seg/iso; mkdir -p $W
echo "## sem trava"; bash $P; echo "saída: $?"
echo "## codex sandbox :read-only"; bash $P codex sandbox -P :read-only -C $W --; echo "saída: $?"
echo "## codex sandbox :workspace"; bash $P codex sandbox -P :workspace -C $W --; echo "saída: $?"
echo "## systemd-run PrivateNetwork + ProtectHome"
bash $P systemd-run --user --pipe --wait --quiet -p PrivateNetwork=yes -p ProtectHome=read-only --
echo "saída: $?"
