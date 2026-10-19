#!/usr/bin/env python3
"""regra.py: mostra que regra de um settings.json do Claude Code decide um comando Bash.

  python3 regra.py settings.json "cd /tmp && rm -rf build"

Imita, de forma SIMPLIFICADA, o que a doc oficial descreve (code.claude.com/docs/en/permissions, lida em
19/10/2026): ordem fixa deny → ask → allow; o comando é partido em &&, ||, ;, |, & e quebra de linha, e
o conteúdo de $( … ) também conta; deny e ask valem se QUALQUER subcomando casar; allow só aprova se
TODOS casarem; "Bash(x *)" casa "x" e "x …"; regra sem * casa só o texto exato; "Bash" sozinho casa tudo.
Não cobre tudo (wrappers, find, redirecionamentos, modos): quem decide de verdade é o Claude Code.
Saída: 0 allow · 1 deny · 3 ask · 4 sem regra (pergunta no terminal; recusa com --permission-mode dontAsk).
"""
import json
import re
import sys

SEP = re.compile(r"&&|\|\||;|\|&|\||&|\n")


def subcomandos(cmd):
    partes = [cmd]
    partes += re.findall(r"\$\(([^()]*)\)", cmd)          # $( … ) também é comando
    out = []
    for p in partes:
        p = re.sub(r"\$\([^()]*\)", "", p)
        out += [s.strip() for s in SEP.split(p) if s.strip()]
    return out


def casa(regra, sub):
    if regra == "Bash":
        return True
    m = re.fullmatch(r"Bash\((.*)\)", regra)
    if not m:
        return False
    pad = m.group(1)
    if pad.endswith(" *") and pad.count("*") == 1:
        base = pad[:-2]
        return sub == base or sub.startswith(base + " ")
    rx = "^" + ".*".join(re.escape(x) for x in pad.split("*")) + "$"
    return re.match(rx, sub, re.S) is not None


def decidir(perm, cmd):
    subs = subcomandos(cmd)
    for tipo in ("deny", "ask"):
        for r in perm.get(tipo, []):
            for s in subs:
                if casa(r, s):
                    return tipo, r, s
    allow = perm.get("allow", [])
    if subs and all(any(casa(r, s) for r in allow) for s in subs):
        return "allow", next(r for r in allow if casa(r, subs[0])), subs[0]
    return "sem regra", "-", " · ".join(subs)


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip()); return 2
    perm = json.load(open(sys.argv[1], encoding="utf-8")).get("permissions", {})
    tipo, regra, sub = decidir(perm, sys.argv[2])
    print(f"{tipo:<9} {regra:<22} ← {sub}")
    return {"allow": 0, "deny": 1, "ask": 3}.get(tipo, 4)


if __name__ == "__main__":
    sys.exit(main())
