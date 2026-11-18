# Pharos · Dynamic Programming

**Global Solution 2026.2 · FIAP · CitizenTech · Engenharia de Software**

## Ficha da CitizenTech

| Campo | Conteúdo |
|---|---|
| **Nome da CitizenTech** | **Pharos**: plataforma de mobilidade com informações históricas de segurança |
| **Cidade e bairro** | São Paulo (SP), região do Capão Redondo, Zona Sul, na Região Metropolitana de São Paulo |
| **Território piloto** | Entorno do Terminal Metrô Capão Redondo. Inclui o trecho paulistano da Estrada de Itapecerica (corredor das linhas metropolitanas 001 e 002 da ARTESP), a Estrada do M'Boi Mirim, a Av. Comendador Sant'Anna, a Av. Carlos Lacerda e o trecho da Av. João Paulo II em Embu das Artes. A validação técnica mostrou que as linhas 001 e 002 fazem o mesmo itinerário na Estrada de Itapecerica. Trajetos efetivamente diferentes aparecem quando se consideram as 15 linhas da ARTESP que passam pelo terminal ou pelo fim do corredor, nas paradas 407, 405 e 1443 (detalhes em `docs/RELATORIO_VALIDACAO_DP.md`) |
| **Cidadão beneficiado** | Estudantes, trabalhadores e demais pessoas que usam ônibus, metrô e trem no dia a dia, especialmente em trajetos noturnos ou por regiões pouco conhecidas |
| **Problema, em uma frase** | Usuários do transporte público têm dificuldade para comparar trajetos considerando, além do tempo e das baldeações, informações históricas relacionadas à segurança dos locais percorridos |
| **Como funciona** | O usuário seleciona origem e destino dentro da região piloto. O Pharos mostra até três alternativas de ônibus, calculadas antes a partir dos horários programados da ARTESP, e permite compará-las por tempo estimado, distância percorrida, quantidade de baldeações (sempre na mesma parada) e registros históricos agregados de ocorrências criminais, quando os dados permitirem. A distância de caminhada não é calculada; no protótipo, as etapas a pé são apenas simuladas na interface. A plataforma explica os critérios e as limitações, e o próprio usuário escolhe o trajeto. Nenhuma alternativa é apresentada como segura |
| **O que cada parte faz** | **Front-end:** interface web para consultar e comparar trajetos. **Java:** API REST para locais, conexões, consultas e informações dos percursos. **Database Design:** banco Oracle com paradas, linhas, cenários, pares origem-destino, alternativas, etapas e indicadores históricos. **Data Science:** análise de padrões históricos de ocorrências, com regressão linear e logística. **Dynamic Programming (este módulo):** algoritmo Python (Floyd–Warshall) que calcula as alternativas de trajeto na rede piloto da ARTESP e exporta os resultados para o Oracle. **Network Architect:** rede de informações ao passageiro no Packet Tracer, com segmentação, serviços e segurança. **AR/VR:** experiência 3D com alternativas de deslocamento em uma estação ou terminal. **Agile:** personas, requisitos, casos de uso, backlog, protótipos e apresentação |
| **Link do repositório** | https://github.com/breno-hbs/pharos |
| **Indicador de impacto** | Percentual de participantes dos testes que conseguem comparar duas alternativas e entender corretamente as informações históricas apresentadas, inclusive suas limitações. Complementares: tempo de resposta da consulta, quantidade de trajetos válidos e utilidade percebida pelos passageiros |
| **ODS conectados** | **ODS 11** (Cidades e Comunidades Sustentáveis): acesso a informações relevantes sobre mobilidade urbana. **ODS 9** (Indústria, Inovação e Infraestrutura): dados públicos e tecnologia digital para apoiar decisões de deslocamento. **ODS 10** (Redução das Desigualdades): acesso à informação para quem depende do transporte público. **ODS 16** (Paz, Justiça e Instituições Eficazes): uso transparente e responsável de informações públicas de segurança |

## Integrantes

| Nome completo | RM |
|---|---|
| Pedro Henrique dos Santos | RM564188 |
| Pedro Cunha Coutinho | RM562191 |
| Breno Henrique Bortoloti Santos | RM562856 |
| Nicolas Tetsuo Kimura | RM565377 |
| Lucas Santana Silva | RM566261 |

## O que este módulo resolve

