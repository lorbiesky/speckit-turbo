# Configuração de qualidade

O arquivo opcional `.specify/extensions/turbo/turbo-config.yml` pertence somente à extensão Turbo. Comece pelo template instalado e ajuste a política por projeto.

```yaml
tdd:
  enabled: true
  allow_exception: true
  require_human_approval_for_exception: true

checkpoints:
  require_human_approval:
    specification: true
    plan: true
    constitution: true
    tdd_exception: true

visual:
  enabled: true
  persist_references: false
  references_path: .specify/visual-references
  require_visual_acceptance: true
  visual_regression: false

constitution:
  enabled: true
  require_human_approval: true
  question_format: single_choice_with_free_text
  option_count: 3
  show_recommendation: true
  adaptive_follow_up: true
  require_constitutional_scope: true
```

## TDD

Com TDD ativo, `$speckit-turbo-tdd` mapeia critérios de aceite para testes e exige evidência do ciclo red → green → refactor antes da implementação. Para desativá-lo explicitamente:

```yaml
tdd:
  enabled: false
```

Uma exceção com TDD ativo não é desativação: o agente registra justificativa, risco e validação alternativa em `tdd-cycle.md`, então pausa para aprovação humana quando a política exigir.

## Entrevista da constitution

O fluxo `$speckit-turbo-constitution` pergunta somente sobre princípios duradouros,
normativos e aplicáveis a várias entregas. Ele não transforma decisões de uma feature,
bibliotecas, nomes de arquivos, detalhes visuais isolados ou configurações temporárias em
regras constitucionais.

Cada pergunta apresenta uma política constitucional por vez, três alternativas baseadas
nas evidências do repositório, uma recomendação e uma opção de resposta livre. A resposta
livre passa pela mesma validação de escopo. Candidatos operacionais são descartados e
encaminhados para spec, plano técnico, tarefa, visual spec ou configuração; eles não entram
no draft.

## Screenshots e referências visuais

Anexe o print diretamente ao pedido:

```text
$speckit-turbo-feature Implementar esta tela conforme o print anexado.
```

O agente gera `visual-spec.md`, critérios `VAC-*` e perguntas bloqueantes somente quando uma incerteza muda materialmente a implementação. Por padrão a imagem não é salva. Para persistir referências, habilite `persist_references`; antes de copiar qualquer imagem, o comando visual cria ou valida um bloco gerenciado no `.gitignore` e confirma a regra com Git. O Turbo nunca executa `git add` para imagens.
