# Migração segura da distribuição npm legada

O Spec Kit Turbo 2.0 substitui a distribuição npm por componentes nativos do GitHub Spec Kit. A migração não apaga automaticamente nada do projeto.

## Antes de começar

1. Atualize o Spec Kit para `>=0.11.4` com `specify self upgrade`.
2. Faça uma cópia de `.specify/turbo/` se uma instalação legada existir.
3. Registre qualquer workflow ativo e seus artefatos antes de mudar de mecanismo.

## Instale a composição nativa

Adicione os catálogos de extensão, workflow e bundle e instale `speckit-turbo`, conforme o [guia de instalação](installation.md). Confirme que `specify extension list` mostra `turbo` e que `specify workflow list` mostra os sete workflows `turbo-*`.

No Codex, confirme os novos comandos:

```text
$speckit-turbo-start Retomar a entrega atual
$speckit-turbo-status
```

Os novos gates e retomadas passam a usar `.specify/workflows/runs/<run-id>/`. Não copie ou edite manualmente o estado legado para esse diretório.

## Limpeza opcional

Somente após confirmar a nova instalação e guardar o backup, remova manualmente os arquivos legados conhecidos em `.specify/turbo/`. Não remova specs, constitution, templates upstream, evidências ou configurações do projeto. A limpeza é opcional: os assets legados não são executados pela arquitetura nativa.