O Pharos precisa mostrar ao cidadão **duas ou mais formas reais** de ir de um ponto a outro de ônibus. Este módulo calcula, sobre a rede real da ARTESP, os caminhos mínimos entre **todos os pares de paradas** do piloto com **Floyd–Warshall**. A partir das tabelas resultantes, monta até três alternativas efetivamente diferentes para cada origem e destino, com tempo programado, distância, baldeações e sequência de paradas.

Exemplo real (dia útil, 06h–09h), de 13211 (Av. João Paulo II, Embu das Artes) até 407 (Terminal Metrô Capão Redondo):

| Alternativa | Percurso | Distância | Paradas | Tempo |
|---|---|---|---|---|
| Linha **551** (ou 551BI1) | Av. Carlos Lacerda | 6,0 km | 22 | ~29 min |
| Linha **193** | Estrada de Itapecerica | 9,0 km | 32 | ~44 min |

As duas alternativas compartilham só 26% do traçado.

**Escopo deste módulo.** São apenas ônibus metropolitanos da ARTESP (GTFS público). Metrô, trem e linhas municipais da SPTrans não entram no grafo. Também não há trechos a pé: os dados não trazem rede de pedestres, então as baldeações acontecem na mesma parada. Por isso, a "distância de caminhada" prevista no conceito foi trocada por **distância percorrida no ônibus** e **número de embarques**. A função de custo experimental com indicador histórico de ocorrências **não foi implementada**. O indicador atual cobre só o corredor das linhas 001/002 e precisa ser recalculado para cada alternativa antes de entrar no custo.

### Indicadores do Pharos medidos neste módulo

| Indicador (da Ficha) | Resultado medido |
|---|---|
| Quantidade de trajetos válidos | Entre os 16 pontos do MVP (240 pares, dia útil 06h–09h): **83 pares com trajeto**, dos quais **18 têm 2 ou 3 alternativas distintas** |
| Validade dos caminhos | **100%**: nenhum dos 30.002 caminhos mínimos tem conexão inexistente, baldeação inútil ou laço (teste `test_otimos_sao_validos`), e cada trecho existe no GTFS |
| Tempo de resposta | Pré-cálculo do Floyd–Warshall: até ~0,15 s por critério. Consulta de alternativas de um par: 0,03 a 0,22 s |

## Algoritmos e técnicas

Os três conceitos da disciplina aparecem no código:

| Conceito | Onde | Arquivo |
|---|---|---|
| **Grafos** | Rede de ônibus como grafo dirigido: paradas são vértices e viagens são arestas | `pharos/grafo.py` |
| **Tabulação** | **Floyd–Warshall** bottom-up: uma matriz guarda os resultados intermediários. É a versão usada pelo Pharos | `pharos/floyd_warshall.py` |
| **Tabulação** | Alinhamento das paradas ao traçado do ônibus, que mede a distância percorrida (o GTFS não traz `shape_dist_traveled`). Mesmo formato do problema 5.2 da apostila | `pharos/alinhamento.py` |
| **Memoização** | Floyd–Warshall top-down, recursivo, com um dicionário `memo`. Serve para mostrar de onde vem a tabela e para conferir que a versão bottom-up dá o mesmo resultado | `pharos/floyd_warshall.py` |

O Floyd–Warshall está na lista de inspiração da disciplina ("tabela de distâncias entre todos os pares").

### Floyd–Warshall como programação dinâmica

| Elemento | No Pharos |
|---|---|
| **Estado** | `d(i, j, k)`: menor custo da parada `i` até a parada `j` usando só os vértices `0..k-1` como intermediários |
| **Decisão** | Passar ou não pelo vértice `k-1` |
| **Transição** | `d(i, j, k) = min( d(i, j, k-1),  d(i, k-1, k-1) + d(k-1, j, k-1) )` |
| **Caso base** | `d(i, j, 0) = W[i][j]`: custo da aresta direta, 0 se `i = j`, infinito se não há aresta |
| **Objetivo** | `d(i, j, V)` para todos os pares, com o caminho reconstruído pela tabela `NXT` |

Seguimos a mesma sequência vista em aula com as escadas e o ladrão de casas (House Robber), e **as três versões dão exatamente as mesmas distâncias** (conferido nos testes):

