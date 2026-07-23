# Constitution socrática

Use `$speckit-turbo-constitution` para criar, revisar ou atualizar regras de engenharia. O fluxo começa com diagnóstico do repositório — constitution existente, orientações de agente, stack, testes, CI, documentação e padrões observáveis — e escolhe criação ou atualização.

O facilitador pergunta uma decisão por vez e adapta a próxima pergunta à resposta. Antes
disso, classifica os candidatos como `constitutional`, `possibly_constitutional` ou
`not_constitutional`. Só candidatos que sejam duradouros, normativos, aplicáveis a várias
entregas, observáveis e objetivamente validáveis entram na entrevista.

Cada pergunta usa escolha única com três políticas constitucionais, uma recomendação baseada
em evidências e uma resposta livre. A recomendação não aprova a decisão. Quando a integração
do agente oferece uma UI nativa de perguntas, ela deve ser usada; caso contrário, o agente
renderiza o mesmo formato em texto.

Decisões de biblioteca para uma feature, nomes de arquivos, detalhes de tela, preferências
visuais isoladas, endpoints, tarefas de refactor e configurações temporárias não são
perguntas constitucionais. Elas são registradas como descartadas, com encaminhamento para
spec, plano técnico, tarefa, visual spec ou configuração.

O resultado intermediário é persistido em:

- `.specify/memory/constitution-interview.md` — diagnóstico, classificação de candidatos, candidatos descartados, perguntas, opções, recomendação, respostas, decisões, confiança, contradições e próxima ação;
- `.specify/memory/constitution.draft.md` — proposta para revisão.

A constitution final nunca é substituída durante a entrevista. O draft contém somente
princípios elegíveis e completos com justificativa, prática observável, validação e limites.
O workflow nativo pausa em um gate humano; somente uma aprovação explícita, sem contradições
críticas ou perguntas bloqueantes, permite aplicar a proposta em `.specify/memory/constitution.md`
com o comando upstream.

Para retomar uma entrevista interrompida, use `$speckit-turbo-resume` ou `specify workflow resume <run-id>`.
