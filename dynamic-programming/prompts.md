# prompts.md · Uso de IA no módulo de Dynamic Programming

O briefing da GS e o professor da disciplina pedem que os prompts usados com IA fiquem registrados neste arquivo. Abaixo estão os prompts **na íntegra**, na ordem em que foram enviados.

- **Ferramenta:** Claude (Anthropic), em uma conversa de 06, 07, 12 e 17/11/2026, conduzida por Pedro Henrique dos Santos.
- **Arquivos anexados pela equipe:**
  - `artesp_gtfs.zip` (GTFS público da ARTESP).
  - `Validacao_GTFS_ARTESP.md` e `Corredor_Itapecerica.geojson` (tarefa 1.6).
  - `PHAROS — Definição de Escopo e MVP` (v0.1).
  - Briefing oficial `GS CitizenTech - 2ES Fev - FIAP 2026.pdf`.
  - Critérios de correção do professor de Dynamic Programming.

**[PREENCHER]** Se outros prompts foram usados, em outras conversas ou ferramentas, acrescente-os ao final. Isso inclui a preparação do prompt 1, que veio com o título "Prompt completo para você usar na IA", e a tarefa 1.6.

---

## Prompt 1 · 06/11/2026

**Mensagem:**

> opa, fiquei com as meterias de Dynamic Programming e DATABASE DESIG, mas agora vamos fazer a parte de Dynamic 
>
> Preciso de uma devolutiva:
> [ ] Um par concreto de origem e destino com alternativas distintas, ou evidência de que não foi encontrado.
> [ ] Identificadores das linhas e paradas utilizados.
> [ ] Código Python executável, não apenas pseudocódigo.
> [ ] Resultados reais dos testes e casos sem caminho.
> [ ] Decisão recomendada sobre Python → Oracle → Java.
> [ ] Limitações e funcionalidades que precisam sair ou mudar no MVP.

**Prompt anexado (`attachment.txt`):**

