# PLANO — Segurança do Loop Autônomo (Formação LOOP-R Engenharia, curso 4 de 6) · 19/10/2026

Curso sem kit externo: o kit é a pasta `kit/` deste repo (python3, bash, node só para os hooks do inema-agent-runtime). Cada prática tem **ensaio sem custo** (agente falso, chamadas de ferramenta falsas, sondas locais) e, em três aulas, um passo **real** com `claude -p` pela assinatura (uma chamada cada). O "pronto quando" do passo real confere o disco ou o código de saída, nunca o texto do modelo.
Saídas com selo "real": capturadas em 19/10/2026 nesta máquina (Claude Code 2.1.303, codex-cli 0.163.0, systemd 255, Python 3.12, Ubuntu com `kernel.apparmor_restrict_unprivileged_userns=1`), por `kit/capturar.sh` a partir de `kit/blocos/*.sh`; `kit/conferir-blocos.py` confere que cada bloco "Terminal" do JSON é idêntico ao arquivo testado.

Fontes: pesquisa §4 (Willison, lethal trifecta, 16/06/2025; Meta, Agents Rule of Two; OWASP agêntico via Help Net Security 11/06/2026; sandbox pode falhar, Help Net Security + LangChain), doc oficial do Claude Code lida em 19/10/2026 (permissions, hooks, sandboxing), doc do Codex CLI (`codex exec -s`, `codex sandbox`, aviso do `--yolo`), `triade-letal` (CHECKLIST, inventario.py), `inema-agent-runtime/runtime` (CAPACIDADES, POLITICA, R1, R5, R7, `raio.mjs`, `colisao.mjs`, `.claude/settings.json`), `constituicao-agentes/modelo` (níveis de autonomia), `execucao-longa/tools/loop-longrun.sh` (já usa `-s workspace-write`), lições reais de `wifi/LESSONS.md` e a política de ação irreversível do CLAUDE.md global (anonimizada).
O que a pesquisa marca [2ª]/[incerto] não entra como fato: estatísticas "98% dos agentes", datas de Routines, detalhes das falhas do Cursor/Codex de 2026 (só "relatado").

Fora do escopo (dono em outro curso): escala de critério (curso 0); verificar e congelar testes (curso 1); loop-longrun.sh por dentro e units do vigia (curso 2, aula 6); worktrees, estratégia de colisão e filas entre sessões (curso 3, aulas 5 e 6); promoção e rollback de regras (curso 5). Aqui: sandbox = fronteira que o sistema operacional impõe; worktree = link para o curso 3.

Achados do ensaio (ensinados, não corrigidos nos repos de fonte):
1. `systemd-run --user -p PrivateNetwork=yes -p ProtectHome=read-only` roda **sem** as travas neste host (journal: "proceeding without"); a fuga passa. Os tetos (MemoryMax, timeout, RuntimeMaxSec) funcionam.
2. O sandbox do Claude Code não sobe sem `socat` no Linux; por padrão roda **sem** sandbox; com `failIfUnavailable: true` recusa iniciar (capturado).
3. `codex sandbox -P :read-only` / `:workspace` (perfis observados no 0.163.0) bloqueiam escrita fora e rede, mas deixam **ler** fora da pasta.
4. Num `claude -p` em `bypassPermissions`, o `deny` do settings e o `deny`/`ask` de hook PreToolUse barraram os comandos (o `ask` sem terminal não executou) — 1 rodada cada, 19/10/2026.
5. `RuntimeMaxSec=` não vale com `Type=oneshot` (systemd-analyze avisa): no modelo de unit, `TimeoutStartSec=`.

| # | slug | título | objetivo (≤160) | diagrama | prática → pronto quando |
|---|---|---|---|---|---|
| 1 | triade | A tríade letal: dados privados, conteúdo não confiável, saída para fora | mapear as sessões do seu loop nas três pernas da tríade letal e cortar uma perna onde as três se juntam. | dados privados + conteúdo de terceiros + saída → exfiltração; cortar uma perna | `triade.py triagem.json` → `TRÍADE: violada em triagem` (rc 1); cortada → `nenhuma sessão autônoma` (rc 0); inventario `--demo` |
| 2 | dois | Regra de Dois | aplicar a Regra de Dois: no máximo duas de [A] entrada não confiável, [B] dado sensível, [C] mudar estado ou sair, por sessão. | A, B, C → 2 de 3 / nova sessão / humano | `corretor.json` passa na tríade e reprova na Regra de Dois (rc 1); dividido → rc 0 com SUPERVISIONADA |
| 3 | injecao | Injeção pelo conteúdo que o agente lê | reproduzir com um agente falso a injeção por página envenenada e bloqueá-la separando quem lê de quem tem o segredo. | página (texto oculto) → agente → ferramenta / resposta → canário | ingênuo `VAZOU` (rc 1); sem-saida ainda `VAZOU: canário em resposta.md`; separado `canário ausente` (rc 0); real: linha do canário |
| 4 | permissoes | Permissões por etapa: capacidades e política | dar a cada etapa do loop só as permissões que ela usa, com deny no settings.json do Claude Code e -s no Codex. | planejar / executar / revisar → deny → ask → allow | `regra.py` mostra `rm -r -f` passando por `Bash(rm -rf *)` e barrado por `Bash(rm *)`; real: `build/app.bin continua lá` |
| 5 | hooks | Hooks como guarda: antes da ferramenta, contra apagar e colidir | ligar um hook PreToolUse que nega o irreversível, pede confirmação ao apagar e avisa colisão entre sessões. | chamada → hook (deny/ask/nada) → regras → ferramenta | `provar-guarda.sh` → 6 deny, 2 ask; real: `mudança não commitada preservada` + `continua lá` |
| 6 | sandbox | Sandbox de rede e de arquivos | provar na sua máquina que o sandbox bloqueia escrita fora da pasta e rede, em vez de confiar na flag. | wrapper → 4 sondas → BLOQUEADO/ABERTO → veredito | sem trava `FURADO` (rc 1); codex `:workspace` `OK` (rc 0); systemd `FURADO`; Claude sem socat recusa iniciar |
| 7 | irreversivel | Irreversível pede humano; rodar fora do terminal sem aumentar o raio | pôr envio, push e apagar atrás de uma porta que só o humano abre e rodar o loop no systemd com teto e sandbox. | agente pede → humano aprova (hash) → executa uma vez; systemd → teto → sandbox | porta: `RECUSADO` ×4 e `EXECUTADO` 1×; systemd + codex sandbox → `ISOLAMENTO: OK` |
| 8 | auditoria | Auditoria de segurança do seu loop | auditar o seu loop com o mapa das sessões, gerar o checklist do que falta e marcar a data da próxima revisão. | mapa → auditar.py → checklist → corrigir → reauditar | `meu-loop.json` → `0/8 — REPROVADA` (rc 1); `meu-loop-seguro.json` → `22/22 — APROVADA` (rc 0) (mapa + gerador) |

Simulação: `simconversa` na aula 3 (uma página pede ao agente para "confirmar o pedido no link"; o aluno decide o que o loop faz); `simfila` na aula 7 (fila de ações em que uma é irreversível e para na porta).
Vídeo: nenhum vídeo publicado é deste tema (AUDITORIA §c); sem vídeo.
Imagens: capa + inicio + 8 heroes pelo Codex (uma por vez, todas na 1ª tentativa), sem texto.
Próximo curso da ordem: curso 5, `https://inematds.github.io/loop-r-eng-aprende-v72/` (ainda não publicado em 19/10/2026).