1. **Recursão pura** (`dist_recursiva`): cada chamada abre outras três, e o `medidor` mostra o mesmo subproblema calculado várias vezes. Com 8 vértices já são 629.824 chamadas.
2. **Recursão + memoização** (`floyd_warshall_memo`): o dicionário `memo` faz cada estado ser calculado uma vez só. Em compensação, guarda V²·(V+1) estados (memória Θ(V³)).
3. **Tabela bottom-up** (`floyd_warshall`): a camada `k` só depende da camada `k-1`, e a linha e a coluna `k` não mudam nela. Por isso **uma única matriz V × V** é atualizada no lugar, como na FASE 7 da apostila ("a mesma resposta com pouca memória"). A reconstrução do caminho usa `NXT[i][j]`, o próximo vértice depois de `i`; quando `k` melhora o par, `NXT[i][j] = NXT[i][k]`.

Uma otimização: só relaxamos `(i, j)` quando `i` alcança `k` e `k` alcança `j`, porque com um termo infinito a soma nunca melhora o valor. Os resultados continuam idênticos, e o tempo em Python puro caiu pela metade.

### Alinhamento parada → traçado (tabulação)

- **Estado:** `M[i][j]` é a menor soma de distâncias para projetar as paradas `0..i`, com a parada `i` no segmento `j`.
- **Transição:** `M[i][j] = dist(parada i, segmento j) + min( M[i-1][0..j] )`. Esse mínimo é carregado enquanto `j` avança, então cada célula custa O(1).
- **Reconstrução:** a tabela `escolha` mostra em que segmento ficou cada parada.
- **Para que serve:** garante que as paradas sigam a ordem da viagem, mesmo quando o traçado passa duas vezes perto do mesmo ponto (laço no terminal).
- **Verificação:** o teste `test_tabela_igual_forca_bruta` compara o resultado com todas as combinações possíveis em 60 casos aleatórios.

### Modelo de grafo

| Elemento | Representa |
|---|---|
| Vértice | Parada física do GTFS (`stop_id`). São **237 paradas** no recorte. Cada sentido da via tem a sua |
| Aresta u→v | Uma viagem em **uma linha**: embarca em `u` e desce em `v`, mais adiante na mesma linha e sentido. Grafo dirigido com **7.775 arestas** |
| Baldeação | Trocar de aresta num vértice, ou seja, descer de uma linha e subir em outra **na mesma parada** |
| Peso `tempo` | Espera estimada (intervalo da linha ÷ 2) + tempo a bordo programado pela ARTESP |
| Peso `distancia` | Extensão percorrida no traçado GTFS |
| Peso `embarques` | 1 por aresta |

Como **cada aresta é um embarque**, o critério `embarques` minimiza o número de baldeações de verdade, e não o número de paradas percorridas.

Tempo e distância de cada aresta são somas de trechos entre paradas consecutivas, e esses trechos têm o mesmo valor para todas as linhas que passam por eles. Por isso, dividir uma viagem em duas nunca fica mais barato. O teste `test_otimos_sao_validos` confere que nenhum caminho mínimo, nos 30.002 pares alcançáveis, tem baldeação inútil.

## Eficiência (análise prática e teórica)

`python main.py desempenho` (ou a opção 4 do menu) mede três abordagens na mesma matriz de custos e **confere no código que todas dão as mesmas distâncias**:

- Floyd–Warshall em Python puro.
- Floyd–Warshall vetorizado (NumPy, mesma recorrência).
- Dijkstra a partir de cada origem, com fila de prioridade `heapq`.

A mesma medição mostra o crescimento em subgrafos de 30 a 237 vértices e compara as três versões vistas em aula. Valores medidos no ambiente de desenvolvimento, por critério (variam conforme a máquina e a execução):

| Abordagem | Complexidade | Operações em V = 237 | Tempo medido |
|---|---|---|---|
| Floyd–Warshall, Python puro | Θ(V³) tempo, Θ(V²) memória | até V³ = 13,3 milhões de relaxações | 0,09–0,15 s |
| Floyd–Warshall, NumPy | Θ(V³) | idem | 0,04–0,05 s |
| Dijkstra × V (heapq) | O(V·(V+E)·log V) | ~7,9 milhões | 0,03–0,04 s |

Na versão NumPy, o tempo dividido por k³ fica praticamente constante a partir de k = 60, entre 2,7 e 4,2 ns nas medições. Isso confirma na prática o crescimento cúbico.

