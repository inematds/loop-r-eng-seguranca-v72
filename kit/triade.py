#!/usr/bin/env python3
"""triade.py: confere o mapa do seu loop contra a tríade letal e a Regra de Dois.

O mapa é um JSON com as sessões do loop e, em cada uma, as ferramentas que ela enxerga.
Cada ferramenta marca o que faz:
  "privado": true      devolve dado que não é público (repo privado, .env, banco, e-mail)
  "terceiros": true    devolve texto que alguém de fora pode ter escrito (issue, página, e-mail recebido)
  "saida": true        manda algo para fora, para um destino que o modelo pode escolher
  "muda_estado": true  muda alguma coisa (arquivo, banco, git, planilha), mesmo sem sair da máquina
Sessão com "humano": true = toda ação passa por aprovação humana (vira SUPERVISIONADA, não reprova).

  python3 triade.py mapa.json              # tríade letal (Simon Willison): privado + terceiros + saída
  python3 triade.py mapa.json --regra dois # Regra de Dois (Meta): no máximo 2 de [A] [B] [C]

Saída 0: nenhuma sessão autônoma com as três. Saída 1: alguma fecha. Saída 2: mapa inválido.
Não chama modelo nem rede: só lê o JSON. Quem garante que o mapa é verdadeiro é você.
"""
import json
import sys


def pernas(sessao, regra):
    f = sessao.get("ferramentas", [])
    tem = lambda k: any(x.get(k) for x in f)
    if regra == "dois":
        return {"A terceiros": tem("terceiros"), "B privado": tem("privado"),
                "C muda/sai": tem("saida") or tem("muda_estado")}
    return {"privado": tem("privado"), "terceiros": tem("terceiros"), "saída": tem("saida")}


def avaliar(mapa, regra):
    """Devolve [(nome, pernas, veredito)] com veredito OK, FECHA ou SUPERVISIONADA."""
    out = []
    for s in mapa.get("sessoes", []):
        p = pernas(s, regra)
        if all(p.values()):
            v = "SUPERVISIONADA" if s.get("humano") else "FECHA"
        else:
            v = "OK"
        out.append((s.get("nome", "?"), p, v))
    return out


def main():
    args = sys.argv[1:]
    regra = "dois" if "--regra" in args and args[args.index("--regra") + 1] == "dois" else "triade"
    arqs = [a for a in args if a.endswith(".json")]
    if not arqs:
        print(__doc__.strip().splitlines()[0]); print("uso: triade.py mapa.json [--regra dois]")
        return 2
    try:
        mapa = json.load(open(arqs[0], encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"mapa inválido: {e}"); return 2
    nome_regra = "REGRA DE DOIS" if regra == "dois" else "TRÍADE"
    res = avaliar(mapa, regra)
    for nome, p, v in res:
        marcas = "  ".join(f"{k}:{'sim' if b else 'não'}" for k, b in p.items())
        print(f"{nome:<12} {marcas}  → {v}")
    fecham = [n for n, _, v in res if v == "FECHA"]
    sup = [n for n, _, v in res if v == "SUPERVISIONADA"]
    if sup:
        print(f"aviso: {', '.join(sup)} tem as três, mas com humano aprovando cada ação")
    if fecham:
        print(f"{nome_regra}: violada em {', '.join(fecham)}")
        return 1
    print(f"{nome_regra}: nenhuma sessão autônoma com as três ({len(res)} {'sessão' if len(res) == 1 else 'sessões'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
