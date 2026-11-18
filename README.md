# PHAROS

**Plataforma de mobilidade com informações históricas de segurança.**

## Ficha da CitizenTech

**Nome da CitizenTech:** Pharos — Plataforma de mobilidade com informações históricas de segurança.

**Cidade e bairro:** São Paulo–SP, Capão Redondo, Zona Sul, na Grande São Paulo.

**Território piloto:** Entorno do Terminal Metrô Capão Redondo. Inclui o trecho paulistano da Estrada de Itapecerica (corredor das linhas metropolitanas 001 e 002 da ARTESP), a Estrada do M'Boi Mirim, a Av. Comendador Sant'Anna, a Av. Carlos Lacerda e o trecho da Av. João Paulo II em Embu das Artes. A validação técnica mostrou que as linhas 001 e 002 fazem o mesmo itinerário na Estrada de Itapecerica; trajetos realmente diferentes aparecem com as 15 linhas da ARTESP que passam pelo terminal ou pelo fim do corredor (detalhes em [`dynamic-programming/docs/RELATORIO_VALIDACAO_DP.md`](dynamic-programming/docs/RELATORIO_VALIDACAO_DP.md)).

**Cidadão beneficiado:** Estudantes, trabalhadores e demais pessoas que utilizam ônibus, metrô e trem para seus deslocamentos, especialmente em horários noturnos ou em regiões pouco conhecidas.

**Problema, em uma frase:** Usuários do transporte público têm dificuldade para comparar trajetos considerando, além do tempo e das baldeações, informações históricas de ocorrências criminais nas áreas percorridas.

**Como funciona:** O usuário seleciona uma origem e um destino dentro da região piloto. O Pharos mostra as alternativas de ônibus (até três por par), calculadas antes a partir dos horários programados da ARTESP, e permite compará-las por tempo estimado, distância percorrida, quantidade de baldeações (sempre na mesma parada) e registros históricos agregados de ocorrências criminais, quando os dados permitirem. A distância de caminhada não é calculada e o front-end implementado não exibe etapas a pé. A plataforma apresenta as fontes e limitações dessas informações, permitindo que o usuário escolha seu trajeto sem prometer que alguma alternativa seja segura.

**O que cada parte faz:**

- **Front-end:** interface web para planejar e comparar trajetos.
- **Java — Domain Driven Design:** API REST em Spring Boot para gerenciar locais, trechos, conexões, consultas e informações dos percursos.
- **Database Design:** banco Oracle para armazenar dados estruturados de transporte e indicadores históricos.
- **Data Science:** análise de registros históricos e desenvolvimento de modelos de regressão linear e logística.
- **Dynamic Programming:** algoritmo Python para calcular caminhos em uma rede piloto utilizando grafos.
- **Network Architect:** simulação no Cisco Packet Tracer de uma infraestrutura de informações ao passageiro.
- **AR/VR:** experiência 3D para demonstrar alternativas de deslocamento em um ambiente urbano ou terminal.
- **Agile:** definição de requisitos, personas, casos de uso, backlog, protótipos e apresentação da solução.

**Link do repositório:** https://github.com/breno-hbs/pharos

**Site (front-end):** https://pharos-sand.vercel.app

**API (deploy):** https://pharos-api-kaxr.onrender.com (teste rápido: `/saude`). O plano gratuito do Render dorme: a primeira chamada pode levar cerca de 1 minuto.

**Indicador de impacto:** Percentual de participantes dos testes que conseguem comparar alternativas de deslocamento e compreender corretamente as informações históricas apresentadas e suas limitações. Indicadores complementares incluem tempo de resposta das consultas, validade dos caminhos e utilidade percebida pelos participantes.

**ODS conectados:**

- **ODS 11 — Cidades e Comunidades Sustentáveis:** ampliar o acesso a informações relevantes sobre mobilidade urbana.
- **ODS 9 — Indústria, Inovação e Infraestrutura:** integrar dados públicos e tecnologias digitais para apoiar decisões de deslocamento.
- **ODS 10 — Redução das Desigualdades:** facilitar o acesso à informação para usuários dependentes do transporte público.
- **ODS 16 — Paz, Justiça e Instituições Eficazes:** promover o uso transparente e responsável de informações públicas relacionadas à segurança.

---

## Estado do projeto

Projeto acadêmico da Global Solution FIAP 2026.2, em fase final de entrega (prazo: 19/11/2026). A validação técnica do território e dos trajetos alternativos foi concluída em 06/11/2026, com o GTFS da ARTESP.

**O que está integrado:**
- **API Java** publicada no Render (https://pharos-api-kaxr.onrender.com), conectada ao Oracle da FIAP. Documentação em [`backend/java`](backend/java).
- **Front-end** (`frontend/`) consumindo a API: paradas, trajetos e registro anônimo de consultas. Como rodar e quais chamadas usa: [`frontend/README.md`](frontend/README.md).

**Simulado de propósito:** relatos comunitários, pins, confirmações e o mapa ilustrativo (a API e o banco de exemplo não têm relatos nem coordenadas). O banco de exemplo só tem trajetos calculados para o pico da manhã de dia útil.

## Como contribuir

O desenvolvimento do Pharos é organizado em branches e Pull Requests.

Antes de começar qualquer implementação, leia o [Guia de Contribuição](CONTRIBUTING.md), que contém as regras de versionamento, revisão de código, integração e segurança adotadas pela equipe.
