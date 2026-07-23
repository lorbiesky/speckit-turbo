# Instalação, atualização e remoção

## Instalação com um comando

O bootstrap oficial baixa somente um script pequeno do GitHub Raw e usa o Specify CLI local. Este repositório não é clonado.

Linux/macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.2/scripts/install-turbo.sh | sh -s -- .
```

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.2/scripts/Install-Turbo.ps1)))
```

O diretório atual é o padrão. Para outro diretório, use `sh -s -- ./meu-projeto` ou execute o script PowerShell baixado com `-ProjectRoot .\meu-projeto`. O instalador é idempotente e apenas encadeia comandos oficiais do Spec Kit.

No PowerShell, use `ScriptBlock` como mostrado acima; isso evita que o pipeline `irm | iex` interprete linhas do script remoto como argumentos separados.

## Projeto novo

Inicialize o projeto com o fluxo oficial do Spec Kit e a integração desejada. Em seguida adicione os catálogos e instale o bundle Turbo:

```bash
specify init --here --integration codex
specify extension catalog add https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/extensions.json --name speckit-turbo --install-allowed
specify workflow catalog add https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/workflows.json
specify bundle catalog add https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/bundles.json --id speckit-turbo --policy install-allowed
specify workflow add turbo-feature
specify workflow add turbo-bugfix
specify workflow add turbo-refactor
specify workflow add turbo-maintenance
specify workflow add turbo-hotfix
specify workflow add turbo-discovery
specify workflow add turbo-constitution
specify bundle install speckit-turbo
```

O bundle instala a extensão `turbo` e registra a composição dos sete workflows `turbo-*`; os sete comandos `specify workflow add` garantem a instalação dos workflows pelo caminho nativo compatível. A configuração é criada em `.specify/extensions/turbo/turbo-config.yml`; os assets upstream permanecem sob controle do Spec Kit.

## Projeto Spec Kit existente

Execute os comandos de catálogo, instale os sete workflows com `specify workflow add` e finalize com `specify bundle install speckit-turbo`. A instalação é composicional: não altera `.specify/memory/constitution.md`, templates, scripts, comandos ou workflows já presentes. Se um componente tiver o mesmo id, o Spec Kit mostrará o conflito em vez de sobrescrevê-lo silenciosamente.

### Se aparecer `--dev source must be a workflow YAML`

Isso significa que o bundle tentou delegar a instalação de um workflow antes que ele estivesse instalado. Não use `--dev` para corrigir essa mensagem. Execute os sete comandos de workflow da seção anterior e repita:

```bash
specify bundle install speckit-turbo
```

Se aparecer `HTTP Error 404` para `speckit-turbo-bundle-2.0.2.zip`, atualize os catálogos e confirme que o Spec Kit é `>=0.11.4`:

```bash
specify self upgrade
specify bundle catalog remove speckit-turbo
specify bundle catalog add https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/bundles.json --id speckit-turbo --policy install-allowed
```

O identificador correto do bundle é `speckit-turbo`; nomes como `speckit-turboclear` não existem no catálogo.

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
