# Instalação, atualização e remoção

## Instalação com um comando

O bootstrap oficial baixa somente um script pequeno do GitHub Raw e usa o Specify CLI local. Este repositório não é clonado.

Linux/macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.4/scripts/install-turbo.sh | sh -s -- .
```

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.4/scripts/Install-Turbo.ps1)))
```

O diretório atual é o padrão. Para outro diretório, use `sh -s -- ./meu-projeto` ou execute o script PowerShell baixado com `-ProjectRoot .\meu-projeto`. O instalador é idempotente e apenas encadeia comandos oficiais do Spec Kit.

No PowerShell, use `ScriptBlock` como mostrado acima; isso evita que o pipeline `irm | iex` interprete linhas do script remoto como argumentos separados.

## Projeto novo

Inicialize o projeto com o fluxo oficial do Spec Kit e a integração desejada. Em seguida, execute o instalador de um comando:

```bash
specify init --here --integration codex
curl -fsSL https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.4/scripts/install-turbo.sh | sh -s -- .
```

O instalador registra a extensão `turbo`, os sete workflows `turbo-*` e o bundle. A configuração é criada em `.specify/extensions/turbo/turbo-config.yml`; os assets upstream permanecem sob controle do Spec Kit.

## Projeto Spec Kit existente

Execute apenas o instalador de um comando na raiz do projeto. A instalação é composicional: não altera `.specify/memory/constitution.md`, templates, scripts, comandos ou workflows upstream já presentes. Workflows e extensão Turbo já instalados são atualizados de forma não interativa; configurações locais da extensão são preservadas.

### Se a instalação falhar

Primeiro atualize o Spec Kit. Depois, execute novamente o instalador da release atual; ele substitui apenas as URLs de catálogo gerenciadas pelo Turbo.

```bash
specify self upgrade
curl -fsSL https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.4/scripts/install-turbo.sh | sh -s -- .
```

O identificador correto do bundle é `speckit-turbo`; nomes como `speckit-turboclear` não existem no catálogo. Não execute `specify workflow update` no bootstrap automatizado: o comando é interativo.

## Atualização

Atualize primeiro o próprio Spec Kit e então execute novamente o instalador da release desejada:

```bash
specify self upgrade
curl -fsSL https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.4/scripts/install-turbo.sh | sh -s -- .
```

Revise os release notes antes de atualizar. A configuração local da extensão não deve ser apagada por uma atualização.

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