> Prompt completo para você usar na IA:
> # PHAROS — Validação técnica de Dynamic Programming e alternativas de trajetos
>
> Você atuará como analista de redes de transporte, algoritmos de grafos e programação dinâmica.
>
> **Objetivo:** analisar os arquivos anexados e verificar se o MVP do projeto acadêmico Pharos é tecnicamente viável, especialmente sua funcionalidade de comparação de trajetos.
>
> Não quero apenas explicações teóricas. Quero uma análise reproduzível com resultados fundamentados nos arquivos, código Python e evidências.
>
> ## 1. Contexto do projeto
>
> **Projeto:** Pharos — Global Solution FIAP 2026.2, CitizenTech.
>
> **Prazo de entrega:** 19/11/2026.
>
> **Público:** estudantes e trabalhadores que utilizam transporte coletivo na Grande São Paulo.
>
> **Território piloto:** Estrada de Itapecerica, região do Capão Redondo, Zona Sul de São Paulo.
>
> **Objetivo da solução:** desenvolver uma plataforma web responsiva que permita comparar alternativas de deslocamento, mostrando informações como tempo programado, distância de caminhada quando houver dados adequados, quantidade de baldeações e indicadores históricos agregados de ocorrências próximas.
>
> O sistema não deve prever crimes, estimar risco individual nem afirmar que um trajeto é seguro.
>
> ## 2. Arquivos anexados
>
> 1. `artesp_gtfs.zip` — GTFS da ARTESP de 07/10/2026.
> 2. `Validacao_GTFS_ARTESP.md` — relatório técnico anterior.
> 3. `Corredor_Itapecerica.geojson` — corredor inicialmente analisado.
> 4. `Escopo do MVP — Pharos v0.1` — documento de produto.
> 5. Requisitos oficiais da disciplina Dynamic Programming.
>
> Inspecione os arquivos efetivamente recebidos. Se algum estiver ausente, informe a limitação e não invente resultados.
>
> ## 3. Informações da análise anterior
>
> Uma auditoria anterior relatou os seguintes resultados:
>
> - 823 rotas cadastradas no GTFS.
> - 759 rotas com sequências de paradas utilizáveis.
> - 280 rotas com pelo menos uma parada programada no município de São Paulo.
> - As linhas 001 e 002 compartilham 28 paradas na Estrada de Itapecerica.
> - Foi realizado um cruzamento geográfico inicial com ocorrências históricas da SSP-SP.
>
> Esses números são antecedentes da investigação, não devem ser aceitos automaticamente. Confira os dados necessários nos arquivos.
>
> ## 4. Tarefa A — Validar alternativas reais
>
> Identifique se existe pelo menos um par de origem e destino na região piloto com dois trajetos efetivamente diferentes.
>
> Para isso:
>
> 1. Identifique as linhas e seus sentidos.
> 2. Verifique os pontos de parada, as sequências e os traçados.
> 3. Diferencie linhas distintas que percorrem o mesmo caminho de trajetos geometricamente diferentes.
> 4. Investigue se existem conexões ou baldeações viáveis entre serviços.
> 5. Verifique se os serviços escolhidos operam em um mesmo cenário temporal, quando essa comparação depender dos horários.
> 6. Identifique pares de pontos com duas ou três alternativas efetivamente utilizáveis.
> 7. Se as linhas 001 e 002 não oferecerem alternativas diferentes, procure outras linhas próximas ou recomende uma ampliação limitada do piloto.
>
> **Resultado obrigatório:** uma tabela com origem, destino, identificadores das linhas, alternativas, diferença entre percursos, existência de baldeações e evidência extraída do GTFS.
>
> Não considere duas linhas que compartilham o mesmo itinerário como dois caminhos geometricamente distintos.
>
> ## 5. Tarefa B — Construir o grafo piloto
>
> Proponha e, se possível, implemente em Python um grafo pequeno, fiel aos dados analisados.
>
> Especifique:
>
> - O que representa cada vértice.
> - O que representa cada aresta.
> - Como as paradas são identificadas.
> - Como os sentidos de viagem são respeitados.
> - Como as conexões e baldeações são representadas.
> - Como os pesos de tempo e distância são calculados.
> - Como são tratados dados ausentes ou horários interpolados.
>
> Não invente tempos, distâncias ou conexões.
>
> Se forem utilizadas aproximações, declare as hipóteses e suas limitações.
>
> ## 6. Tarefa C — Validar Dynamic Programming
>
> A disciplina exige utilizar programação dinâmica.
>
> Avalie a adequação do algoritmo de Floyd–Warshall ao tamanho da rede piloto.
>
> Se for adequado, implemente uma prova de conceito com:
>
> - Matriz de custos.
> - Cálculo de caminhos mínimos.
> - Reconstrução dos caminhos.
> - Testes com rotas possíveis e impossíveis.
> - Análise de complexidade temporal e espacial.
> - Comparação entre pelo menos dois critérios de custo, quando sustentados pelos dados.
>
> Se Floyd–Warshall não for adequado à rede completa, proponha um recorte menor justificável.
>
> Não substitua automaticamente Floyd–Warshall por Dijkstra e afirme que os requisitos de programação dinâmica foram atendidos. Verifique primeiro o enunciado oficial.
>
> ## 7. Tarefa D — Integração com Java e Oracle
>
> A aplicação principal do Pharos utilizará:
>
> - Front-end web responsivo.
> - API REST Java Spring Boot.
> - Servidor Oracle da FIAP.
> - Dados tratados da ARTESP e SSP-SP.
>
> Compare duas possibilidades:
>
> **Opção 1 — Processamento prévio**
>
> O Python lê a rede, calcula as alternativas e exporta resultados em CSV ou JSON. Os resultados são carregados no Oracle e consultados pela API Java.
>
> **Opção 2 — Processamento sob demanda**
>
> A API Java solicita o cálculo de caminhos a um componente Python em execução.
>
> Para cada alternativa, avalie complexidade, dependências, deploy, manutenção e viabilidade até 19/11/2026.
>
> Recomende uma arquitetura para o MVP, explicitando se o algoritmo será executado previamente ou durante cada consulta.
>
> A entrega de Dynamic Programming deve continuar demonstrável e testável de forma independente.
>
> ## 8. Tarefa E — Avaliar funcionalidades do MVP
>
> Determine quais funcionalidades podem ser implementadas com os dados existentes:
>
> - Seleção de origem e destino.
> - Comparação de trajetos diferentes.
> - Tempo programado de viagem.
> - Distância de caminhada.
> - Quantidade de baldeações.
> - Sequência de paradas.
> - Escolha de critério de comparação.
>
> Classifique cada uma como:
>
> - Viável com os dados atuais.
> - Viável com restrições.
> - Dependente de fonte adicional.
> - Inviável no prazo ou no recorte atual.
>
> Para distância de caminhada, não utilize automaticamente a distância em linha reta como distância real percorrida a pé.
>
> ## 9. Entregáveis da análise
>
> Devolva:
>
> 1. **Conclusão objetiva:** o corredor atual suporta comparação real de trajetos? Sim, não ou ainda não comprovado.
> 2. **Tabela de alternativas:** pares origem–destino e caminhos identificados.
> 3. **Modelo de grafo:** vértices, arestas, pesos e conexões.
> 4. **Prova de conceito Python:** código executável e instruções de execução.
> 5. **Resultado dos testes:** saídas reais, casos sem solução e limitações.
> 6. **Recomendação de arquitetura:** integração com Java e Oracle.
> 7. **Lista de funcionalidades viáveis:** o que podemos manter no MVP.
> 8. **Riscos e pendências:** quais decisões ainda dependem de dados ou da equipe.
> 9. **Resumo para o Notion:** texto curto para registrar como evidência na tarefa 2.1.
>
> ## 10. Regras
>
> - Utilize os arquivos anexados como fonte principal.
> - Diferencie fatos verificados, hipóteses e recomendações.
> - Não invente rotas, horários, métricas ou conexões.
> - Não trate a contagem de ocorrências criminais como risco individual.
> - Não afirme que duas alternativas são diferentes apenas porque pertencem a linhas distintas.
> - Não considere horários de 2026 como prova do serviço disponível durante ocorrências de 2025.
> - Evite complexidade desnecessária: precisamos de uma solução acadêmica reproduzível até 19/11.
>
> **Comece verificando os arquivos anexados e depois execute a análise técnica.**

