#!/usr/bin/env python3
"""porta.py: a ação irreversível passa por uma porta que só o humano abre.

O agente PEDE (grava o pedido com o conteúdo exato). O humano APROVA num terminal de verdade, vendo
destino e conteúdo; a aprovação guarda o hash do conteúdo. Só então EXECUTAR roda, e recusa se o
conteúdo mudou depois da aprovação. Os pedidos e as aprovações ficam em PORTA_DIR, que deve estar FORA
da pasta que o agente pode escrever (no sandbox do Codex workspace-write, fora do workspace).

  python3 porta.py pedir ACAO DESTINO ARQUIVO   # agente: imprime o id do pedido
  python3 porta.py ver ID                       # qualquer um: mostra o pedido
  python3 porta.py aprovar ID                   # humano: exige terminal (tty) e digitar o id
  python3 porta.py executar ID                  # loop: só roda com aprovação válida

A "execução" deste ensaio só acrescenta uma linha em PORTA_DIR/saida.log (troque pelo seu envio real).
Saída 0 ok · 1 recusado · 2 uso errado.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

D = Path(os.environ.get("PORTA_DIR", "/tmp/ensaio-seg/porta"))


def h(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def carregar(i):
    p = D / "pedidos" / f"{i}.json"
    if not p.exists():
        print(f"RECUSADO: pedido {i} não existe"); sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8")), p


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__.strip()); return 2
    (D / "pedidos").mkdir(parents=True, exist_ok=True)
    (D / "aprovados").mkdir(parents=True, exist_ok=True)
    if a[0] == "pedir" and len(a) == 4:
        conteudo = Path(a[3]).read_text(encoding="utf-8")
        i = time.strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(2).hex()
        (D / "pedidos" / f"{i}.json").write_text(json.dumps(
            {"id": i, "acao": a[1], "destino": a[2], "conteudo": conteudo}, ensure_ascii=False), encoding="utf-8")
        print(f"pedido {i}: {a[1]} → {a[2]} ({len(conteudo)} caracteres). Aguardando aprovação humana.")
        return 0
    if a[0] in ("ver", "aprovar", "executar") and len(a) == 2:
        ped, _ = carregar(a[1])
        if a[0] == "ver":
            print(f"{ped['acao']} → {ped['destino']}\n---\n{ped['conteudo']}---"); return 0
        if a[0] == "aprovar":
            if not sys.stdin.isatty():
                print("RECUSADO: aprovar exige um terminal humano (stdin não é tty)"); return 1
            print(f"{ped['acao']} → {ped['destino']}\n---\n{ped['conteudo']}---")
            if input("Digite o id para aprovar: ").strip() != ped["id"]:
                print("RECUSADO: id não confere"); return 1
            (D / "aprovados" / ped["id"]).write_text(h(ped["conteudo"]), encoding="utf-8")
            print(f"APROVADO {ped['id']} (hash {h(ped['conteudo'])})"); return 0
        apr = D / "aprovados" / ped["id"]
        if not apr.exists():
            print(f"RECUSADO: {ped['id']} sem aprovação humana"); return 1
        if apr.read_text(encoding="utf-8").strip() != h(ped["conteudo"]):
            print(f"RECUSADO: o conteúdo de {ped['id']} mudou depois da aprovação"); return 1
        with open(D / "saida.log", "a", encoding="utf-8") as f:
            f.write(f"{ped['acao']} {ped['destino']} {h(ped['conteudo'])}\n")
        apr.unlink()  # aprovação vale uma vez
        print(f"EXECUTADO {ped['id']}: {ped['acao']} → {ped['destino']}"); return 0
    print(__doc__.strip()); return 2


if __name__ == "__main__":
    sys.exit(main())
