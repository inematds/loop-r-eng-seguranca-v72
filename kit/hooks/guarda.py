#!/usr/bin/env python3
"""guarda.py: hook PreToolUse do Claude Code que NEGA o irreversível e protege os arquivos do juiz.

Lê do stdin o JSON que o Claude Code manda antes de cada ferramenta (tool_name, tool_input, cwd).
  Bash  → nega push forçado, reset --hard, git clean -f, checkout -- ., git restore (da árvore),
          find -delete, rm recursivo em / ~ $HOME ou .. (com ou sem aspas, também dentro de bash -c),
          pkill / killall como comando, dd of= e mkfs.
          E nega ESCRITA via Bash nos protegidos: > e >>, tee, sed -i, cp/install/ln (destino),
          mv/rm/truncate/shred/unlink (qualquer argumento).
  Edit / Write / MultiEdit / NotebookEdit → nega se o arquivo está em GUARDA_PROTEGIDOS
          (padrão: goal.md tests/ .claude/ e a própria pasta do hook).
Responde {"hookSpecificOutput": {"permissionDecision": "deny", ...}} ou não imprime nada.

O que ela NÃO pega (é regex e leitura de comando, não sandbox): um programa que grava por conta própria
(python3 -c "open('goal.md','w')", node -e, perl -e, um script seu), caminho montado em variável,
eval, base64 | sh. Para isso servem o deny Edit(...)/Write(...) da aula 4 e o sandbox da aula 6.
Para o "apagar com confirmação" (ask com a contagem do que some), use o raio.mjs do inema-agent-runtime.
Testar sem Claude: printf '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | python3 guarda.py
"""
import json
import os
import re
import shlex
import sys

INICIO = r"(?:^|[;&|(`'\"]\s*|\bsudo\s+|\bxargs\s+)"   # começo de comando (também dentro de bash -c '…')
NEGAR_BASH = [
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b)", "push forçado reescreve o remoto"),
    (r"\bgit\s+reset\s+.*--hard\b", "reset --hard descarta trabalho não commitado"),
    (r"\bgit\s+clean\s+-\w*f", "git clean -f apaga arquivos não rastreados"),
    (r"\bgit\s+checkout\s+--\s+\.", "checkout -- . descarta mudanças não commitadas"),
    (r"\bfind\b.*\s-delete\b", "find -delete apaga sem lista prévia"),
    (r"\brm\s+(-\w*\s+)*-\w*[rR]\w*\s+(-\w+\s+)*['\"]?(/|~|\$HOME|\$\{HOME\}|\.\.)(?=$|[\s'\"`;&|)]|/(?:\*|$|[\s'\"`;&|)]))",
     "rm recursivo na raiz, no HOME ou acima da pasta"),
    (INICIO + r"(pkill|killall)\b", "matar por nome pode derrubar processo que não é seu"),
    (r"\bdd\b.*\bof=", "dd escreve direto no destino"),
    (r"\bmkfs(\.\w+)?\b", "mkfs formata um disco"),
]
DESTINO_ULTIMO = {"cp", "install", "ln"}                   # escreve no último argumento
TODOS_ARGS = {"mv", "rm", "truncate", "shred", "unlink"}   # mexe em qualquer argumento
SEPARA = {";", "&&", "||", "|", "&", "\n", "(", ")"}


def protegidos(cwd):
    padrao = os.environ.get("GUARDA_PROTEGIDOS", "goal.md tests/ .claude/")
    itens = padrao.split()
    itens.append(os.path.dirname(os.path.abspath(__file__)) + "/")
    return [os.path.normpath(i if os.path.isabs(i) else os.path.join(cwd, i)) for i in itens]


def protegido(alvo, cwd):
    if not alvo or alvo.startswith("-"):
        return False
    alvo = alvo.replace("${HOME}", "~").replace("$HOME", "~").replace("${PWD}", cwd).replace("$PWD", cwd)
    caminho = os.path.normpath(os.path.join(cwd, os.path.expanduser(alvo)))
    return any(caminho == p or caminho.startswith(p + "/") for p in protegidos(cwd))


def git_restore(seg):
    """git restore descarta mudança da árvore; só --staged (sem --worktree/-W) mexe apenas no índice."""
    if seg[:2] != ["git", "restore"]:
        return False
    return "--staged" not in seg or "--worktree" in seg or "-W" in seg


def segmentos(cmd):
    """Divide o comando em comandos simples (listas de palavras), abrindo bash -c / sh -c '…'."""
    try:
        lx = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()<>")
        lx.whitespace_split = True
        toks = list(lx)
    except ValueError:
        toks = cmd.split()
    seg = []
    for t in toks + [";"]:
        if t in SEPARA or set(t) <= set(";&|()") and t:
            if seg:
                yield seg
                if len(seg) >= 3 and os.path.basename(seg[0]) in ("bash", "sh", "zsh") and seg[1] == "-c":
                    yield from segmentos(seg[2])
            seg = []
        else:
            seg.append(t)


def escreve_protegido(cmd, cwd):
    for seg in segmentos(cmd):
        if git_restore(seg):
            return "git restore descarta mudanças não commitadas"
        alvos = [seg[i + 1] for i, t in enumerate(seg[:-1]) if re.fullmatch(r"\d?(>|>>|>\||&>|&>>)", t)]
        palavras = [t for t in seg if not re.fullmatch(r"\d?[<>&|]+\d?", t)]
        while palavras and (palavras[0] == "sudo" or re.fullmatch(r"\w+=\S*", palavras[0])):
            palavras = palavras[1:]
        nome = os.path.basename(palavras[0]) if palavras else ""
        args = palavras[1:]
        if nome == "tee" or (nome == "sed" and any(a.startswith("-i") or a.startswith("--in-place") for a in args)):
            alvos += args
        elif nome in DESTINO_ULTIMO and args:
            alvos.append(args[-1])
        elif nome in TODOS_ARGS:
            alvos += args
        for a in alvos:
            if protegido(a, cwd):
                return f"{a} é protegido (juiz, objetivo ou a própria guarda); escrita via Bash também conta"
    return None


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
        motivo = escreve_protegido(cmd, cwd)
        if motivo:
            return negar(motivo)
        return 0
    if ferramenta in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or ""
        if protegido(alvo, cwd):
            return negar(f"{alvo} é protegido (juiz, objetivo ou a própria guarda)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