**O que a IA produziu:**

- Análise do GTFS, com contagens, interpolação dos horários e viagens duplicadas.
- Pares origem–destino com alternativas distintas.
- Código do pacote `pharos/`, testes, exportação para o Oracle e o relatório `docs/RELATORIO_VALIDACAO_DP.md`.

---

## Prompt 2 · 06/11/2026

> oq falta eu fazer dessa materia, e oq vc precisa saber mais???

**O que a IA produziu:** lista de pendências da disciplina (nomes e RMs, Ficha no README, decisão de território, teste em máquina da equipe, defesa) e perguntas para a equipe.

---

## Prompt 3 · 07/11/2026

> o professor mandou isso aqui

**Anexo (critérios do professor, publicados na tarefa do Teams):**

> 1. Global Solution - Dynamic Programming
> Alguns esclarecimentos sobre os meus critérios de correção e dicas pra ajudar vocês a fazerem a GS. Se houver alguma dúvida venham falar comigo/mandem mensagem no Teams. Não sofram com o projeto, divirtam-se que aprende-se mais. Abs!
>
> link do arquivo: https://docs.google.com/document/d/1spdA4AGgijGbisCvbq71yNgxY0WRNY2il0SMFgo9MTg/edit?tab=t.0 
> 1.1 - Termos / lista de conceitos
> Memoização: técnica de programação dinâmica em que usamos dicionários para guardar o resultado da recursão, evitando computações repetidas.
> Tabulação: em vez de implementar a recursão de fato, usamos uma lista ou matriz para ir salvando resultados intermediários (na apostila, ver o problema 5.2, Maximização de Lucro em Confeitaria).
> Grafos: podem ser úteis em diversas aplicações. Vocês podem utilizar algoritmos vistos em aula ou outros algoritmos, que aprendam por conta.
> 1.2 - Critérios
> O algoritmo resolve uma necessidade da CitizenTech da sua equipe, a mesma das outras disciplinas. As ideias abaixo são exemplos: adaptem ao problema que vocês escolheram. Podem implementar mais de um algoritmo, ou apenas um.
> Os critérios de avaliação são
> Relação com a GS - algoritmo útil de fato - 2.5 pontos
> Implementação correta do algoritmo (se você fizer um algoritmo fora da lista de conceitos, poderá perder 100% desse critério! Fale comigo se tiver alguma inspiração) - 2.5 pontos
> Análise prática (ex: medição de tempo, implementada no código e funcionando) ou explicação teórica da eficiência do algoritmo (o algoritmo tem de fato que ser eficiente! Não basta medir um algoritmo ruim) - 2.5 pontos
> Qualidade de código (uso de funções com passagem e retorno, separação interface e funções puras, try/except, boas práticas) - 2.5 pontos
> Atenção à eficiência: numa busca em largura (ou na ordenação topológica), retirar da fila com fila.pop(0) custa O(n) a cada retirada. Usem a fila com proximo, vista em aula, ou collections.deque. No Dijkstra e no A*, usem uma fila de prioridade (heapq).
> 1.3 - Entrega
> Entregas fora do padrão ou desorganizadas podem sofrer descontos de até 25 pontos. O padrão é:
> um único arquivo ZIP, na tarefa do Teams, enviado por um integrante da equipe, até 19/11 às 23h55;
> dentro do ZIP: o código-fonte completo e o arquivo ReadMe;
> no ReadMe: a Ficha da CitizenTech no início, os RMs e nomes dos alunos, a descrição dos algoritmos abordados e das funcionalidades implementadas;
> se usaram IA, os prompts em um arquivo prompts.md;
> Se não usaram, o mesmo arquivo, afirmando que não usaram
> nada de dados pessoais reais: usem dados simulados ou públicos, e digam de onde vieram.
> 1.4 Inspiração
> Você não precisa usar as ideias abaixo. Elas só estão aqui para te inspirar. Faça uma coisa que tem a ver com o seu projeto!
> Ideias usando algoritmos já vistos
> Rota com menos baldeações - metrô/ônibus como grafo; menor número de trocas até o destino. BFS (aula do metrô). Note que a nossa implementação de sala faz a rota com menos arestas, não com menos baldeações. Dica: com as linhas como vértices, ligadas quando têm uma estação em comum, a mesma BFS dá o menor número de baldeações. https://cp-algorithms.com/graph/breadth-first-search.html
> Manchas de alagamento - grade de sensores (molhado/seco); contar e medir cada área alagada. Number of islands. https://leetcode.com/problems/number-of-islands/
> Bairro isolado - se uma rua fica indisponível, quem ainda alcança o posto de saúde? Componentes conexas por BFS. https://cp-algorithms.com/graph/search-for-connected-components.html
> Distância até a enchente - para cada casa, quantas quadras até a água. BFS com várias origens. https://leetcode.com/problems/rotting-oranges/
> Corrente de aviso - rede "quem avisa quem" (dirigida, como o tinder); em quantas rodadas o alerta chega a todos? BFS em grafo dirigido. https://leetcode.com/problems/keys-and-rooms/
> Saída de evacuação - menor caminho numa grade com bloqueios até a saída. BFS em grade. https://leetcode.com/problems/shortest-path-in-binary-matrix/
> Mutirões sem dias seguidos - escolher dias de mutirão (não consecutivos) maximizando pessoas atendidas. House robber. https://leetcode.com/problems/house-robber/
> Horta comunitária - terreno e água limitados, várias culturas, máximo de alimento produzido. Tabulação 2D (problema da confeitaria da apostila, 5.2).
> Cozinha comunitária - arroz e feijão limitados, tipos de marmita; máximo de pessoas alimentadas. Mesma tabela da confeitaria, outro objetivo.
> Ideias com algoritmos novos
> Ambulância mais rápida - ruas com tempos diferentes. Dijkstra. https://cp-algorithms.com/graph/dijkstra.html
> Rota de menor esforço para cadeirante - mapa de alturas do bairro; andando em qualquer direção, achar o caminho cujo trecho mais íngreme seja o mais suave possível. Dijkstra em grade. https://leetcode.com/problems/path-with-minimum-effort/
> Rota segura à noite - custo da rua = distância + falta de iluminação; busca guiada pelo destino. A*. https://www.redblobgames.com/pathfinding/a-star/introduction.html – Dijkstra resolve; o A*, guiado pelo destino, chega à mesma rota explorando menos ruas.
> Wi-Fi para bairros sem cobertura - ligar todos os pontos de acesso de uma comunidade com o menor total de cabo. Árvore geradora mínima (Kruskal ou Prim). https://cp-algorithms.com/graph/mst_kruskal.html
> Ordem dos documentos do benefício - etapas que dependem de outras; em que ordem fazer (e detectar dependência circular). Ordenação topológica (Kahn). https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm https://cp-algorithms.com/graph/topological-sort.html (versão por DFS) https://leetcode.com/problems/course-schedule-ii/
> Tabela de distâncias entre postos de saúde - todas as distâncias entre todos os pares. Floyd-Warshall (que também é programação dinâmica). https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html
> Orçamento de zeladoria - verba fixa, obras com custo e impacto; quais fazer. Mochila 0/1. https://www.geeksforgeeks.org/dsa/0-1-knapsack-problem-dp-10/
> Busca que perdoa erro de digitação - assistente de serviços públicos acha "carteira de trabalo". Distância de edição. https://leetcode.com/problems/edit-distance/
> Voluntários x tarefas - cada voluntário sabe fazer algumas tarefas; máximo de tarefas cobertas. Emparelhamento bipartido (Kuhn). https://cp-algorithms.com/graph/kuhn_maximum_bipartite_matching.html
> Capacidade de distribuição de água - canos com vazão máxima; quanto chega ao bairro. Fluxo máximo (Edmonds-Karp). https://cp-algorithms.com/graph/edmonds_karp.html
> Pontes críticas - quais ruas/pontes, se bloqueadas, isolam um bairro. Pontes em grafo (Tarjan). https://cp-algorithms.com/graph/bridge-searching.html

