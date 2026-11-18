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

## Pedro Henrique dos Santos
_(adicionar os prompts)_
