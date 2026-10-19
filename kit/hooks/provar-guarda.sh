#!/usr/bin/env bash
# provar-guarda.sh — manda chamadas de ferramenta FALSAS para os hooks, como o Claude Code faria,
# e imprime a decisão de cada um. Não chama modelo. Usa a guarda.py deste kit e, se existir,
# o raio.mjs e o colisao.mjs do inema-agent-runtime (RUNTIME=caminho do clone).
set -uo pipefail
K=$(cd "$(dirname "$0")" && pwd)
R=${RUNTIME:-$HOME/projetos/inema-agent-runtime}/runtime/mods/runtime-guarda/hooks
P=/tmp/ensaio-seg/hooks
rm -rf "$P" && mkdir -p "$P/tests" "$P/build" && cd "$P"
echo a > build/a.o; echo b > build/b.o; echo "def test_x(): pass" > tests/test_x.py
decisao() { grep -o '"permissionDecision": *"[a-z]*"' | grep -o '[a-z]*"$' | tr -d '"' || true; }
caso() { # caso <hook> <rótulo> <json>
  local d; d=$(printf '%s' "$3" | $1 | decisao); printf '%-34s → %s\n' "$2" "${d:--}"; }
bash_json() { printf '{"cwd":"%s","session_id":"s1","tool_name":"Bash","tool_input":{"command":"%s"}}' "$P" "$1"; }
edit_json() { printf '{"cwd":"%s","session_id":"%s","tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$P" "$2" "$1"; }
G="python3 $K/guarda.py"
echo "## guarda.py (nega o irreversível)"
caso "$G" "git push --force origin main" "$(bash_json 'git push --force origin main')"
caso "$G" "git reset --hard HEAD~3"      "$(bash_json 'git reset --hard HEAD~3')"
caso "$G" "find . -name '*.o' -delete"   "$(bash_json "find . -name '*.o' -delete")"
caso "$G" "rm -rf ~"                     "$(bash_json 'rm -rf ~')"
caso "$G" "pkill -f servidor"            "$(bash_json 'pkill -f servidor')"
caso "$G" "python3 -m pytest -q"         "$(bash_json 'python3 -m pytest -q')"
caso "$G" "Edit tests/test_x.py"         "$(edit_json tests/test_x.py s1)"
caso "$G" "Edit src/app.py"              "$(edit_json src/app.py s1)"
if [ -f "$R/raio.mjs" ]; then
  echo "## raio.mjs (apagar pede confirmação, com a contagem)"
  caso "node $R/raio.mjs" "rm -r build"   "$(bash_json 'rm -r build')"
  caso "node $R/raio.mjs" "rm -r nada"    "$(bash_json 'rm -r nada')"
  echo "## colisao.mjs (outra sessão editou há pouco)"
  export INEMA_RUNTIME_ESTADO=$P/.estado
  printf '%s' "$(edit_json tests/test_x.py sessao-A)" | node "$R/colisao.mjs" pos
  caso "node $R/colisao.mjs pre" "sessão B edita o mesmo arquivo" "$(edit_json tests/test_x.py sessao-B)"
  caso "node $R/colisao.mjs pre" "sessão A edita de novo"          "$(edit_json tests/test_x.py sessao-A)"
else
  echo "(sem $R: clone https://github.com/inematds/inema-agent-runtime para ver raio e colisão)"
fi
