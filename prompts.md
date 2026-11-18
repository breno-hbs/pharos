# Prompts

Registro dos prompts de IA usados no PHAROS, como pede a guia da Global Solution: IA como copiloto, para aprender e revisar. Cada integrante deve saber explicar cada linha do que usou.

**Como ler:** cada item tem o objetivo, o pedido feito (resumido), o que a IA devolveu e **como a equipe validou** o resultado. Nenhum prompt contém dados pessoais reais; os dados de exemplo são simulados ou públicos (SSP-SP, GTFS da ARTESP).

> Os prompts deste arquivo foram escritos por **Breno** (API Java, integração front↔API, Network Architect, documentação e vídeo). Cada integrante acrescenta os seus abaixo, em uma seção própria.

## Breno · API Java, integração, rede, documentação e vídeo

### 1. Integração do front com a API Java
- **Objetivo:** ligar o front em Next.js (feito por um colega) à API Spring Boot publicada no Render.
- **Pedido:** verificar como estava o front e integrá-lo ao back-end, trocando os dados fixos por chamadas reais (`GET /paradas`, `GET /trajetos`, `POST/PUT /consultas`) e tratando carregamento, erro e "sem dados".
- **Resultado:** cliente da API (`frontend/app/api.ts`, `use-api.ts`) e telas ajustadas; PR #18.
- **Como validamos:** rodamos o front contra a API real no Render e conferimos no navegador as rotas 551 e 193, o `POST /consultas` (201) e o `PUT` (200). Dois erros reais apareceram e foram corrigidos: `selecionavel` aceita só `S` ou `N`, e o par inicial não tinha trajeto no banco de exemplo.
- **Decisão nossa:** a API não calcula caminhada, então "Menos caminhada" virou "Menor distância".

### 2. Revisão do repositório contra o checklist da GS
- **Objetivo:** conferir código, documentação e repositório com o que a entrega pede.
- **Pedido:** revisar o repositório e a documentação contra o checklist do documento da GS.
- **Resultado:** lista de acertos e correções. Achados: "22 rotas" na documentação (o código tem 20), texto de protótipos desatualizado, README da raiz com pendências antigas.
- **Como validamos:** contamos as rotas nos controllers e na tabela do PDF; varremos o repositório atrás de credenciais (nenhuma encontrada).

### 3. Documentação em PDF
- **Objetivo:** corrigir a contagem de rotas e acrescentar a seção 10 com o front integrado.
- **Pedido:** fazer as correções e trocar/acrescentar as telas com a versão real do front.
- **Resultado:** `documentacao.pdf` com 23 páginas; as telas do Figma foram mantidas porque o checklist pede os protótipos.
- **Como validamos:** conferimos página a página (texto e numeração) depois da edição.

### 4. Network Architect (Packet Tracer)
- **Objetivo:** documentar a rede da CitizenTech (VLANs, DHCP, NAT/PAT, DNS, HTTP, segurança).
- **Pedido:** estruturar o relatório em PDF e a Ficha da CitizenTech a partir da topologia feita no Packet Tracer.
- **Como validamos:** testes no próprio Packet Tracer (ping entre VLANs, DNS, página HTTP da Ficha) e prints no PDF.

### 5. Vídeo pitch
- **Objetivo:** roteiro e montagem do vídeo de até 3 minutos.
- **Pedido:** roteiro cobrindo problema, cidadãos beneficiados, solução, telas e benefício esperado.
- **Como validamos:** revisão em grupo antes de publicar; números do pitch conferidos nas fontes (SSP-SP, instituições citadas).

### 6. Diagrama de casos de uso (ajuste)
- **Objetivo:** alinhar o diagrama 3.4 ao que a API faz.
- **Pedido:** trocar "caminhada" por "distância" no UC04 e retirar o rodapé "pendente".
- **Como validamos:** comparação com a Ficha e com o front.

## Lucas Santana Silva
_(adicionar os prompts)_

## Nicolas Tetsuo Kimura
_(adicionar os prompts)_

## Pedro Cunha Coutinho
_(adicionar os prompts)_

## Pedro Henrique dos Santos · Database Design e Dynamic Programming