**Recursão × memoização × tabela** (subgrafos da rede real, critério tempo):

| k vértices | Recursão pura: chamadas | Memoização: estados guardados | Tabela: células |
|---|---|---|---|
| 8 | 629.824 | 576 | 64 |
| 30 | inviável (~3^k) | 27.900 | 900 |
| 60 | inviável | 219.600 | 3.600 |

**Leitura honesta.** O grafo é esparso: tem aresta em 4.008 dos 55.932 pares possíveis (7%). Em grafo esparso, Dijkstra repetido faz menos operações e fica 2 a 3× mais rápido em Python puro. Mesmo assim, mantivemos o Floyd–Warshall por quatro motivos:

1. É programação dinâmica por tabulação, a técnica da disciplina, indicada para "todas as distâncias entre todos os pares".
2. O cálculo roda **uma vez, antes**, para gerar a tabela completa que vai para o Oracle. Nesse uso, menos de 0,2 s por critério é desprezível.
3. As tabelas `D` e `NXT` respondem qualquer par, e as alternativas por linha de embarque saem com consultas O(1).
4. A recorrência é derivada passo a passo (recursão, memoização, tabela) e o código final tem três laços, fácil de verificar.

Esse equilíbrio vale só para o piloto. No GTFS inteiro (25.105 paradas) seriam 1,6 × 10¹³ relaxações e 5 GB por matriz. Para calcular sob demanda nessa escala, o adequado seria Dijkstra (ou A*) de origem única por consulta.

## Funcionalidades implementadas

