# PHAROS

**Plataforma de mobilidade com informações históricas de segurança.**

## Ficha da CitizenTech

**Nome da CitizenTech:** Pharos — Plataforma de mobilidade com informações históricas de segurança.

**Cidade e bairro:** São Paulo–SP, Capão Redondo, Zona Sul, na Grande São Paulo.

**Território piloto:** Trecho da Estrada de Itapecerica, com foco preliminar nas linhas metropolitanas 001 e 002 da ARTESP. A delimitação do trecho e a existência de trajetos alternativos ainda dependem de validação técnica.

**Cidadão beneficiado:** Estudantes, trabalhadores e demais pessoas que utilizam ônibus, metrô e trem para seus deslocamentos, especialmente em horários noturnos ou em regiões pouco conhecidas.

**Problema, em uma frase:** Usuários do transporte público têm dificuldade para comparar trajetos considerando, além do tempo e das baldeações, informações históricas de ocorrências criminais nas áreas percorridas.

**Como funciona:** O usuário seleciona uma origem e um destino dentro da região piloto. O Pharos calcula alternativas de deslocamento e permite compará-las considerando tempo estimado, distância de caminhada, quantidade de baldeações e registros históricos agregados de ocorrências criminais, quando os dados permitirem. A plataforma apresenta as fontes e limitações dessas informações, permitindo que o usuário escolha seu trajeto sem prometer que alguma alternativa seja segura.

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

**Indicador de impacto:** Percentual de participantes dos testes que conseguem comparar alternativas de deslocamento e compreender corretamente as informações históricas apresentadas e suas limitações. Indicadores complementares incluem tempo de resposta das consultas, validade dos caminhos e utilidade percebida pelos participantes.

**ODS conectados:**

- **ODS 11 — Cidades e Comunidades Sustentáveis:** ampliar o acesso a informações relevantes sobre mobilidade urbana.
- **ODS 9 — Indústria, Inovação e Infraestrutura:** integrar dados públicos e tecnologias digitais para apoiar decisões de deslocamento.
- **ODS 10 — Redução das Desigualdades:** facilitar o acesso à informação para usuários dependentes do transporte público.
- **ODS 16 — Paz, Justiça e Instituições Eficazes:** promover o uso transparente e responsável de informações públicas relacionadas à segurança.

---

## Estado do projeto

Projeto acadêmico da Global Solution FIAP 2026.2, em fase de definição e validação técnica.

**Pendências atuais:**
- Validar a delimitação do trecho da Estrada de Itapecerica e verificar se há trajetos alternativos.
- Validar a granularidade e a qualidade dos dados da SSP-SP.
- Confirmar as conexões de transporte do MVP.
- Consolidar a arquitetura e os contratos de integração.

**Prazo de entrega:** 19/11/2026.

## Como contribuir

O desenvolvimento do Pharos é organizado em branches e Pull Requests.

Antes de começar qualquer implementação, leia o [Guia de Contribuição](CONTRIBUTING.md), que contém as regras de versionamento, revisão de código, integração e segurança adotadas pela equipe.