Ferramenta: Claude (Anthropic), de 06/11 a 18/11/2026. Os prompts do DP estão na íntegra em `dynamic-programming/prompts.md`.

### 1. Modelo de dados
- **Objetivo:** modelar o banco Oracle do Pharos a partir do escopo do MVP e do resultado do módulo de Dynamic Programming.
- **Pedido:** propor o modelo lógico-relacional (tabelas, atributos, PKs, FKs e cardinalidades), coerente com a API Java e com o cálculo de trajetos.
- **Resultado:** a primeira proposta, de 07/11, tinha trechos de caminhada, área e consulta de trajeto e foi descartada. A versão final tem 10 tabelas com prefixo `PH_`, 10 PKs, 9 UKs, 16 FKs e 28 CHECKs.
- **Decisão nossa:** o cálculo de trajetos roda antes, em Python, e o banco guarda só o resultado; as ocorrências ficam apenas agregadas, sem boletim individual nem dado pessoal.

### 2. Scripts DDL, DML e DQL
- **Objetivo:** implementar fisicamente o modelo no Oracle da FIAP.
- **Pedido:** gerar `02_ddl.sql`, `03_dml.sql` (no mínimo 5 linhas por tabela) e `04_dql.sql` com as três consultas do briefing.
- **Resultado:** os três scripts, testados antes em PostgreSQL 16 e no parser do dialeto Oracle. `PH_FONTE_DADOS` tem 4 linhas, com a exceção justificada no próprio script; os indicadores de ocorrência e as consultas de exemplo são simulados e identificados como tal.
- **Como validamos:** rodamos os três scripts no Oracle da FIAP (SQL Developer, F5) em 16/11. O dicionário de dados mostrou 10 tabelas e as restrições P=10, U=9, R=16 e C=28; as contagens e as três consultas deram o resultado esperado.

### 3. Diagramas no Oracle Data Modeler
- **Objetivo:** ter o diagrama do modelo lógico feito no Oracle Data Modeler, como pede o briefing.
- **Pedido:** importar o DDL no Data Modeler e gerar os modelos lógico e relacional.
- **Resultado:** 49 dos 50 comandos importados (só o bloco PL/SQL de limpeza não é reconhecido, o que é esperado) e os dois diagramas.
- **Como validamos:** conferimos nos diagramas as 10 tabelas e os 16 relacionamentos.

### 4. Documentação do banco em PDF
- **Objetivo:** montar o PDF com capa, sumário, objetivo, escopo, funcionalidades e diagramas.
- **Pedido:** gerar a documentação a partir do modelo e dos scripts, com a execução no Oracle registrada.
- **Resultado:** `database/01_documentacao_modelo.pdf`, com 11 páginas.
- **Como validamos:** os quatro arquivos de entrega foram conferidos por SHA-256: são iguais no computador do Pedro e no GitHub.

### 5. Coerência entre banco, API e DP
- **Objetivo:** garantir que o banco representa o que a API usa e o que o DP calcula.
- **Pedido:** conferir os DAOs do `backend/java` contra o DDL e a amostra do DML contra a exportação do DP.
- **Resultado:** os DAOs usam só tabelas e colunas que existem no DDL. A amostra do DML bate com a exportação do DP em status, linhas, paradas, distâncias e baldeações; os tempos do DML estão arredondados ao minuto (diferença máxima de 0,5 min).

### 6. Dynamic Programming: trajetos com Floyd–Warshall
- **Objetivo:** verificar se o território piloto tem trajetos realmente diferentes e implementar o algoritmo da disciplina.
- **Pedido:** analisar o GTFS da ARTESP, montar o grafo da rede piloto e implementar o Floyd–Warshall com testes, medição de eficiência e exportação para o banco.
- **Resultado:** o módulo `dynamic-programming/` (Floyd–Warshall nas versões recursiva, memoizada e em tabela, 73 testes e exportação no formato das tabelas do banco) e o relatório de validação. A análise mostrou que as linhas 001 e 002 fazem o mesmo itinerário, e o território passou a ser o entorno do Terminal Capão Redondo.
- **Como validamos:** rodamos os 73 testes e o menu no Windows (Python 3.14.5); a consulta 13211 → 407 conferiu com o relatório de validação.