**O que a IA produziu:**

- Ficha da CitizenTech no início do README e mapa dos critérios.
- Menu interativo, tratamento de erros com `try/except` e testes de interface.
- Medição de eficiência no código: Floyd–Warshall em Python puro e em NumPy, comparado com Dijkstra usando `heapq`.
- Otimização do laço do Floyd–Warshall e compatibilidade com Python 3.8.
- Este arquivo.

---

## Prompt 4 · 07/11/2026

> A ficha precisa estar no início do `README` do repositório, conforme o briefing
>
> * Nome da CitizenTech: Pharos — Plataforma de mobilidade com informações históricas de segurança.
> * Cidade e bairro: São Paulo — SP, região do Capão Redondo, Zona Sul, dentro da Região Metropolitana de São Paulo (Grande São Paulo).
> * Território piloto: Trecho da Estrada de Itapecerica, com foco inicial nas linhas metropolitanas 001 e 002 da ARTESP. O território foi selecionado com base na disponibilidade de dados de transporte e registros históricos de ocorrências próximas ao corredor. A delimitação exata dos trechos e a existência de trajetos alternativos ainda dependem de validação técnica.
> * Cidadão beneficiado: Estudantes, trabalhadores e demais pessoas que utilizam ônibus, metrô e trem para se deslocar diariamente, especialmente em trajetos noturnos ou por regiões pouco conhecidas.
> * Problema, em uma frase: Usuários do transporte público têm dificuldade para comparar diferentes trajetos considerando, além do tempo e das baldeações, informações históricas relacionadas à segurança dos locais percorridos.
> * Como funciona: O usuário seleciona uma origem e um destino dentro da região atendida pelo protótipo. O Pharos calcula alternativas de deslocamento e apresenta informações como tempo estimado, distância de caminhada, quantidade de baldeações e registros históricos agregados de ocorrências criminais, quando os dados permitirem. A plataforma explica os critérios utilizados e permite que o próprio usuário escolha seu trajeto, sem prometer que alguma alternativa seja segura.
> * O que cada parte faz:
>    * Front-end: interface web para consultar e comparar trajetos.
>    * Java: API REST responsável por locais, conexões, consultas e informações dos percursos.
>    * Database Design: banco Oracle para armazenar locais, linhas, trechos, conexões e indicadores históricos.
>    * Data Science: análise de padrões históricos de ocorrências e desenvolvimento de modelos de regressão linear e logística.
>    * Dynamic Programming: algoritmo Python para calcular caminhos em uma rede piloto de transporte.
>    * Network Architect: simulação no Packet Tracer de uma rede de informações ao passageiro, incluindo segmentação, serviços e segurança.
>    * AR/VR: experiência 3D demonstrando alternativas de deslocamento em uma estação ou terminal.
>    * Agile: definição de personas, requisitos, casos de uso, backlog, protótipos e apresentação da solução.
> * Link do repositório: https://github.com/breno-hbs/pharos?utm_source=chatgpt.com
> * Indicador de impacto: Percentual de participantes dos testes que conseguem comparar duas alternativas e compreender corretamente as informações históricas apresentadas, incluindo suas limitações. Indicadores complementares: tempo de resposta da consulta, quantidade de trajetos válidos e avaliação da utilidade das informações pelos passageiros.
> * ODS conectados:
>    * ODS 11 — Cidades e Comunidades Sustentáveis: ampliar o acesso a informações relevantes sobre mobilidade urbana.
>    * ODS 9 — Indústria, Inovação e Infraestrutura: integrar dados públicos e tecnologias digitais para apoiar decisões de deslocamento.
>    * ODS 10 — Redução das Desigualdades: facilitar o acesso à informação para cidadãos que dependem do transporte público.
>    * ODS 16 — Paz, Justiça e Instituições Eficazes: promover a utilização transparente e responsável de informações públicas relacionadas à segurança.
>
> veja se essas informaçoes podem ajudar

