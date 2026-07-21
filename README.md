# Spec Kit Turbo

Camada local, versionada e reutilizável sobre o [GitHub Spec Kit](https://github.com/github/spec-kit). O Turbo mantém os artefatos e comandos reconhecíveis do Spec Kit (`specify`, `plan`, `tasks`, `implement`) e adiciona roteamento, skills, gates, retomada e rastreabilidade para trabalhar melhor com agentes de código — inicialmente Codex.

## O que ele resolve

O Turbo separa a parte criativa do agente da parte previsível do processo:

```text
Pedido → classificação → workflow → skill responsável → artefatos/gates → entrega
                         ↑                                      ↓
                    state.json ← pausa, aprovação e retomada ← evidências
```

- O agente pesquisa, especifica, planeja, implementa, testa e revisa.
- O runtime controla a ordem das fases, condições, precondições, checkpoints e evidências mínimas.
- O Spec Kit continua sendo a referência para os artefatos upstream; o Turbo não faz fork dele.

## Capacidades

- instalação limpa ou adaptação segura de um projeto que já usa Spec Kit;
- workflows para `feature`, `bugfix`, `refactor`, `discovery`, `maintenance`, `hotfix` e `constitution`;
- skills para orquestração, produto, arquitetura, implementação, testes, revisão, constitution socrática e especificação visual;
- estado persistente em `.specify/turbo/state.json`, com retomada por outro agente ou sessão;
- gates com evidência obrigatória e checkpoints humanos configuráveis;
- criação e atualização segura da constitution por entrevista socrática;
- análise de screenshots em `visual-spec.md`, com critérios visuais `VAC-*`;
- proteção de referências visuais persistidas com `.gitignore` e `git check-ignore`;
- `doctor`, validação estrutural, manifesto de versão, backup e upgrade idempotente.

## Pré-requisitos

- Node.js 18+ e npm;
- Git;
- para instalação limpa: `uv` e acesso ao repositório upstream do Spec Kit.

Python 3.10+ só é necessário para contribuir e executar a suíte legada de validação:

```bash
python3 -m pip install -r requirements-dev.txt
```

## Instalação via npm

O modo recomendado é executar sem instalação global:

```bash
npx speckit-turbo@latest init ../meu-projeto --mode existing
```

Ou instale globalmente para usar o comando sem `npx`:

```bash
npm install --global speckit-turbo
speckit-turbo init ../meu-projeto --mode existing
```

O pacote npm inclui workflows, skills, templates, schemas e um runtime Node autocontido. Não há pré-requisito de Python, `pip` ou PyYAML para instalar, diagnosticar ou conduzir fluxos. Use `npx speckit-turbo@latest help` para ver os comandos, `npx speckit-turbo@latest doctor . --strict` para diagnosticar um consumidor e `npx speckit-turbo@latest version .` para consultar a versão instalada.

O instalador altera somente assets gerenciados pelo Turbo:

```text
.agents/skills/turbo-*
.specify/turbo/
bloco delimitado do AGENTS.md
bloco delimitado de referências visuais no .gitignore
```

Ele nunca substitui o conteúdo externo a esses blocos. Em upgrades, um backup dos assets Turbo é criado em `.specify/turbo/backups/`.

## Primeira configuração

No projeto consumidor, edite `.specify/turbo/project.yml`. Troque os placeholders e habilite apenas os gates que o projeto consegue executar.

```yaml
project:
  name: customer-portal
  type: frontend
  stack: angular

commands:
  install: npm ci
  lint: npm run lint
  test: npm test -- --watch=false
  build: npm run build

workflow:
  require_clarification: true
  require_plan_approval: true
  require_tests: true
  require_final_review: true
  human_checkpoints:
    - product-specification
    - technical-plan
```

Cada fase listada em `human_checkpoints` para em `awaiting_approval` depois de reunir as evidências. Uma fase declarada como checkpoint `always` — por exemplo, a aprovação da constitution — sempre pede decisão humana.

Rode o diagnóstico antes de iniciar trabalho:

```bash
cd ../meu-projeto
npx speckit-turbo@latest doctor .
```

Use `--strict` em automação para tratar warnings, como placeholders, como falha:

```bash
npx speckit-turbo@latest doctor . --strict
```

## Uso diário: workflow guiado

### Comandos no Codex

No Codex, o caminho mais curto é usar `$turbo` com o pedido em linguagem natural. Ele classifica o trabalho, identifica retomadas e screenshots, inicia o workflow e encaminha para a skill responsável:

```text
$turbo Criar checkout como visitante
$turbo Corrigir erro 500 ao finalizar pagamento
$turbo Atualizar as regras de engenharia do projeto
$turbo-status
$turbo-resume
```

Atalhos explícitos estão disponíveis quando a classificação já é conhecida: `$turbo-feature`, `$turbo-bugfix`, `$turbo-refactor`, `$turbo-discovery`, `$turbo-maintenance`, `$turbo-hotfix` e `$turbo-constitution`. Eles complementam — e não substituem — os comandos upstream `$speckit-*`.

O runtime instalado é `.specify/turbo/turbo.js`. Ele **não executa as skills nem comandos do Spec Kit sozinho**: o agente realiza o trabalho e produz os artefatos; o runtime registra o fluxo e só permite avançar com a evidência requerida.

Todos os comandos abaixo devem ser executados na raiz do projeto consumidor.

### 1. Inicie um trabalho

```bash
node .specify/turbo/turbo.js workflow --path . start feature --work-id checkout-guest
```

Classificações disponíveis:

| Classificação | Quando usar |
| --- | --- |
| `feature` | novo comportamento ou capacidade do produto |
| `bugfix` | falha observável com reprodução, causa raiz e regressão |
| `refactor` | mudança estrutural com invariantes comportamentais |
| `discovery` | pesquisa para apoiar decisão, sem compromisso de implementação |
| `maintenance` | atualização operacional, dependência ou tarefa técnica planejada |
| `hotfix` | correção urgente com contenção e risco de produção |
| `constitution` | criação ou evolução das regras de engenharia do projeto |

O comando cria as fases do workflow em `state.json` e mostra a fase aplicável atual, o responsável e os requisitos do gate. O template inicial pode ser substituído automaticamente; para substituir um trabalho já iniciado, use `--force` conscientemente.

### 2. Siga a skill indicada

O resultado do runtime aponta o `Owner`. Carregue a skill correspondente em `.agents/skills/turbo-*/SKILL.md`, execute o trabalho e gere os artefatos solicitados pela fase.

Exemplo de sequência típica de feature:

```text
turbo-orchestrator
→ turbo-visual-specifier (somente com imagem)
→ turbo-product-owner + speckit-specify
→ turbo-architect + speckit-plan
→ turbo-orchestrator + speckit-tasks/analyze
→ turbo-implementation-specialist + speckit-implement
→ turbo-test-engineer
→ turbo-code-reviewer
→ delivery-summary.md
```

### 3. Registre a conclusão da fase

Cada item do gate deve receber uma evidência curta, verificável e vinculada a um artefato, comando, teste ou decisão. Use o identificador exibido pelo runtime.

```bash
node .specify/turbo/turbo.js workflow --path . complete intake \
  --evidence classified_as_feature="Pedido classificado como feature no state.json" \
  --evidence scope_recorded="Escopo e exclusões registrados em spec.md" \
  --evidence project_profile_loaded="project.yml revisado para Angular"
```

Se faltar evidência ou o identificador não pertencer ao gate, o comando falha e o estado não avança. Isso evita concluir uma fase apenas por declaração.

### 4. Trate checkpoints humanos

Depois de concluir uma fase configurada como checkpoint, o runtime fica pausado. Registre a decisão de forma explícita:

```bash
node .specify/turbo/turbo.js workflow --path . checkpoint technical-plan \
  --approve --note "Plano aprovado pela equipe em 2026-07-21"
```

Ou bloqueie o avanço e preserve o motivo:

```bash
node .specify/turbo/turbo.js workflow --path . checkpoint technical-plan \
  --reject --note "Avaliar impacto da nova dependência antes de seguir"
```

Após resolver uma rejeição ou bloqueio, retome:

```bash
node .specify/turbo/turbo.js workflow --path . resume
```

### 5. Consulte ou atualize o estado

```bash
node .specify/turbo/turbo.js workflow --path . status
node .specify/turbo/turbo.js workflow --path . status --refresh
```

`--refresh` reavalia condições e precondições declaradas. Ele pula fases não aplicáveis — por exemplo, `visual-analysis` sem print — e mostra a próxima ação segura.

## Screenshots e especificações visuais

Ao abrir uma feature com print, informe os arquivos de entrada ao iniciar o workflow:

```bash
node .specify/turbo/turbo.js workflow --path . start feature \
  --work-id checkout-ui --visual-input /caminho/do/print.png
```

Isso ativa `turbo-visual-specifier` antes da especificação de produto. A skill transforma a imagem em `visual-spec.md`, separando fatos `observed`, hipóteses `inferred`, lacunas `unknown`, confiança e critérios de aceite `VAC-*`. A especificação de produto só fica disponível após a conclusão dessa fase.

Por padrão, o Turbo não copia imagens. Para persistir referências, configure:

```yaml
visual:
  enabled: true
  persist_references: true
  references_path: .specify/visual-references
  require_visual_acceptance: true
  visual_regression: false
```

O instalador cria e mantém somente este bloco no `.gitignore`:

```gitignore
# speckit-turbo:start
.specify/visual-references/
# speckit-turbo:end
```

Antes de persistir uma imagem, a skill deve confirmar `git check-ignore`. Se a proteção não funcionar, a análise é bloqueada e nenhuma imagem é copiada ou adicionada ao Git.

## Constitution socrática

Para criar ou atualizar as regras de engenharia, inicie o workflow `constitution` e siga `turbo-constitution-facilitator`:

```bash
node .specify/turbo/turbo.js workflow --path . start constitution --work-id engineering-principles
```

O facilitador:

1. analisa stack, CI, testes, documentação, `AGENTS.md` e a constitution existente;
2. faz uma pergunta por vez, baseada em evidências do repositório;
3. persiste respostas e decisões em `.specify/memory/constitution-interview.md`;
4. gera `.specify/memory/constitution.draft.md` por meio do `speckit-constitution`;
5. exige aprovação humana antes de alterar `.specify/memory/constitution.md`.

Em uma conversa com o agente, use intenções como “crie a constitution”, “atualize a constitution” ou “retome a entrevista da constitution”. A constitution final nunca deve ser substituída quando há perguntas bloqueantes, contradições, rejeição ou falha na geração do draft.

## Artefatos e rastreabilidade

O Turbo mantém a cadeia:

```text
requisito → critério de aceite → decisão → tarefa → código → teste/evidência → revisão
```

Os principais artefatos ficam nos locais esperados pelo Spec Kit ou no diretório Turbo:

| Artefato | Finalidade |
| --- | --- |
| `spec.md` | problema, escopo, requisitos e critérios de aceite |
| `clarifications.md` | perguntas e respostas que eliminam ambiguidade |
| `visual-spec.md` | inventário e critérios visuais derivados de screenshots |
| `plan.md` | plano técnico, riscos, contratos e decisões |
| `tasks.md` | tarefas mapeadas aos critérios de aceite |
| `bug-evidence.md` / `root-cause.md` | reprodução e investigação de bugfix |
| `refactor-analysis.md` | invariantes, baseline e fronteiras de refactor |
| `delivery-summary.md` | validações, riscos residuais e follow-ups |
| `.specify/turbo/state.json` | fase, evidências, perguntas, bloqueios e próxima ação |

## Diagnóstico, atualização e versão

```bash
# diagnóstico da instalação consumidora
npx speckit-turbo@latest doctor . --strict

# versão do Turbo instalada no projeto atual
npx speckit-turbo@latest version .

# atualização do projeto consumidor
npx speckit-turbo@latest upgrade ../meu-projeto
```

O `doctor` verifica integração, assets, perfil, comandos de qualidade, estado, constitution, referências visuais, backups e proteção do `.gitignore`. Ele não modifica o projeto.

## Desenvolvimento do Turbo

Antes de enviar mudanças, execute:

```bash
python3 scripts/validate.py
npm test
npm pack --dry-run
git diff --check
```

O validador cobre schemas, templates, skills, owners, gates, condições, checkpoints, precondições e roteamento de classificações.

Consulte também [a documentação de instalação](docs/installation.md) e [a arquitetura](docs/architecture.md).
