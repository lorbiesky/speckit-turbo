# Desenvolvimento, validação e release

## Estrutura

- `extension.yml` e `commands/`: extensão Turbo e comandos de agente.
- `workflows/`: workflows nativos instaláveis.
- `templates/` e `scripts/`: assets da extensão.
- `bundle.yml`: composição versionada.
- `catalogs/`: índices para os assets do GitHub Releases.
- `VERSION`: fonte única de versão.
- `scripts/install-turbo.sh` e `scripts/Install-Turbo.ps1`: conveniências de instalação que apenas encadeiam o Specify CLI.

## Validação local

Python é usado somente para manutenção do repositório, não por consumidores:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
git diff --check
```

Para verificar a compatibilidade com o Spec Kit atual, use uma instalação `>=0.11.4` e instale a extensão e workflows a partir de caminhos locais de desenvolvimento. Depois valide o bundle com `specify bundle validate` e produza o asset com `specify bundle build`.

## Release

1. Atualize `VERSION`, `extension.yml`, `bundle.yml` e os catálogos para a mesma versão.
2. Execute todos os gates locais.
3. Crie a tag `v<versão>` e publique-a.
4. O workflow de release cria os zips da extensão, dos workflows e do bundle, e os anexa ao GitHub Release.
5. Confirme que os URLs nos catálogos resolvem os assets publicados e teste uma instalação limpa pelo bundle.

Não publique no npm: GitHub Releases e os catálogos do Spec Kit são a única distribuição pública do Turbo.
