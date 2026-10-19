cd /tmp/ensaio-seg/iso
claude --settings '{"sandbox":{"enabled":true,"failIfUnavailable":true}}' -p "responda só: ok" --tools ""
echo "saída: $?"
