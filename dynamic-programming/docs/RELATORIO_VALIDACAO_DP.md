# Pharos · Validação de trajetos alternativos e Dynamic Programming

**Tarefa 2.1 · FIAP CitizenTech · 06/11/2026**

Neste relatório, **[F]** marca um fato verificado nos arquivos, **[H]** uma hipótese ou aproximação declarada e **[R]** uma recomendação.

## 1. Conclusão objetiva

| Pergunta | Resposta |
|---|---|
| O corredor das linhas 001/002 suporta comparação real de trajetos? | **Não.** [F] Em todo o trecho paulistano da Estrada de Itapecerica, 001 e 002 têm as mesmas 13 + 15 paradas, na mesma ordem. Entre 396 e 405, oito linhas (001, 002, 193, 339, 340, 451, 484, 531) fazem o mesmo itinerário, o que equivale a **uma alternativa**. |
| Existe comparação real no entorno do piloto? | **Sim, comprovado no GTFS.** [F] Ampliando o recorte em torno do Terminal Metrô Capão Redondo (Av. João Paulo II em Embu das Artes, Av. Carlos Lacerda e Estrada do M'Boi Mirim), **18 dos 240 pares** entre os 16 pontos do MVP têm 2 ou 3 alternativas geometricamente distintas, inclusive com baldeação no terminal. |
| Floyd–Warshall é adequado? | **Sim, no recorte, como pré-cálculo.** [F] V = 237 paradas: até 13,3 milhões de relaxações, 0,12 a 0,15 s em Python puro e ~0,05 s com NumPy por critério. [F] Como o grafo é esparso (7% dos pares têm aresta), Dijkstra a partir de cada origem com `heapq` faz o mesmo cálculo em ~0,04 s, com distâncias idênticas. O Floyd–Warshall foi mantido por ser a técnica de programação dinâmica da disciplina e porque roda uma única vez, antes das consultas. No GTFS completo (25.105 paradas) seria inviável. |

## 2. Arquivos verificados

- [F] `artesp_gtfs.zip`: SHA-256 `f3fdca95…d45a`, versão 20261007. As contagens batem com o relatório 1.6: 823 rotas, 25.105 paradas, 86.724 viagens, 4.555.603 passagens, 84.852 viagens com passagens e 759 rotas utilizáveis.
- [F] **100% das 84.852 viagens** têm intervalo uniforme entre paradas, e todas as 3.702 combinações de linha, sentido e tipo de dia têm a mesma duração em qualquer horário. O horário intermediário é, portanto, a duração da viagem dividida igualmente pelo número de paradas.
- [F] São **2.402 viagens duplicadas** (mesma linha, sentido, serviço e horário de partida, quase sempre com traçados diferentes) em 22 linhas. No piloto, as linhas afetadas são 558 e 563, cujos dois traçados têm listas de partidas idênticas.
- [F] O GeoJSON do corredor tem 26 arestas, com 168, 391 e 753 BOs (100, 250 e 500 m). Como cada BO foi atribuído a uma única aresta entre os dois sentidos, os 391 BOs se dividem em 134 no sentido 0 e 257 no sentido 1.
- [F] O briefing oficial (p. 34) pede "algoritmo em Python aplicando algumas das técnicas: Memoização, Tabulação, Grafos", com "escolha coerente, funcionamento correto e noção de eficiência". O texto não nomeia um algoritmo. Floyd–Warshall cobre **Grafos + Tabulação**.
- [F] O documento de escopo v0.1 exige, como critério adicional, "pelo menos duas alternativas efetivamente distintas", ou então rever o território.

## 3. Tabela de alternativas

Cenário dia útil, 06h–09h, critério tempo. A sobreposição é a fração de um traçado que fica a até 30 m do outro.

| Origem | Destino | Alternativas (linhas equivalentes) | Diferença entre percursos | Baldeação | Evidência no GTFS |
|---|---|---|---|---|---|
| **13211** Av. João Paulo II, 1581 (Embu) | **407** Terminal Metrô Capão Redondo | A1: **551** (= 551BI1) via Estr. Pirajussara–Valo Velho, Av. Augusto Barbosa Tavares e **Av. Carlos Lacerda**, 6,00 km, 22 paradas, ~29 min · A2: **193** via Estr. Itapecerica–Campo Limpo e **Estrada de Itapecerica** (corredor piloto), 8,97 km, 32 paradas, ~44 min | 26% de sobreposição: só o início na João Paulo II e o trecho 405→407 | Não | Padrões `551_0_743`, `551BI1_0_8293`, `193_0_352`. O 193 passa por 12643 e 396–404; o 551 passa por 33608 |
| **407** Terminal | **13466** Av. João Paulo II, 1581 | A1: **551** 5,88 km, ~31 min · A2: **193** 8,99 km, ~46 min | 25% | Não | `551_1_523`, `193_1_359` |
| **32960** Estr. M'Boi Mirim, 5780B | **21657** Av. Comendador Sant'Anna, 679 | A1: **237** via R. Abílio César e R. Henrique Sam Mindlin, 2,75 km, ~16 min · A2: **513** (= 558, 563, 844) via Estr. M'Boi Mirim e Av. Comendador Sant'Anna, 3,12 km, ~16 min | **19%**. Os dois extremos ficam no município de São Paulo | Não | `237_0_419`, `513_0_8241`, `558_0_729/8227`, `563_0_593/8229`, `844_0_8243` |
| **32960** | **407** | A1: **237** 4,62 km, ~23 min · A2: **513/558/563/844** 4,98 km, ~23 min | 49%: divergem de 32960 a 21657 e seguem juntos até o terminal | Não | idem |
| **405** Estr. de Itapecerica, 4765 | **2201** Estr. M'Boi Mirim, 5790 | A1: 193 (ou outras 7 linhas) até 407 e depois **237**, 5,49 km, ~28 min · A2: idem até 407 e depois **513/558/563/844**, 5,85 km, ~32 min | 57% | **Sim, 1 baldeação no 407**, mesmo `stop_id` | Às 07h00 de dia útil: 484 07:00→07:02, depois 237 07:05→07:24 |

Os outros 13 pares com alternativas distintas estão em `saida/ph_alternativa.csv` (os pares com 2 ou 3 alternativas). Alguns deles começam no lado "sentido bairro" e vão até o fim da linha para voltar (ex.: 13466 → 407 com 193 + 193 + 551). São válidos no modelo, mas não servem para a demonstração.

## 4. Modelo de grafo

| Item | Definição |
|---|---|
| Recorte [H] | Retângulo lat −23,705 a −23,636 e lon −46,806 a −46,760. Entram todas as linhas que passam por 407, 405 ou 1443: **15 linhas, 34 padrões, 237 paradas** |
| Vértice | `stop_id` do GTFS. Cada sentido tem paradas próprias; por exemplo, 405 e 9873 ficam a 23 m, em lados opostos |
| Aresta | Embarque em u e desembarque em v na mesma viagem de **uma** linha. Grafo dirigido, com 7.775 arestas e 4.008 pares (u, v) |
| Sentido | Herdado da ordem de `stop_sequence` em cada padrão |
| Baldeação | Mudança de aresta no mesmo vértice. [F] O Terminal 407 recebe 13 linhas com o mesmo `stop_id` |
| Tempo a bordo | Soma de saltos canônicos. Cada salto entre paradas consecutivas recebe a média dos tempos programados das linhas que o percorrem, ponderada pelas viagens do dia. [H] A interpolação da ARTESP é por linha, então a diferença entre linhas no mesmo salto é artefato, não velocidade |
| Distância | Soma de saltos canônicos medidos no traçado. As paradas são projetadas no `shapes.txt` por alinhamento monotônico (tabulação). [F] Todas as paradas do recorte ficam a menos de 50 m do traçado, sem nenhuma inversão de ordem. [F] O acesso ao terminal (405→407) varia de 723 a 999 m conforme a linha; o valor canônico é 861 m. [F] Conferência independente direto no `shapes.txt`, pelo vértice mais próximo: 551 dá 5,88 km e 193 dá 9,03 km de 13211 a 407, contra 6,00 e 8,97 km no modelo (diferença de até 2%) |
| Espera | [H] (janela ÷ partidas da linha em u) ÷ 2. Linha sem partida na janela não entra no grafo |
| Dados ausentes | Sem `shape_dist_traveled`, distância calculada pelo traçado. Sem `calendar_dates`, feriado recebe o padrão WD. Sem rede de pedestres, nenhuma caminhada é modelada |

## 5. Prova de conceito

Código em `pharos/`, linha de comando em `main.py` e instruções no `README.md`. O Floyd–Warshall tem versão em Python puro, que é a padrão e a avaliada, e versão NumPy com a mesma recorrência. As duas produzem tabelas **idênticas** (verificado em teste). `python main.py desempenho` mede as duas e Dijkstra × V na mesma matriz, e mostra o crescimento em subgrafos de 30 a 237 vértices. Sem argumentos, `python main.py` abre um menu interativo.

Complexidade:

- **Tempo:** Θ(V³) por critério.
- **Memória:** Θ(V²) para D e Θ(V²) para NXT.
- **Pré-cálculo dos três critérios:** 3 × 13,3 milhões de relaxações.
- **Consulta de alternativas:** O(arestas em o + arestas em d) acessos à tabela, mais a comparação geométrica das candidatas.

## 6. Resultados dos testes

`python -m unittest discover -s tests -v` executou **73 testes, todos OK, em ~8–11 s**, em Python 3.8.20 e em Python 3.13.18 (reexecutado em 17/11/2026, depois de alinhar a exportação ao banco; na versão de 06/11 eram 49).

| Tipo | Caso | Resultado observado |
|---|---|---|
| Algoritmo | Grafo de 5 vértices resolvido à mão | A→E = 7 pelo caminho A-C-B-D-E; C→D = 3, que vence a aresta direta de custo 5 |
| Algoritmo | 40 grafos aleatórios | Python = NumPy = Dijkstra (oráculo independente) |
| Algoritmo | Entrada inválida | Peso negativo, diagonal ≠ 0 e matriz não quadrada levantam `ValueError` |
| Rede | Ótimos válidos | **0 de 30.002** pares alcançáveis, nos três critérios, com baldeação inútil ou laço |
| Rede | 13211→407, 407→13466, 32960→407, 405→2201 | Alternativas e linhas da tabela acima. Cada trecho é subsequência contígua de um padrão real |
| Critérios | 1325→407 | Tempo escolhe **513** (6,04 km); distância e embarques escolhem **237** (5,68 km); os tempos ficam a menos de 1 min de diferença |
| Critérios | 1325→744 | Tempo: 513 + 193, 64,3 min, 13,32 km. Distância: 237 + 484 + 193, **71,5 min, 12,91 km**. O critério puro de distância aceita +1 baldeação e +7 min para economizar ~400 m |
| Cenário | 13211→407 no pico da tarde | 551BI1 some, porque só opera de manhã nesse sentido |
| Cenário | 13211→407 no domingo, 08h00 | 551 sai às 08:21 e 193 às 08:02; **os dois chegam às 08:45** |
| Sem caminho | 407→393, 407→32960 | `SEM_TRAJETO`: os ônibus que passam nessas paradas vêm de fora do recorte |
| Sem caminho razoável | 32960→2201 (lados opostos da via, 37 m) | `SEM_TRAJETO_RAZOAVEL`: o único caminho é ir ao terminal e voltar (9,2 km, desvio de 252×) |
| Sem caminho | Parada 99999 | `KeyError` com mensagem |
| Horário | 193 a partir de 23:59 | Inviável: não há mais partidas em 13211 |

Na rede inteira, 30.002 dos 55.932 pares ordenados (53,6%) têm caminho. Os demais dependem de atravessar a rua, de sair do recorte ou de ir contra o sentido sem uma linha que retorne dentro do piloto.

## 7. Arquitetura recomendada (Python → Oracle → Java)

| Critério | Opção 1: pré-processamento | Opção 2: Python sob demanda |
|---|---|---|
| Complexidade | Baixa: o Python gera CSV, que é carregado no Oracle | Média e alta: dois serviços, contrato HTTP, timeouts |
| Dependências da API Java | Só Oracle | Oracle + serviço Python no ar |
| Deploy | Só a API no Render | API + serviço Python. No plano gratuito do Render os serviços podem hibernar, e a primeira chamada fica lenta |
| Manutenção | Reexportar quando mudar GTFS ou parâmetro | Dois códigos em produção |
| Prazo 19/11 | Viável | Arriscado |
| Volume | 5 cenários × 240 pares: 1.200 pares, 508 alternativas, 875 etapas, 9.286 linhas de sequência | |

**[R] Opção 1.** O algoritmo roda **antes**, uma vez por cenário (`python main.py exportar`). A API Java só lê as tabelas do modelo oficial (`database/02_ddl.sql` do repositório): `ph_par_origem_destino`, `ph_alternativa`, `ph_etapa_trajeto`, `ph_parada`, `ph_linha` e `ph_cenario`. A exportação gera um CSV para cada uma, com as mesmas colunas (seção 11). Quando não houver trajeto, a API devolve o status gravado em `ph_par_origem_destino`, sem inventar resultado. A entrega de DP continua independente: ZIP com o código, a CLI e os testes, que rodam sem Oracle.

## 8. Funcionalidades do MVP

| Funcionalidade | Classificação | Condição |
|---|---|---|
| Seleção de origem e destino | **Viável com restrições** | Só entre os 16 pontos cadastrados, que dependem do sentido. Oferecer só destinos com trajeto: 83 dos 240 pares por cenário |
| Comparação de trajetos diferentes | **Viável com restrições** | Exige ampliar o território. Usar 13211↔407, 32960→21657, 32960→407 e 405→2201 na demonstração |
| Tempo programado | **Viável com restrições** | Rotular como "tempo programado estimado pela ARTESP (GTFS 2026)" e "espera estimada". Não reflete trânsito nem horário de pico |
| Distância de caminhada | **Dependente de fonte adicional** | Requer rede de pedestres (ex.: OpenStreetMap). [R] Retirar do MVP e exibir "baldeação na mesma parada" |
| Quantidade de baldeações | **Viável com os dados atuais** | Baldeação só na mesma parada |
| Sequência de paradas | **Viável com os dados atuais** | Nomes do `stops.txt`; ordem do `stop_times.txt` |
| Escolha de critério | **Viável com restrições** | Os três critérios existem, mas mudam pouco o resultado em viagens diretas. [R] Mostrar tempo, distância e baldeações lado a lado e deixar o usuário ordenar, sem chamar nenhuma opção de "melhor" |
| Indicadores de ocorrências por alternativa | **Dependente de recálculo** | O GeoJSON atual cobre só o corredor: 10 dos 31 saltos do 193 e nenhum do 551 na ida. Na volta, o 551 toca uma única aresta, 1443→9873, com 85 BOs. Somar arestas geraria uma comparação "85 × 191" sem base metodológica |

## 9. Riscos e pendências

1. **Decisão da equipe:** mudar o território de "Estrada de Itapecerica" para "entorno do Terminal Metrô Capão Redondo (Embu das Artes – Capão Redondo – M'Boi Mirim)". Isso afeta a Ficha CitizenTech, as personas, os protótipos, o pitch e o AR/VR.
2. **Indicador SSP:** recalcular por alternativa, com BOs únicos a até 250 m do traçado completo. Parte do 193 e a origem 13211 ficam em Embu das Artes, e é preciso confirmar se a planilha da SSP cobre esse município. Os boletins são de 2025 e o GTFS é de 2026, o que continua sendo uma diferença de ano.
3. **Espera:** a ordem entre 237 e 513 em 32960→407 (22,7 × 23,0 min) depende da hipótese de espera. Apresentar como estimativa.
4. **Limiares declarados:** sobreposição de 80%, até 2 baldeações e desvio de até 3×. A equipe precisa saber justificá-los na defesa.
5. **Oracle da FIAP:** o DDL e o DML do banco rodaram lá em 16/11. A carga dos CSVs da exportação ainda não foi testada no Oracle; a amostra do DML foi conferida contra a exportação (seção 11).
6. **`prompts.md`:** registrar a revisão humana nos campos `[PREENCHER]`.

## 10. Resumo para o Notion (tarefa 2.1)

> **Validação DP / trajetos, 06/11/2026.** O GTFS ARTESP 20261007 (SHA-256 f3fdca95…d45a) foi conferido. O corredor 001/002 da Estrada de Itapecerica é **um único itinerário**: 8 linhas nas mesmas paradas, sem alternativa real. No entorno do Terminal Metrô Capão Redondo, a comparação é **comprovada**: 13211 (Av. João Paulo II, Embu) → 407 (Terminal) tem 551 via Av. Carlos Lacerda (6,0 km, ~29 min) e 193 via Estrada de Itapecerica (9,0 km, ~44 min), com 26% de sobreposição; 32960 (M'Boi Mirim) → 21657 (Av. Comendador Sant'Anna) tem 237 e 513/558/563/844, com 19% de sobreposição; 405 → 2201 tem baldeação real no Terminal 407. Floyd–Warshall em Python sobre 237 paradas, 7.775 arestas e 3 critérios (tempo, distância, embarques) roda em até 0,15 s por critério em Python puro (Dijkstra × V com heapq dá o mesmo resultado em ~0,04 s); versões recursiva, memoizada e em tabela conferidas entre si; 49 testes OK em Python 3.8 e 3.13. Achados: os horários intermediários do GTFS são 100% interpolados de forma uniforme e as durações não variam ao longo do dia; há 2.402 viagens duplicadas no feed (558 e 563 no piloto). Decisão recomendada: pré-processar em Python, carregar CSV no Oracle e a API Java só consulta. Pendências: aprovar a ampliação do território, recalcular o indicador SSP por alternativa e retirar a distância de caminhada do MVP.

## 11. Atualização de 17/11/2026: exportação no formato do banco

**O que mudou.** O exportador passou a gravar um CSV por tabela do modelo oficial (`database/02_ddl.sql`), com os nomes de colunas do DDL: `ph_cenario`, `ph_parada`, `ph_linha`, `ph_par_origem_destino`, `ph_alternativa` e `ph_etapa_trajeto`. As chaves substitutas (IDENTITY) não vão nos arquivos; as estrangeiras saem pela chave natural (`cd_cenario`, `cd_parada_gtfs`, `cd_linha`, `nm_fonte`). Os cenários do Python passaram a usar os códigos e as janelas de `PH_CENARIO` (`UTIL_MANHA`, `UTIL_TARDE`, `UTIL_NOITE`, `SABADO_MANHA`, `DOMINGO_MANHA`). O DDL sugerido antigo (`ddl_oracle_sugerido.sql`) foi removido, porque contradizia o modelo oficial.

**Conversões.** `ALTERNATIVAS_DISTINTAS` e `TRAJETO_UNICO` → `COM_ALTERNATIVAS`; tempo em minutos com 1 casa (`NUMBER(5,1)`); distância em km com 2 casas (`NUMBER(6,2)`); município pelo nome da parada no GTFS, por 6 paradas conferidas pelo endereço (`config.py`) ou `NÃO INFORMADO` (6 paradas da Estrada de Itapecerica acima do nº 6555). [F] Inferir pela parada vizinha errou 2 de 128 casos numa validação cruzada, na divisa São Paulo/Embu das Artes, por isso não foi usado.

**Testes.** 24 testes novos: 18 da exportação, 2 da linha de comando e 4 de reprodutibilidade. Os da exportação conferem cabeçalhos, CHECKs, unicidade das chaves naturais, integridade referencial entre os arquivos, encadeamento das etapas (origem → baldeações na mesma parada → destino) e os cenários do DML. Total: 73 testes OK em Python 3.8.20 e 3.13.18.

**Reprodutibilidade.** [F] A primeira comparação entre as exportações feitas em Python 3.8 e 3.13 mostrou 8 das 508 alternativas (sábado e domingo, com 3 embarques) com a baldeação numa parada vizinha de mesmo custo; por exemplo, 13211 → 1454 baldeando em 1443 numa versão e em 1444 na outra. [F] Causa: o `sum()` de floats passou a usar soma compensada no Python 3.12 (`sum([0.1] * 10)` dá 1.0 no 3.13 e 0.9999999999999999 no 3.8), e esse último bit decidia o empate. Correção: `math.fsum` no custo das alternativas e na média dos saltos. [F] Depois dela, a exportação sai idêntica byte a byte nas duas versões. Em relação à exportação anterior em 3.13, as tabelas `ph_*` não mudaram; só a coluna `geradores` de 10 linhas do detalhe.

**Conferência com o DML do banco (amostra de 7 pares, 10 alternativas e 12 etapas).** [F] Os 7 pares têm o mesmo status; as 10 alternativas têm a mesma ordem, as mesmas linhas e paradas de embarque e desembarque, a mesma distância e o mesmo número de baldeações. [F] Os municípios das 7 paradas coincidem. A única diferença é o tempo em 7 alternativas: o DML tem valores arredondados ao minuto, os mesmos aproximados da tabela da seção 3 (~29, ~44 min etc.).

| Par (UTIL_MANHA) | Ordem | DML (min) | Exportação (min) |
|---|---|---|---|
| 13211 → 407 | 1 | 29,0 | 29,4 |
| 13211 → 407 | 2 | 44,0 | 44,1 |
| 407 → 13466 | 1 | 31,0 | 30,7 |
| 407 → 13466 | 2 | 46,0 | 45,7 |
| 32960 → 21657 | 2 | 16,0 | 16,2 |
| 405 → 2201 | 1 | 28,0 | 27,9 |
| 405 → 2201 | 2 | 32,0 | 31,5 |

As outras 3 alternativas (32960 → 21657 ordem 1; 32960 → 407 ordens 1 e 2) são iguais. [R] Trocar esses 7 valores no `03_dml.sql` deixa banco e DP idênticos; a diferença máxima é de 0,5 min.

