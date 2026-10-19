# Segurança do Loop Autônomo — Formação LOOP-R Engenharia (curso 4 de 6)

Curso aberto e gratuito do INEMA.CLUB no formato INEMA Learning v7.2, em português, inglês e espanhol:
**https://inematds.github.io/loop-r-eng-seguranca-v72/** · [EN](https://inematds.github.io/loop-r-eng-seguranca-v72/en/) · [ES](https://inematds.github.io/loop-r-eng-seguranca-v72/es/)

Oito aulas para quem roda os próprios agentes (Claude Code ou Codex) em loop: tríade letal, Regra de Dois, injeção pelo conteúdo que o agente lê, permissões por etapa, hooks de guarda, sandbox provado na sua máquina, porta humana para o irreversível e auditoria do loop. Tom defensivo: nada aqui ataca sistemas de terceiros; as demonstrações são locais, com agente falso.

## O kit (`kit/`)

Python 3 e bash; node só para os hooks do [inema-agent-runtime](https://github.com/inematds/inema-agent-runtime). Todo ensaio roda sem chamar modelo. Três passos reais (`*/real.sh`) fazem uma chamada `claude -p` cada, pela sua assinatura.

| arquivo | aula | o que faz |
|---|---|---|
| `triade.py`, `mapas/` | 1, 2 | confere o mapa das sessões contra a tríade letal e a Regra de Dois |
| `injecao/` | 3 | página envenenada, agente falso (ingenuo, sem-saida, separado), canário |
| `permissoes/` | 4 | settings.json por etapa e `regra.py` (que regra decide um comando) |
| `hooks/` | 5 | `guarda.py` (PreToolUse que nega o irreversível), `provar-guarda.sh`, `settings-exemplo.json` |
| `prova-isolamento.sh` | 6, 7 | quatro tentativas de fuga dentro de um wrapper e um veredito |
| `porta/`, `systemd/` | 7 | porta do irreversível (pedir, aprovar com hash, executar uma vez) e modelo de unit |
| `auditar.py` | 8 | auditoria do mapa e checklist em Markdown |
| `blocos/`, `saidas/`, `capturar.sh`, `conferir-blocos.py` | — | os comandos das aulas, as saídas capturadas em 19/10/2026 e a conferência de que o site mostra o que foi testado |

```bash
git clone https://github.com/inematds/loop-r-eng-seguranca-v72 ~/projetos/loop-r-eng-seguranca-v72
K=~/projetos/loop-r-eng-seguranca-v72/kit && python3 $K/triade.py $K/mapas/triagem.json
```

## Gerar o site

Conteúdo em `conteudo/<idioma>/` (JSON). O HTML é gerado: `python3 gerar.py && python3 validar.py --links` (e `--lang en|es`). Não edite o HTML à mão.

[INEMA.CLUB](https://inema.club) · conteúdo aberto e gratuito