**Anexos:**

- Documento de conceito do Pharos (problema, solução, viabilidade, ODS e indicadores).
- Resultado do brainstorm.
- Imagem com a tabela de integrantes (nomes e RMs).

**O que a IA produziu:**

- Ficha e integrantes no README.
- A Ficha recebeu três ajustes, para ficar coerente com a validação técnica:
  - o território passou a cobrir o entorno do Terminal Capão Redondo;
  - "distância de caminhada" passou a valer só "quando os dados permitirem";
  - o parâmetro `utm_source` foi retirado do link.
- Tabela de indicadores medidos neste módulo.

---

## Prompt 5 · 07/11/2026

> esta tudo pronto???

**O que a IA produziu:** conferência do ZIP (seções do README, pendências, ausência de dados pessoais, testes) e a lista do que ainda depende da equipe.

---

## Prompt 6 · 07/11/2026

> Implementação correta do algoritmo (se você fizer um algoritmo fora da lista de conceitos, poderá perder 100% desse critério! Fale comigo se tiver alguma inspiração) - 2.5 pontos
>
>
> pode conferir essa parte pra mim? essa é a apostila q ele passa pra gente, nao sei se ajuda

**Anexo:** `apostila_dynamic_programming_2026.pdf` (apostila da disciplina).

**O que a IA produziu:**

