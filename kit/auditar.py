#!/usr/bin/env python3
"""auditar.py: auditoria de segurança do seu loop, a partir do mapa (o mesmo JSON do triade.py com
um bloco "controles" por sessão). Imprime um item por sessão e controle, e grava o checklist.

  python3 auditar.py mapa.json                 # relatório no terminal
  python3 auditar.py mapa.json --md check.md   # também grava o checklist em Markdown, com a correção

Controles de cada sessão (todos opcionais; o que faltar conta como não feito):
  "motor": "claude" | "codex"
  "deny": [...]                regras deny do settings.json (Claude Code)
  "sandbox": "read-only" | "workspace-write" | "danger-full-access" | "nenhum"   (Codex -s, ou o seu)
  "hooks": ["guarda.py", ...]  hooks PreToolUse ligados
  "prova_isolamento": "AAAA-MM-DD OK"   saída do prova-isolamento.sh nesta máquina
  "rede": true | false         a sessão alcança a internet
  "porta": true                ações irreversíveis passam pela porta.py (humano aprova)
  "tetos": {"tempo": "2h", "memoria": "4G"}
Saída 0: tudo OK. Saída 1: algum item falhou. Saída 2: mapa inválido. Não chama modelo nem rede.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from triade import pernas  # noqa: E402

DENY_MINIMO = {"rm": "Bash(rm *)", "push": "Bash(git push *)", "rede": ("Bash(curl *)", "WebFetch"),
               "env": "Read(./.env)"}


def itens(s):
    c = s.get("controles", {})
    f = s.get("ferramentas", [])
    tem = lambda k: any(x.get(k) for x in f)
    humano = bool(s.get("humano"))
    p3 = pernas(s, "triade")
    p2 = pernas(s, "dois")
    out = []
    out.append(("tríade letal", humano or not all(p3.values()),
                "corte uma perna: leitor sem dados nem saída que devolve só campos (aula 1)"))
    out.append(("Regra de Dois", humano or not all(p2.values()),
                "no máximo 2 de A/B/C por sessão, ou nova sessão de contexto limpo, ou humano (aula 2)"))
    motor = c.get("motor")
    if motor == "claude":
        deny = set(c.get("deny", []))
        falta = [k for k, v in DENY_MINIMO.items()
                 if not (set(v) & deny if isinstance(v, tuple) else v in deny)]
        out.append(("permissões (deny mínimo)", not falta,
                    f"acrescente ao deny: {', '.join(falta)} (kit/permissoes/executar.json, aula 4)"))
        out.append(("hook de guarda", "guarda.py" in c.get("hooks", []) or not tem("muda_estado"),
                    "ligue a guarda.py em PreToolUse (aula 5)"))
    elif motor == "codex":
        out.append(("permissões (sandbox do Codex)", c.get("sandbox") in ("read-only", "workspace-write"),
                    "use -s read-only ou -s workspace-write; nunca --yolo no loop (aula 4)"))
    else:
        out.append(("permissões", False, 'diga o "motor" (claude ou codex) e as regras da sessão (aula 4)'))
    out.append(("isolamento provado", "OK" in str(c.get("prova_isolamento", "")),
                "rode o prova-isolamento.sh com o mesmo wrapper do loop e anote a data (aula 6)"))
    out.append(("rede x dados privados", not (tem("privado") and c.get("rede", True)),
                "sessão que lê dado privado roda sem rede (aula 6)"))
    out.append(("irreversível pede humano", humano or not tem("saida") or bool(c.get("porta")),
                "envio, push e apagar passam pela porta.py (aula 7)"))
    t = c.get("tetos", {})
    out.append(("tetos de tempo e memória", bool(t.get("tempo")) and bool(t.get("memoria")),
                "timeout + MemoryMax em cada ciclo (aula 7; curso 2, aula 6)"))
    return out


def main():
    a = sys.argv[1:]
    arqs = [x for x in a if x.endswith(".json")]
    if not arqs:
        print(__doc__.strip()); return 2
    try:
        mapa = json.load(open(arqs[0], encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"mapa inválido: {e}"); return 2
    linhas, ok, total = [], 0, 0
    for s in mapa.get("sessoes", []):
        print(f"## {s.get('nome', '?')}")
        linhas.append(f"## {s.get('nome', '?')}")
        for nome, passou, corr in itens(s):
            total += 1; ok += passou
            print(f"  {'OK   ' if passou else 'FALHA'} {nome}" + ("" if passou else f" → {corr}"))
            linhas.append(f"- [{'x' if passou else ' '}] {nome}" + ("" if passou else f": {corr}"))
    veredito = "APROVADA" if ok == total else "REPROVADA"
    print(f"AUDITORIA: {ok}/{total} itens OK — {veredito}")
    if "--md" in a:
        destino = a[a.index("--md") + 1]
        cab = f"# Checklist de segurança: {mapa.get('loop', '?')}\n\nResultado: {ok}/{total} itens OK — {veredito}\n\n"
        Path(destino).write_text(cab + "\n".join(linhas) + "\n", encoding="utf-8")
        print(f"checklist gravado em {destino}")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
