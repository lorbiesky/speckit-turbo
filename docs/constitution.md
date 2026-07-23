# Constitution socrática

Use `$speckit-turbo-constitution` para criar, revisar ou atualizar regras de engenharia. O fluxo começa com diagnóstico do repositório — constitution existente, orientações de agente, stack, testes, CI, documentação e padrões observáveis — e escolhe criação ou atualização.

O facilitador pergunta uma decisão por vez e adapta a próxima pergunta à resposta. Os temas são princípios de engenharia, qualidade e testes, arquitetura, segurança e privacidade, documentação, colaboração e governança.

O resultado intermediário é persistido em:

- `.specify/memory/constitution-interview.md` — diagnóstico, perguntas, respostas, decisões, confiança, contradições e próxima ação;
- `.specify/memory/constitution.draft.md` — proposta para revisão.

A constitution final nunca é substituída durante a entrevista. O workflow nativo pausa em um gate humano; somente uma aprovação explícita, sem contradições críticas ou perguntas bloqueantes, permite aplicar a proposta em `.specify/memory/constitution.md` com o comando upstream.

Para retomar uma entrevista interrompida, use `$speckit-turbo-resume` ou `specify workflow resume <run-id>`.