- Conferência do Floyd–Warshall contra a lista de conceitos e contra a referência da recorrência.
- Formulação no vocabulário da apostila: estado, decisão, transição, caso base e objetivo.
- Versões recursiva (com `medidor`) e com memoização (`memo`), conferidas contra a versão em tabela.
- Tabela do alinhamento reescrita em Python puro, com teste de força bruta.
- Exemplos `>>>` nas docstrings e nova seção na medição de eficiência.

---

## Prompt 7 · 07/11/2026

> pode marcar pra mim no notion oq foi feito ou nao?
>
>
> https://app.notion.com/p/Dynamic-Programming-23f4703dd081830199a5816753689b58

**Anexo:** captura de tela da página da tarefa no Notion da equipe.

**O que a IA produziu:**

- Seção "Entradas e saídas" no README, com um exemplo real de comando e saída.
- Marcação, no Notion da equipe (pelo navegador do usuário), de 49 dos 51 itens da lista da tarefa, com base nas evidências. Ficaram desmarcados o envio do ZIP no Teams e a confirmação do envio.
- Status da tarefa alterado para "In progress".

---

## Prompt 8 · 12/11/2026

> vamos conferir denovo, esta tudo certo o entregável???

**O que a IA produziu:**

- Conferência final do ZIP: arquivos, ausência de temporários e de dados pessoais, 49 testes em Python 3.8 e 3.13, comandos e menu.
- Reprodução da rede e das exportações a partir do GTFS original, com resultado idêntico.
- Teste da saída com a codificação usada no Windows (cp1252).
- Correção de três trechos do README e inclusão dos prompts 7 e 8.

