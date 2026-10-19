[ -d ~/projetos/triade-letal ] || git clone -q https://github.com/inematds/triade-letal ~/projetos/triade-letal
cd ~/projetos/triade-letal
python3 inventario.py --demo                    # exemplo fictício, para ver o formato
python3 inventario.py --md /tmp/matriz.md > /dev/null && grep -c "|" /tmp/matriz.md
