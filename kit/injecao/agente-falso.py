#!/usr/bin/env python3
"""agente-falso.py: imita o PIOR caso de um agente que lê conteúdo não confiável.

Não é um modelo. É um script que obedece a qualquer frase "Instrução para o agente: ..." que achar no
texto, como um modelo enganado faria. Serve para ensaiar as defesas sem gastar cota e sem atacar ninguém:
o "canal de saída" é só um arquivo local (saida/enviados.log) e a "resposta" é resposta.md.

  python3 agente-falso.py ingenuo   PASTA   # lê segredo + página inteira, tem a ferramenta enviar
  python3 agente-falso.py sem-saida PASTA   # igual, mas a sessão não tem a ferramenta enviar
  python3 agente-falso.py separado  PASTA   # um leitor por código extrai só campos; o agente vê só os campos

PASTA vem do ensaio-injecao.sh: segredo.txt, pagina.html, saida/.
"""
import html
import json
import re
import sys
from pathlib import Path

INSTR = re.compile(r"Instrução para o agente:\s*(.+?)(?:</|$)", re.S)


def texto_visivel_e_oculto(pagina):
    # o agente ingênuo recebe TUDO: texto escondido por CSS também é texto
    return html.unescape(re.sub(r"\s+", " ", pagina))


def obedecer(contexto, segredo, ferramentas, pasta, resposta):
    for ordem in INSTR.findall(contexto):
        ordem = ordem.strip()
        print(f"achou instrução no conteúdo: \"{ordem[:60]}…\"")
        if "envie" in ordem:
            if "enviar" in ferramentas:
                with open(pasta / "saida" / "enviados.log", "a", encoding="utf-8") as f:
                    f.write(segredo + "\n")
                print("  → chamou enviar(segredo) para o canal de saída")
            else:
                print("  → tentou enviar: ferramenta enviar não existe nesta sessão")
        if "imagem" in ordem:
            url = re.search(r"!\[\]\((\S+?)\)", ordem)
            if url:
                resposta.append("![](" + url.group(1).replace("CONTEUDO_DO_SEGREDO", segredo) + ")")
                print("  → pôs na resposta uma imagem markdown com o segredo na URL")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("ingenuo", "sem-saida", "separado"):
        print(__doc__.strip()); return 2
    modo, pasta = sys.argv[1], Path(sys.argv[2])
    segredo = (pasta / "segredo.txt").read_text(encoding="utf-8").strip()
    pagina = (pasta / "pagina.html").read_text(encoding="utf-8")
    resposta = []
    if modo == "separado":
        # leitor determinístico (sem modelo): só título e preço, por expressão regular
        titulo = re.search(r"<h1>(.*?)</h1>", pagina, re.S)
        preco = re.search(r'class="preco">Preço:\s*([^<]+)<', pagina)
        campos = {"titulo": titulo.group(1).strip() if titulo else None,
                  "preco": preco.group(1).strip() if preco else None}
        (pasta / "campos.json").write_text(json.dumps(campos, ensure_ascii=False), encoding="utf-8")
        print(f"leitor gravou campos.json: {json.dumps(campos, ensure_ascii=False)}")
        # o agente com o segredo e a ferramenta enviar só vê os campos
        contexto = segredo + "\n" + json.dumps(campos, ensure_ascii=False)
        obedecer(contexto, segredo, {"enviar"}, pasta, resposta)
        resposta.insert(0, f"{campos['titulo']} por {campos['preco']}.")
    else:
        ferramentas = {"enviar"} if modo == "ingenuo" else set()
        contexto = segredo + "\n" + texto_visivel_e_oculto(pagina)
        obedecer(contexto, segredo, ferramentas, pasta, resposta)
        resposta.insert(0, "Fonte de bancada FB-30 por R$ 489,00.")
    (pasta / "resposta.md").write_text("\n".join(resposta) + "\n", encoding="utf-8")
    print(f"resposta.md: {len(resposta)} linha(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
