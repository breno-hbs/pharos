"""Parâmetros do piloto Pharos.

Todos os valores abaixo são decisões de projeto declaradas, não dados da ARTESP.
Altere aqui e regenere a rede com `python main.py extrair --gtfs <zip>`.
"""

# Recorte geográfico do piloto (graus WGS84). Cobre o trecho paulistano da
# Estrada de Itapecerica, a Av. João Paulo II (Embu das Artes), o eixo
# Av. Augusto Barbosa Tavares / Av. Carlos Lacerda, a Estrada do M'Boi Mirim
# e o Terminal Metrô Capão Redondo.
BBOX = {"lat_min": -23.705, "lat_max": -23.636, "lon_min": -46.806, "lon_max": -46.760}

# Critério de seleção das linhas: entram no piloto todos os padrões
# (linha + sentido + traçado) que passam por pelo menos uma destas paradas.
# 407 = Terminal do Metrô Capão Redondo; 405 e 1443 = extremos do corredor
# da Estrada de Itapecerica usados pelas linhas 001 e 002.
PARADAS_ANCORA = ("407", "405", "1443")

# Latitude de referência para os fatores métricos locais (WGS84).
LAT_REF = -23.67

# Cenários temporais: mesmos códigos, nomes e janelas da tabela PH_CENARIO do
# banco (database/03_dml.sql no repositório da equipe). A espera estimada em
# cada embarque usa somente as partidas programadas na janela e no tipo de dia
# indicados. service_id do GTFS da ARTESP: WD = dia útil, SAT = sábado,
# SUN = domingo.
CENARIOS = {
    "UTIL_MANHA": {"service_id": "WD", "tp_dia": "UTIL", "inicio": "06:00", "fim": "09:00",
                   "nome": "Dia útil - pico da manhã", "descricao": "Dia útil, 06h00-09h00"},
    "UTIL_TARDE": {"service_id": "WD", "tp_dia": "UTIL", "inicio": "17:00", "fim": "20:00",
                   "nome": "Dia útil - pico da tarde", "descricao": "Dia útil, 17h00-20h00"},
    "UTIL_NOITE": {"service_id": "WD", "tp_dia": "UTIL", "inicio": "20:00", "fim": "24:00",
                   "nome": "Dia útil - noite", "descricao": "Dia útil, 20h00-24h00"},
    "SABADO_MANHA": {"service_id": "SAT", "tp_dia": "SABADO", "inicio": "08:00", "fim": "12:00",
                     "nome": "Sábado - manhã", "descricao": "Sábado, 08h00-12h00"},
    "DOMINGO_MANHA": {"service_id": "SUN", "tp_dia": "DOMINGO", "inicio": "08:00", "fim": "11:00",
                      "nome": "Domingo - manhã", "descricao": "Domingo, 08h00-11h00"},
}
CENARIO_PADRAO = "UTIL_MANHA"

# Critérios de custo do Floyd-Warshall.
#   tempo     = espera estimada (headway/2) + tempo a bordo programado (s)
#   distancia = extensão percorrida no traçado GTFS (m)
#   embarques = número de embarques (baldeações = embarques - 1)
CRITERIOS = ("tempo", "distancia", "embarques")

# Desempates (não alteram a ordem entre caminhos com custos realmente diferentes):
EPS_EMBARQUE_M = 0.001       # distancia: +1 mm por embarque -> prefere menos baldeações
EPS_DISTANCIA_EMB = 1e-6     # embarques: +1e-6 por metro -> prefere o mais curto

# Duas alternativas são "efetivamente distintas" quando a maior fração de
# uma delas que fica a até RAIO_SOBREPOSICAO_M da outra é menor que
# LIMIAR_SOBREPOSICAO.
RAIO_SOBREPOSICAO_M = 30.0
PASSO_AMOSTRAGEM_M = 10.0
LIMIAR_SOBREPOSICAO = 0.80
MAX_ALTERNATIVAS = 3

