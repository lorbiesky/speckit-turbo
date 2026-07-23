# Arquitetura nativa

O Turbo é uma camada complementar, não um fork do GitHub Spec Kit.

```text
catálogos GitHub Raw → bundle speckit-turbo
                           ├─ extensão turbo → comandos speckit.turbo.* + templates + scripts
                           └─ workflows turbo-* → comandos upstream + gates nativos
```

`extension.yml` é a fonte dos doze comandos. A integração Codex registra-os como `$speckit-turbo-*`. Os comandos guiam o agente, preservam `$speckit-*` e nunca criam um runtime próprio.

Cada `workflows/<id>/workflow.yml` descreve um fluxo instalável. Gates, bloqueios e retomada são executados pelo Specify CLI; o único estado operacional fica em `.specify/workflows/runs/<run-id>/` (`state.json`, `inputs.json` e `log.jsonl`).

`bundle.yml` compõe a extensão e os sete workflows, todos na mesma versão de [`VERSION`](../VERSION). Os catálogos em `catalogs/` são metadados públicos que resolvem os assets versionados do GitHub Releases. Um bundle só resolve seus componentes se os catálogos de extensão e workflow também estiverem ativos.

## Limites

- O Turbo não sobrescreve comandos, templates, constitution ou scripts upstream.
- Não há CLI Node, npm, `node_modules`, `.specify/turbo/` nem máquina de estados paralela.
- Workflows não executam comandos arbitrários: testes e validações são conduzidos pelo agente ou pelo pipeline autorizado, e seus resultados são registrados nos artefatos.
- A configuração local fica exclusivamente em `.specify/extensions/turbo/turbo-config.yml`.

## Artefatos

Os artefatos de trabalho continuam próximos da spec do projeto e reconhecíveis pelo Spec Kit. Templates Turbo acrescentam evidências de bug, análise de refactor, ciclo TDD, especificação visual, resumo de entrega e entrevista/draft de constitution. A rastreabilidade obrigatória é requisito → aceitação → decisão → tarefa → código → teste/evidência → revisão.
