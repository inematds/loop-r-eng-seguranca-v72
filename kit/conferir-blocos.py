#!/usr/bin/env python3
"""conferir-blocos.py: confere que cada bloco copiável das aulas é idêntico ao arquivo testado no kit.

  python3 kit/conferir-blocos.py [conteudo/pt/aulas]

Bloco "Terminal · …"  → tem de ser igual a algum kit/blocos/*.sh (o que o capturar.sh roda).
Bloco "Arquivo · kit/X" → tem de ser igual a kit/X.
Saída 0: tudo igual. Saída 1: algum bloco divergiu do que foi testado.
"""
import json
import sys
from pathlib import Path

K = Path(__file__).resolve().parent
pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else K.parent / "conteudo/pt/aulas"
blocos = {p.read_text(encoding="utf-8").rstrip("\n"): p.name for p in (K / "blocos").glob("*.sh")}
ruins = total = 0
for aula in sorted(pasta.glob("*.json")):
    for s in json.loads(aula.read_text(encoding="utf-8"))["secoes"]:
        for b in s.get("blocos", []):
            rot, c = b["rot"], b["conteudo"].rstrip("\n")
            if rot.startswith("Terminal"):
                total += 1
                ok = c in blocos
                ref = blocos.get(c, "nenhum kit/blocos/*.sh igual")
            elif rot.startswith("Arquivo · kit/"):
                total += 1
                arq = K / rot.split("Arquivo · kit/")[1].split(" ")[0]
                ok = arq.exists() and arq.read_text(encoding="utf-8").rstrip("\n") == c
                ref = arq.name
            else:
                continue
            if not ok:
                ruins += 1
                print(f"DIVERGE  {aula.name} · {rot} → {ref}")
print(f"BLOCOS: {total - ruins}/{total} iguais ao kit testado")
sys.exit(1 if ruins else 0)