---

## Prompt 9 · 12/11/2026

> esses sao os integrantes

**Anexo:** imagem da tabela de integrantes da equipe (nomes, RMs e e-mails).

**O que a IA produziu:** inclusão de Lucas Santana Silva (RM566261) na lista de integrantes do README e na tabela de revisão humana. Os e-mails não foram copiados.

---

## Prompt 10 · 17/11/2026

> opa, vamo conferir aqui, oq falta fazer

**O que a IA produziu:**

- Leitura do modelo oficial do banco no repositório da equipe (`database/02_ddl.sql` e `03_dml.sql`), que ainda divergia da exportação do DP (pendência 7 do documento do banco).
- Testes novos escritos antes da mudança (18 da exportação, 2 da linha de comando e 4 de reprodutibilidade), que falharam na versão antiga.
- Exportação reescrita com os nomes e colunas das tabelas oficiais, chaves estrangeiras pela chave natural e cenários com os códigos e janelas de `PH_CENARIO`. Remoção do DDL sugerido antigo.
- Municípios: tirados do nome da parada no GTFS, com 6 paradas conferidas pelo endereço; as demais ficaram `NÃO INFORMADO`, porque inferir pela vizinha errou 2 de 128 casos.
- A comparação entre Python 3.8 e 3.13 mostrou 8 alternativas com a baldeação numa parada vizinha de mesmo custo, porque o `sum()` de floats mudou no Python 3.12. Correção com `math.fsum`; depois dela, a exportação sai idêntica nas duas versões.
- 73 testes OK em Python 3.8.20 e 3.13.18.
- Conferência da amostra do DML contra a exportação: mesmos status, linhas, paradas, distâncias e baldeações; 7 tempos do DML estão arredondados ao minuto (diferença máxima de 0,5 min).
- Atualização do README, do relatório (seção 11) e deste arquivo.

---

## Revisão humana

| Integrante | O que revisou ou conferiu | Data |
|---|---|---|
| Pedro Henrique dos Santos | **[PREENCHER]** Ex.: rodou `python -m unittest discover -s tests -v` (73 OK) e o menu no próprio computador | |
| Pedro Cunha Coutinho | **[PREENCHER]** | |
| Breno Henrique Bortoloti Santos | **[PREENCHER]** | |
| Nicolas Tetsuo Kimura | **[PREENCHER]** | |
| Lucas Santana Silva | **[PREENCHER]** | |
