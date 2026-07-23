# Spec Kit Turbo

Spec Kit Turbo é uma composição nativa para o [GitHub Spec Kit](https://github.com/github/spec-kit). Ele acrescenta comandos, workflows e templates para tornar SDD, TDD, especificação visual e governança mais consistentes.

O Turbo fica no mesmo nível dos componentes oficiais do Spec Kit: uma extensão registra comandos `speckit.turbo.*`; workflows nativos coordenam etapas, gates e retomadas; e um bundle instala a composição versionada.

## Pré-requisitos

- GitHub Spec Kit `>=0.11.4`;
- um projeto inicializado pelo Spec Kit com uma integração suportada. Codex é o caminho prioritário;
- Git para persistir referências visuais opcionais com segurança.

Atualize o Spec Kit quando necessário:

```bash
specify self upgrade
specify version
```

## Instalação

Adicione os catálogos do Turbo ao projeto e instale o bundle. Isso é seguro tanto para um projeto novo quanto para um projeto que já usa Spec Kit: o Turbo não substitui constitution, templates, comandos ou workflows upstream.

Linux/macOS, sem clonar este repositório:

```bash
curl -fsSL https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.1/scripts/install-turbo.sh | sh -s -- .
```

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.1/scripts/Install-Turbo.ps1)))
```

Para outro diretório, use `sh -s -- ./meu-projeto` no shell ou execute `& ([scriptblock]::Create((irm https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.1/scripts/Install-Turbo.ps1))) -ProjectRoot .\meu-projeto`. O bootstrap usa o Specify CLI e não instala Node, npm ou um runtime próprio.

```bash
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

Os workflows são adicionados explicitamente antes do bundle para manter compatibilidade com versões do Specify CLI que delegam incorretamente a instalação de workflows de catálogo durante `bundle install`. A operação é idempotente; se já estiverem instalados, o Spec Kit apenas os reutiliza.

Se o Specify mostrar `--dev source must be a workflow YAML`, os sete comandos `specify workflow add` ainda não foram executados. Se mostrar `HTTP Error 404` para o bundle, atualize o Spec Kit e recarregue o catálogo; o asset oficial `v2.0.1` está publicado no GitHub Releases.

Consulte os componentes instalados com `specify extension list`, `specify workflow list` e `specify bundle list`. Para instruções completas, inclusive projeto novo, atualização e remoção, leia [o guia de instalação](docs/installation.md). Instalações legadas têm um [guia de migração seguro](docs/migration-npm.md).

## Uso no Codex

Após a instalação, use os comandos de agente. Eles preservam os comandos upstream `$speckit-*` e pedem sua intervenção somente quando houver uma decisão ou gate relevante.

```text
$speckit-turbo-start Criar checkout como visitante
$speckit-turbo-feature Implementar esta tela conforme o print anexado
$speckit-turbo-bugfix Corrigir falha de autenticação após expiração do token
$speckit-turbo-refactor Extrair regras de preço do módulo de checkout
$speckit-turbo-status
$speckit-turbo-resume
```

Atalhos disponíveis:

- `$speckit-turbo-start`
- `$speckit-turbo-feature`, `$speckit-turbo-bugfix`, `$speckit-turbo-refactor`
- `$speckit-turbo-maintenance`, `$speckit-turbo-hotfix`, `$speckit-turbo-discovery`
- `$speckit-turbo-constitution`, `$speckit-turbo-status`, `$speckit-turbo-resume`
- `$speckit-turbo-tdd`, `$speckit-turbo-visual`

Os workflows instalados podem também ser iniciados ou retomados com `specify workflow run`, `specify workflow status` e `specify workflow resume`. O estado pertence ao Spec Kit em `.specify/workflows/runs/<run-id>/`.

## O que o Turbo acrescenta

- SDD: problema, escopo e aceitação antes do plano e da implementação.
- TDD configurável: novos projetos têm `tdd.enabled: true`; red → green → refactor é registrado, e exceções exigem justificativa, validação alternativa e aprovação quando configurada.
- Visual specs: screenshots anexados produzem `visual-spec.md` e critérios `VAC-*`, classificados como observado, inferido ou desconhecido.
- Constitution socrática: entrevista adaptativa, draft e aprovação humana antes de modificar `.specify/memory/constitution.md`.
- Gates e retomada nativos: decisões e pausas usam workflows do Spec Kit, não um `state.json` paralelo.

Configure somente a extensão em `.specify/extensions/turbo/turbo-config.yml`. Veja [configuração](docs/configuration.md), [constitution](docs/constitution.md) e [arquitetura](docs/architecture.md).

## Desenvolvimento e releases

O repositório publica assets versionados no GitHub Releases e os catálogos apontam para esses assets. A versão única é [`VERSION`](VERSION). Para validar, empacotar ou lançar uma versão, siga [desenvolvimento e release](docs/development.md).

## Licença

[MIT](LICENSE).
