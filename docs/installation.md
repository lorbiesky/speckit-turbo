# Instalação, atualização e remoção

## Projeto novo

Inicialize o projeto com o fluxo oficial do Spec Kit e a integração desejada. Em seguida adicione os catálogos e instale o bundle Turbo:

```bash
specify init --here --integration codex
specify extension catalog add https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/extensions.json --name speckit-turbo --install-allowed
specify workflow catalog add https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/workflows.json
specify bundle catalog add https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/bundles.json --id speckit-turbo --policy install-allowed
specify bundle install speckit-turbo
```

O bundle instala a extensão `turbo` e os sete workflows `turbo-*`. A configuração opcional é criada em `.specify/extensions/turbo/turbo-config.yml` pela extensão; os assets upstream permanecem sob controle do Spec Kit.

## Projeto Spec Kit existente

Execute somente os três comandos de catálogo e `specify bundle install speckit-turbo`. A instalação é composicional: não altera `.specify/memory/constitution.md`, templates, scripts, comandos ou workflows já presentes. Se um componente tiver o mesmo id, o Spec Kit mostrará o conflito em vez de sobrescrevê-lo silenciosamente.

## Atualização

Atualize primeiro o próprio Spec Kit e então os componentes instalados:

```bash
specify self upgrade
specify extension update turbo
specify workflow update
specify bundle update speckit-turbo
```

Revise os release notes e as diferenças antes de aprovar uma atualização. A configuração local da extensão não deve ser apagada por uma atualização.

## Remoção

Remova apenas os componentes Turbo. Componentes e artefatos de terceiros continuam intactos.

```bash
specify bundle remove speckit-turbo
specify extension remove turbo
specify workflow remove turbo-feature
```

Repita o último comando para os demais `turbo-*` se o bundle não os removeu como parte da operação. Preserve `.specify/extensions/turbo/turbo-config.yml` se desejar reutilizar sua política em uma instalação futura.

## Migração de instalação legada

Versões anteriores usavam uma distribuição npm e arquivos em `.specify/turbo/`. O Turbo 2 não remove nem altera automaticamente esses arquivos, configurações antigas, specs ou constitutions. Siga o [guia de migração segura](migration-npm.md) depois de confirmar a nova instalação.