- **Menu interativo** (`python main.py`): o usuário escolhe origem e destino na lista de pontos do MVP, o cenário e o critério.
- Até 3 alternativas por par, sem repetição. Linhas no mesmo itinerário viram uma única alternativa (ex.: 001, 002, 193, 339, 340, 451, 484 e 531 na Estrada de Itapecerica), e alternativas com 80% ou mais do traçado sobreposto são descartadas.
- Três critérios de custo (`tempo`, `distancia`, `embarques`) e a comparação entre eles.
- Cinco cenários, com os mesmos códigos e janelas da tabela `PH_CENARIO` do banco: `UTIL_MANHA` (dia útil, 06h–09h), `UTIL_TARDE` (17h–20h), `UTIL_NOITE` (20h–24h), `SABADO_MANHA` (08h–12h) e `DOMINGO_MANHA` (08h–11h). Uma linha sem partida na janela não entra no grafo daquele cenário.
- Simulação no quadro de horários a partir de um horário. Por exemplo, saindo às 07h00, o 551 parte às 07:04 e chega às 07:28.
- Situações sem solução tratadas: `SEM_TRAJETO`, `SEM_TRAJETO_RAZOAVEL` (por exemplo, atravessar a rua exigiria ir ao terminal e voltar), parada inexistente, horário inválido e último ônibus já saiu.
- Exportação no formato do banco oficial: um CSV por tabela do `database/02_ddl.sql` do repositório, mais GeoJSON para o mapa (ver [Exportação para o banco](#exportação-para-o-banco)).

## Como executar

Requisitos: Python 3.8 ou superior, `numpy` e `pandas`. Os testes passam em Python 3.8, 3.13 e 3.14 (este último também no Windows). O pandas só é usado na extração. No repositório da equipe, o módulo fica na pasta `dynamic-programming/`: entre nela antes de rodar os comandos.

```bash
pip install -r requirements.txt

python main.py                                   # menu interativo

python main.py consultar 13211 407 --hora 07:00  # Embu -> Terminal Capão Redondo
python main.py consultar 32960 21657             # M'Boi Mirim -> Av. Comendador Sant'Anna
python main.py consultar 405 2201 --hora 07:00   # caso com baldeação no terminal
python main.py consultar 407 393                 # caso sem trajeto
python main.py criterios 1325 407                # tempo x distância x embarques
python main.py desempenho                        # medição de eficiência
python main.py exportar --cenarios UTIL_MANHA,UTIL_TARDE,UTIL_NOITE,SABADO_MANHA,DOMINGO_MANHA

python -m unittest discover -s tests -v          # 73 testes
```

### Entradas e saídas

| | Conteúdo |
|---|---|
| **Entradas** | Rede piloto extraída do GTFS da ARTESP (`dados/rede_piloto.json`, com paradas, linhas, sequência de paradas, horários programados e traçados). Na consulta: parada de origem, parada de destino, cenário (tipo de dia e janela horária), critério de ordenação (`tempo`, `distancia` ou `embarques`) e, opcionalmente, um horário de saída |
| **Saída do algoritmo** | Tabelas `D` (menor custo entre todos os pares) e `NXT` (próximo vértice do caminho), uma para cada critério |
| **Saída para o cidadão** | Até 3 alternativas distintas, cada uma com linhas, embarques e baldeações, sequência de paradas, distância, espera estimada e tempo a bordo. Também mostra a sobreposição entre as alternativas e, se houver horário, a simulação no quadro de horários. Quando não há solução, o status é `SEM_TRAJETO` ou `SEM_TRAJETO_RAZOAVEL` |
| **Saída para o banco** | CSVs com o nome e as colunas das tabelas do Oracle (`ph_par_origem_destino`, `ph_alternativa`, `ph_etapa_trajeto` e cadastros), para a API Java só consultar |

### Exemplo de entrada e saída

Entrada:

```bash
python main.py consultar 13211 407 --hora 07:00
```

Saída (trecho):

```
13211 Av. João Paulo II, 1581 - Jardim Casa Branca, Embu das Artes ...  ->  407 Terminal do Metrô Capão Redondo
Cenário: Dia útil, 06h00-09h00 | ordenação: tempo | ALTERNATIVAS_DISTINTAS

  Alternativa 1: 1 embarque(s), 0 baldeação(ões), 22 paradas, 6.00 km, espera ~5.3 + bordo 24.1 = 29.4 min
    linha 551 (mesmo itinerário: 551BI1): 13211 -> 407, 21 saltos, 6000 m, ...

  Alternativa 2: 1 embarque(s), 0 baldeação(ões), 32 paradas, 8.97 km, espera ~2.5 + bordo 41.6 = 44.1 min
    linha 193: 13211 -> 407, 31 saltos, 8972 m, ...

  Sobreposição (fração a até 30 m da outra):
     1.00  0.26
     0.26  1.00

  Simulação no quadro de horários (WD) saindo às 07:00:
    alternativa 1: 551 07:04->07:28 (total 28.0 min)
    alternativa 2: 193 07:01->07:44 (total 44.0 min)
```

Exemplo sem solução: `python main.py consultar 407 393` devolve `SEM_TRAJETO`, porque os ônibus que param em 393 vêm de fora do recorte.

`dados/rede_piloto.json` já vem pronto. O GTFS original (46 MB) só é necessário para regenerar a rede, com `python main.py extrair --gtfs artesp_gtfs.zip`.

### Exportação para o banco

`python main.py exportar` grava em `saida/` um CSV por tabela do modelo oficial (`database/02_ddl.sql` do repositório), com os mesmos nomes de colunas. Os `id_*` são IDENTITY no Oracle e não vão nos arquivos: cada chave estrangeira sai pela coluna UNIQUE da tabela referenciada (`cd_cenario`, `cd_parada_gtfs`, `cd_linha`, `nm_fonte`), e na carga é trocada pelo id com uma consulta nessa coluna.

| Arquivo | Conteúdo | Regra de conversão |
|---|---|---|
| `ph_cenario.csv` | Os 5 cenários | Iguais ao DML do banco |
| `ph_parada.csv` | Paradas usadas nos pares e nas etapas | Município tirado do nome da parada no GTFS. Seis paradas sem cidade no nome foram conferidas pelo endereço (lista e evidência em `config.py`); as demais saem como `NÃO INFORMADO`, sem adivinhar |
| `ph_linha.csv` | As 15 linhas do piloto | `ds_itinerario` = nome da linha no GTFS |
| `ph_par_origem_destino.csv` | Resultado de cada par em cada cenário | `ALTERNATIVAS_DISTINTAS` e `TRAJETO_UNICO` viram `COM_ALTERNATIVAS` |
| `ph_alternativa.csv` | Até 3 alternativas por par | Segundos → minutos com 1 casa; metros → km com 2 casas (arredondamento comercial, 5 sobe, como no Oracle) |
| `ph_etapa_trajeto.csv` | Uma etapa por embarque | Linha do itinerário escolhido; as linhas equivalentes ficam em `complementar/etapa_detalhe.csv` |

Em `complementar/` ficam o detalhe em segundos, a sequência completa de paradas com coordenadas e o GeoJSON do mapa. O `metadados.json` registra a versão do GTFS, os parâmetros e essas regras. Com os 16 pontos do MVP e os 5 cenários, a exportação tem 1.200 pares, 508 alternativas e 875 etapas. Com a mesma `--data-calculo`, os arquivos saem idênticos, byte a byte, em Python 3.8 e 3.13.

## Testes (73)

- **Algoritmo:** grafo resolvido à mão, sem caminho, grafo dirigido, entrada inválida (negativo, NaN, matriz torta) e 40 grafos aleatórios em que Python, NumPy e Dijkstra dão o mesmo resultado.
- **Versões do curso:** recursão pura, memoização e tabela iguais em 25 grafos. O número de chamadas da recursão bate com a fórmula, e cada estado da memoização é calculado uma vez.
- **Tabulação do alinhamento:** igual à força bruta em 60 casos aleatórios.
- **Exemplos nas docstrings** (`>>>`, como na apostila), executados pelos testes.
- **Rede real:** alternativas, baldeação no terminal, cenários, critérios, todos os ótimos válidos e trechos existentes no GTFS.
- **Exportação:** cabeçalhos iguais ao DDL oficial, CHECKs do banco (status, ordem, precisão de `NUMBER(5,1)` e `NUMBER(6,2)`, baldeações de 0 a 2, tamanho dos textos em bytes), chaves naturais únicas, integridade referencial entre os arquivos, etapas encadeadas da origem ao destino e cenários iguais aos do DML.
- **Reprodutibilidade:** os custos são somados com `math.fsum` (soma exatamente arredondada). Sem isso, dois caminhos de mesmo custo podiam empatar de um jeito no Python 3.8 e de outro no 3.13, porque o `sum()` de números de ponto flutuante mudou no Python 3.12.
- **Interface:** menu com entradas inválidas, fim de entrada, códigos de saída da linha de comando, cenário em minúsculas e exportação que recusa entrada inválida antes de gravar.

## Estrutura

```
main.py                       interface: menu e linha de comando (só entrada e saída)
pharos/config.py              recorte, cenários, critérios, limiares e pontos do MVP
pharos/extracao_gtfs.py       GTFS -> dados/rede_piloto.json
pharos/alinhamento.py         tabulação: paradas -> traçado
pharos/grafo.py               vértices, arestas, pesos e matriz de custos
pharos/floyd_warshall.py      algoritmo (Python puro e NumPy) e reconstrução
pharos/alternativas.py        alternativas, distinção geométrica e simulação de horários
pharos/desempenho.py          medições: FW x Dijkstra (heapq) e crescimento
pharos/exportar.py            CSVs no formato do banco (ph_*.csv) e GeoJSON para o mapa
tests/                        testes unitários, de integração e de interface
saida/                        resultado da exportação (ph_*.csv, complementar/, metadados.json)
docs/RELATORIO_VALIDACAO_DP.md
```

## Dados: origem e limitações

- **Fonte pública:** GTFS da ARTESP, versão `20261007`, vigência de 01/01 a 31/12/2026, SHA-256 `f3fdca9599e512e191f1bb78cebcafab1bac8a458fbdd5c5e71cc2d10d97d45a`, licença Creative Commons Atribuição indicada no portal de dados abertos da ARTESP (dadosabertos.artesp.sp.gov.br). **Nenhum dado pessoal** é usado.
- **Tempos programados, não tempo real.** Em 100% das viagens, a ARTESP distribui o tempo de forma uniforme entre as paradas, e a duração não muda ao longo do dia.
- **Espera estimada.** É a metade do intervalo médio da linha na janela, na hipótese de que o passageiro chega em um momento aleatório. Onde várias linhas atendem o mesmo trecho, a estimativa é conservadora.
- **Sem caminhada.** Baldeações só acontecem na mesma parada.
- **Sem feriados.** O feed não traz `calendar_dates.txt`.
- **Viagens duplicadas.** O feed tem 2.402 viagens repetidas, e nas linhas 558 e 563 cada partida é contada uma vez.
- **Filtros de apresentação** (decisões declaradas em `config.py`): no máximo 2 baldeações e índice de desvio de até 3× a linha reta. A linha reta serve só para detectar voltas e nunca é usada como distância de caminhada.

## Uso de IA

Os prompts estão em `prompts.md`.
