#!/usr/bin/env python3
"""guarda.py: hook PreToolUse do Claude Code que NEGA o irreversível e protege os arquivos do juiz.

Lê do stdin o JSON que o Claude Code manda antes de cada ferramenta (tool_name, tool_input, cwd).
  Bash  → nega push forçado, reset --hard, git clean -f, find -delete, rm recursivo em / ~ $HOME ou ..,
          pkill -f / killall, dd of= e mkfs. O resto segue o fluxo normal (sem decisão).
  Edit / Write / MultiEdit / NotebookEdit → nega se o arquivo está em GUARDA_PROTEGIDOS
          (padrão: goal.md tests/ .claude/ e a própria pasta do hook).
Responde {"hookSpecificOutput": {"permissionDecision": "deny", ...}} ou não imprime nada.
Para o "apagar com confirmação" (ask com a contagem do que some), use o raio.mjs do inema-agent-runtime.
Testar sem Claude: printf '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | python3 guarda.py
"""
import json
import os
import re
import sys

NEGAR_BASH = [
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b)", "push forçado reescreve o remoto"),
    (r"\bgit\s+reset\s+.*--hard\b", "reset --hard descarta trabalho não commitado"),
    (r"\bgit\s+clean\s+-\w*f", "git clean -f apaga arquivos não rastreados"),
    (r"\bgit\s+checkout\s+--\s+\.", "checkout -- . descarta mudanças não commitadas"),
    (r"\bfind\b.*\s-delete\b", "find -delete apaga sem lista prévia"),
    (r"\brm\s+(-\w*\s+)*-\w*[rR]\w*\s+(-\w+\s+)*(/|~|\$HOME|\.\.)(\s|/?$|/\*)", "rm recursivo na raiz, no HOME ou acima da pasta"),
    (r"\b(pkill|killall)\b", "matar por nome pode derrubar processo que não é seu"),
    (r"\bdd\b.*\bof=", "dd escreve direto no destino"),
    (r"\bmkfs(\.\w+)?\b", "mkfs formata um disco"),
]


def protegidos(cwd):
    padrao = os.environ.get("GUARDA_PROTEGIDOS", "goal.md tests/ .claude/")
    itens = padrao.split()
    itens.append(os.path.dirname(os.path.abspath(__file__)) + "/")
    return [i if os.path.isabs(i) else os.path.join(cwd, i) for i in itens]


def negar(motivo):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"Guarda: {motivo}. Peça ao humano; não tente outro caminho para o mesmo efeito.",
    }}, ensure_ascii=False))
    return 0


def main():
    try:
        e = json.load(sys.stdin)
    except ValueError:
        return 0
    ferramenta = e.get("tool_name", "")
    entrada = e.get("tool_input") or {}
    cwd = e.get("cwd") or os.getcwd()
    if ferramenta == "Bash":
        cmd = entrada.get("command", "")
        for rx, motivo in NEGAR_BASH:
            if re.search(rx, cmd):
                return negar(motivo)
        return 0
    if ferramenta in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or ""
        caminho = os.path.normpath(os.path.join(cwd, alvo))
        for p in protegidos(cwd):
            p = os.path.normpath(p)
            if caminho == p or caminho.startswith(p.rstrip("/") + "/"):
                return negar(f"{alvo} é protegido (juiz, objetivo ou a própria guarda)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