# Filtros de apresentação (decisão de produto, não alteram o Floyd-Warshall):
# alternativas com mais baldeações ou com índice de desvio maior são omitidas.
# Índice de desvio = distância percorrida / distância em linha reta entre
# origem e destino. A linha reta serve só para detectar voltas (ex.: ir ao
# terminal e voltar para o outro lado da rua); NÃO é usada como caminhada.
MAX_BALDEACOES = 2
MAX_INDICE_DESVIO = 3.0

# Alerta de qualidade: parada projetada a mais de X m do traçado.
ALERTA_PROJECAO_M = 50.0

# Pontos selecionáveis do MVP (exportados para o Oracle e listados no menu).
# Cada par ordenado entre eles tem as alternativas pré-calculadas. Paradas do
# GTFS são por sentido: o ponto do outro lado da rua tem outro stop_id.
PONTOS_MVP = {
    "13211": "Av. João Paulo II, 1581 (Embu das Artes) - sentido Metrô",
    "13466": "Av. João Paulo II, 1581 (Embu das Artes) - sentido bairro",
    "407": "Terminal do Metrô Capão Redondo",
    "405": "Estrada de Itapecerica, 4765 - sentido Metrô",
    "1443": "Estrada de Itapecerica, 4516 - sentido bairro",
    "401": "Estrada de Itapecerica, 5859 (UNASP) - sentido Metrô",
    "1446": "Estrada de Itapecerica, 6040 - sentido bairro",
    "398": "Estrada de Itapecerica, 7115 - sentido Metrô",
    "1449": "Estrada de Itapecerica, 7075 - sentido bairro",
    "393": "Estrada de Itapecerica (oposto nº 888) - sentido Metrô",
    "1454": "Estrada de Itapecerica, 11500 - sentido bairro",
    "33608": "Av. Carlos Lacerda, 2180 - sentido Metrô",
    "21969": "Av. Carlos Lacerda, 2263 - sentido bairro",
    "32960": "Estrada do M'Boi Mirim, 5780B - sentido Metrô",
    "2201": "Estrada do M'Boi Mirim, 5790 - sentido bairro",
    "21657": "Av. Comendador Sant'Anna, 679 - sentido Metrô",
}

# Exportação para o banco (database/02_ddl.sql e 03_dml.sql do repositório).
# As chaves estrangeiras para PH_FONTE_DADOS saem pelo nome da fonte (coluna
# UNIQUE), com o mesmo texto das linhas que o DML do banco já cadastra.
FONTE_GTFS = "GTFS ARTESP - transporte intermunicipal"
FONTE_CALCULO = "Cálculo Pharos - Floyd-Warshall (módulo Dynamic Programming)"

# Município das paradas cujo nome no GTFS não traz a cidade. Só entram paradas
# com evidência no próprio GTFS (as quatro primeiras também estão no DML do
# banco, com o mesmo valor):
#   407   Terminal do Metrô Capão Redondo: as linhas que terminam nele trazem
#         "SAO PAULO (METRO CAPAO REDONDO)" no nome (ex.: linha 001).
#   405   Estrada de Itapecerica, 4765, e 1444, nº 5006: ficam entre 1443
#         (nº 4516, São Paulo) e 404 (nº 5114, São Paulo), no mesmo logradouro.
#   13466 Av. João Paulo II, 1581: mesmo endereço de 13211 (Embu das Artes),
#         no sentido oposto.
#   32960 Estrada do M'Boi Mirim, 5780B: vizinha de 2201 (nº 5790, São Paulo).
#   401   Estrada de Itapecerica, 5859 (UNASP): fica entre 402 (nº 5749) e
#         1446 (nº 6040), ambas em São Paulo.
# As demais saem como "NÃO INFORMADO" (ex.: Estrada de Itapecerica acima do
# nº 6555, a última com cidade no nome). Inferir o município pela parada mais
# próxima com cidade no nome errou 2 de 128 casos numa validação cruzada
# (paradas na divisa São Paulo/Embu das Artes), então o código não adivinha.
MUNICIPIO_CONFERIDO = {"407": "São Paulo", "405": "São Paulo", "13466": "Embu das Artes",
                       "32960": "São Paulo", "1444": "São Paulo", "401": "São Paulo"}
MUNICIPIO_NAO_INFORMADO = "NÃO INFORMADO"
