-- =====================================================================
-- PHAROS - Global Solution 2026 (2º semestre) - FIAP - Database Design
-- Script 03 - DML (dados de exemplo) - Oracle Database
-- Executar depois do 02_ddl.sql. No SQL Developer, use F5 (executar script).
-- Arquivo salvo em UTF-8.
--
-- Origem dos dados:
--  * Paradas, linhas, pares e alternativas: valores reais, tirados do
--    relatório de validação do módulo Dynamic Programming (06/11/2026),
--    calculados sobre o GTFS da ARTESP, versão 20261007, para o cenário
--    "dia útil, 6h às 9h". Tempos arredondados ao minuto como no relatório,
--    exceto 22,7 e 23,0 min, que o relatório traz com uma casa decimal.
--  * PH_INDICADOR_OCORRENCIA e PH_CONSULTA: dados SIMULADOS (fonte 4,
--    fl_simulado = S, e consultas com fl_teste = S). Servem para testar o
--    banco e a API e devem ser trocados pelo cálculo real antes de qualquer
--    demonstração pública.
--  * Coordenadas das paradas ficam NULL: devem ser preenchidas com
--    stop_lat/stop_lon do stops.txt do GTFS. Não foram inventadas.
--
-- Os IDs são informados explicitamente (1 a 999) para deixar as chaves
-- estrangeiras legíveis. A API gera IDs a partir de 1000 (ver DDL).
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. PH_FONTE_DADOS
-- EXCEÇÃO JUSTIFICADA: 4 registros. O domínio desta tabela são as fontes
-- efetivamente usadas pelo MVP, e o Pharos usa apenas quatro: GTFS da
-- ARTESP, dados criminais da SSP-SP, o cálculo do módulo DP e os dados
-- simulados de teste. Criar uma quinta fonte seria inventar dado.
-- ds_url fica NULL até a equipe colar o link exato de cada download
-- (tarefa 3.4 - registrar fontes dos dados utilizados).
-- ---------------------------------------------------------------------
INSERT INTO ph_fonte_dados (id_fonte, nm_fonte, nm_orgao, ds_versao, ds_url,
                            dt_inicio_periodo, dt_fim_periodo, fl_simulado, ds_limitacao)
VALUES (1, 'GTFS ARTESP - transporte intermunicipal',
        'ARTESP - Agência de Transporte do Estado de São Paulo', '20261007', NULL,
        NULL, NULL, 'N',
        'Horários programados, não em tempo real. Os horários entre paradas são interpolados de forma uniforme e não refletem trânsito.');

-- Período: ano de 2025. Conferir as datas exatas do arquivo baixado da SSP-SP.
INSERT INTO ph_fonte_dados (id_fonte, nm_fonte, nm_orgao, ds_versao, ds_url,
                            dt_inicio_periodo, dt_fim_periodo, fl_simulado, ds_limitacao)
VALUES (2, 'SSP-SP - dados criminais (boletins de ocorrência)',
        'Secretaria da Segurança Pública do Estado de São Paulo', '2025', NULL,
        DATE '2025-01-01', DATE '2025-12-31', 'N',
        'Só inclui ocorrências registradas (há subnotificação). Localização aproximada. Dados de 2025 comparados à rede de 2026. Uso apenas agregado.');

INSERT INTO ph_fonte_dados (id_fonte, nm_fonte, nm_orgao, ds_versao, ds_url,
                            dt_inicio_periodo, dt_fim_periodo, fl_simulado, ds_limitacao)
VALUES (3, 'Cálculo Pharos - Floyd-Warshall (módulo Dynamic Programming)',
        'Equipe Pharos - FIAP', 'validação de 06/11/2026', NULL,
        NULL, NULL, 'N',
        'Tempo programado com espera estimada pela frequência da linha. Baldeação só na mesma parada. Sem caminhada. Recorte piloto de 237 paradas.');

INSERT INTO ph_fonte_dados (id_fonte, nm_fonte, nm_orgao, ds_versao, ds_url,
                            dt_inicio_periodo, dt_fim_periodo, fl_simulado, ds_limitacao)
VALUES (4, 'Dados simulados - testes da equipe',
        'Equipe Pharos - FIAP', NULL, NULL,
        NULL, NULL, 'S',
        'Valores fictícios para testar o banco e a API. Não representam a realidade.');


-- ---------------------------------------------------------------------
-- 2. PH_PARADA (fonte 1 - GTFS ARTESP)
-- cd_parada_gtfs = stop_id real do GTFS.
-- ---------------------------------------------------------------------
INSERT INTO ph_parada (id_parada, cd_parada_gtfs, nm_parada, nm_municipio,
                       nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte)
VALUES (1, '407', 'Terminal Metrô Capão Redondo', 'São Paulo', NULL, NULL, 'S', 'S', 1);

INSERT INTO ph_parada (id_parada, cd_parada_gtfs, nm_parada, nm_municipio,
                       nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte)
VALUES (2, '13211', 'Av. João Paulo II, 1581 (sentido Terminal Capão Redondo)', 'Embu das Artes', NULL, NULL, 'N', 'S', 1);

INSERT INTO ph_parada (id_parada, cd_parada_gtfs, nm_parada, nm_municipio,
                       nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte)
VALUES (3, '13466', 'Av. João Paulo II, 1581 (sentido Embu das Artes)', 'Embu das Artes', NULL, NULL, 'N', 'S', 1);

INSERT INTO ph_parada (id_parada, cd_parada_gtfs, nm_parada, nm_municipio,
                       nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte)
VALUES (4, '32960', 'Estr. M''Boi Mirim, 5780B', 'São Paulo', NULL, NULL, 'N', 'S', 1);

INSERT INTO ph_parada (id_parada, cd_parada_gtfs, nm_parada, nm_municipio,
                       nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte)
VALUES (5, '21657', 'Av. Comendador Sant''Anna, 679', 'São Paulo', NULL, NULL, 'N', 'S', 1);

INSERT INTO ph_parada (id_parada, cd_parada_gtfs, nm_parada, nm_municipio,
                       nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte)
VALUES (6, '405', 'Estr. de Itapecerica, 4765', 'São Paulo', NULL, NULL, 'N', 'S', 1);

INSERT INTO ph_parada (id_parada, cd_parada_gtfs, nm_parada, nm_municipio,
                       nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte)
VALUES (7, '2201', 'Estr. M''Boi Mirim, 5790', 'São Paulo', NULL, NULL, 'N', 'S', 1);


-- ---------------------------------------------------------------------
-- 3. PH_LINHA (fonte 1 - GTFS ARTESP)
-- ---------------------------------------------------------------------
INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (1, '551', 'Via Estr. Pirajussara-Valo Velho, Av. Augusto Barbosa Tavares e Av. Carlos Lacerda, até o Terminal Capão Redondo', 'ONIBUS', 1);

INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (2, '193', 'Via Estr. Itapecerica-Campo Limpo e Estrada de Itapecerica (corredor piloto), até o Terminal Capão Redondo', 'ONIBUS', 1);

INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (3, '237', 'Via R. Abílio César e R. Henrique Sam Mindlin', 'ONIBUS', 1);

INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (4, '513', 'Via Estr. M''Boi Mirim e Av. Comendador Sant''Anna', 'ONIBUS', 1);

INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (5, '558', 'Mesmo eixo da linha 513 no recorte piloto (Estr. M''Boi Mirim e Av. Comendador Sant''Anna)', 'ONIBUS', 1);

INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (6, '484', 'Corredor da Estrada de Itapecerica (paradas 396 a 405), até o Terminal Capão Redondo', 'ONIBUS', 1);

INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (7, '001', 'Corredor da Estrada de Itapecerica (paradas 396 a 405), até o Terminal Capão Redondo', 'ONIBUS', 1);

INSERT INTO ph_linha (id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte)
VALUES (8, '002', 'Corredor da Estrada de Itapecerica (paradas 396 a 405), até o Terminal Capão Redondo', 'ONIBUS', 1);


-- ---------------------------------------------------------------------
-- 4. PH_CENARIO
-- Janelas definidas pela equipe. Até agora só UTIL_MANHA foi calculado,
-- os demais estão cadastrados e ainda sem pares.
-- ---------------------------------------------------------------------
INSERT INTO ph_cenario (id_cenario, cd_cenario, nm_cenario, tp_dia, nr_hora_inicio, nr_hora_fim)
VALUES (1, 'UTIL_MANHA', 'Dia útil - pico da manhã', 'UTIL', 6, 9);

INSERT INTO ph_cenario (id_cenario, cd_cenario, nm_cenario, tp_dia, nr_hora_inicio, nr_hora_fim)
VALUES (2, 'UTIL_TARDE', 'Dia útil - pico da tarde', 'UTIL', 17, 20);

INSERT INTO ph_cenario (id_cenario, cd_cenario, nm_cenario, tp_dia, nr_hora_inicio, nr_hora_fim)
VALUES (3, 'UTIL_NOITE', 'Dia útil - noite', 'UTIL', 20, 24);

INSERT INTO ph_cenario (id_cenario, cd_cenario, nm_cenario, tp_dia, nr_hora_inicio, nr_hora_fim)
VALUES (4, 'SABADO_MANHA', 'Sábado - manhã', 'SABADO', 8, 12);

INSERT INTO ph_cenario (id_cenario, cd_cenario, nm_cenario, tp_dia, nr_hora_inicio, nr_hora_fim)
VALUES (5, 'DOMINGO_MANHA', 'Domingo - manhã', 'DOMINGO', 8, 11);


-- ---------------------------------------------------------------------
-- 5. PH_PAR_ORIGEM_DESTINO (cenário 1, fonte 3 - cálculo DP)
-- Pares 6 e 7 reproduzem os casos sem trajeto encontrados na validação.
-- ---------------------------------------------------------------------
-- 13211 -> 407
INSERT INTO ph_par_origem_destino (id_par_od, id_cenario, id_parada_origem, id_parada_destino,
                                   st_resultado, dt_calculo, id_fonte)
VALUES (1, 1, 2, 1, 'COM_ALTERNATIVAS', DATE '2026-11-06', 3);

-- 407 -> 13466
INSERT INTO ph_par_origem_destino (id_par_od, id_cenario, id_parada_origem, id_parada_destino,
                                   st_resultado, dt_calculo, id_fonte)
VALUES (2, 1, 1, 3, 'COM_ALTERNATIVAS', DATE '2026-11-06', 3);

-- 32960 -> 21657
INSERT INTO ph_par_origem_destino (id_par_od, id_cenario, id_parada_origem, id_parada_destino,
                                   st_resultado, dt_calculo, id_fonte)
VALUES (3, 1, 4, 5, 'COM_ALTERNATIVAS', DATE '2026-11-06', 3);

-- 32960 -> 407
INSERT INTO ph_par_origem_destino (id_par_od, id_cenario, id_parada_origem, id_parada_destino,
                                   st_resultado, dt_calculo, id_fonte)
VALUES (4, 1, 4, 1, 'COM_ALTERNATIVAS', DATE '2026-11-06', 3);

-- 405 -> 2201
INSERT INTO ph_par_origem_destino (id_par_od, id_cenario, id_parada_origem, id_parada_destino,
                                   st_resultado, dt_calculo, id_fonte)
VALUES (5, 1, 6, 7, 'COM_ALTERNATIVAS', DATE '2026-11-06', 3);

-- 407 -> 32960
INSERT INTO ph_par_origem_destino (id_par_od, id_cenario, id_parada_origem, id_parada_destino,
                                   st_resultado, dt_calculo, id_fonte)
VALUES (6, 1, 1, 4, 'SEM_TRAJETO', DATE '2026-11-06', 3);

-- 32960 -> 2201
INSERT INTO ph_par_origem_destino (id_par_od, id_cenario, id_parada_origem, id_parada_destino,
                                   st_resultado, dt_calculo, id_fonte)
VALUES (7, 1, 4, 7, 'SEM_TRAJETO_RAZOAVEL', DATE '2026-11-06', 3);


-- ---------------------------------------------------------------------
-- 6. PH_ALTERNATIVA (valores do relatório de validação do DP)
-- ---------------------------------------------------------------------
-- linha 551
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (1, 1, 1, 29.0, 6.00, 0);

-- linha 193
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (2, 1, 2, 44.0, 8.97, 0);

-- linha 551
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (3, 2, 1, 31.0, 5.88, 0);

-- linha 193
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (4, 2, 2, 46.0, 8.99, 0);

-- linha 237
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (5, 3, 1, 16.0, 2.75, 0);

-- linha 513
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (6, 3, 2, 16.0, 3.12, 0);

-- linha 237
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (7, 4, 1, 22.7, 4.62, 0);

-- linha 513
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (8, 4, 2, 23.0, 4.98, 0);

-- 193 até o terminal + 237
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (9, 5, 1, 28.0, 5.49, 1);

-- 193 até o terminal + 513
INSERT INTO ph_alternativa (id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, qt_baldeacoes)
VALUES (10, 5, 2, 32.0, 5.85, 1);


-- ---------------------------------------------------------------------
-- 7. PH_ETAPA_TRAJETO
-- Alternativas 9 e 10 têm duas etapas: baldeação no Terminal (parada 1).
-- ---------------------------------------------------------------------
INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (1, 1, 1, 1, 2, 1);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (2, 2, 1, 2, 2, 1);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (3, 3, 1, 1, 1, 3);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (4, 4, 1, 2, 1, 3);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (5, 5, 1, 3, 4, 5);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (6, 6, 1, 4, 4, 5);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (7, 7, 1, 3, 4, 1);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (8, 8, 1, 4, 4, 1);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (9, 9, 1, 2, 6, 1);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (10, 9, 2, 3, 1, 7);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (11, 10, 1, 2, 6, 1);

INSERT INTO ph_etapa_trajeto (id_etapa, id_alternativa, nr_sequencia, id_linha, id_parada_embarque, id_parada_desembarque)
VALUES (12, 10, 2, 4, 1, 7);


-- ---------------------------------------------------------------------
-- 8. PH_TIPO_OCORRENCIA (categorias definidas pela equipe)
-- ---------------------------------------------------------------------
INSERT INTO ph_tipo_ocorrencia (id_tipo_ocorrencia, cd_tipo, nm_tipo, ds_tipo)
VALUES (1, 'ROUBO_CELULAR', 'Roubo de celular', 'Subtração de celular com violência ou grave ameaça');

INSERT INTO ph_tipo_ocorrencia (id_tipo_ocorrencia, cd_tipo, nm_tipo, ds_tipo)
VALUES (2, 'FURTO_CELULAR', 'Furto de celular', 'Subtração de celular sem violência');

INSERT INTO ph_tipo_ocorrencia (id_tipo_ocorrencia, cd_tipo, nm_tipo, ds_tipo)
VALUES (3, 'ROUBO_OUTROS', 'Roubo de outros bens', 'Roubo de bens pessoais que não sejam celular nem veículo');

INSERT INTO ph_tipo_ocorrencia (id_tipo_ocorrencia, cd_tipo, nm_tipo, ds_tipo)
VALUES (4, 'FURTO_OUTROS', 'Furto de outros bens', 'Furto de bens pessoais que não sejam celular nem veículo');

INSERT INTO ph_tipo_ocorrencia (id_tipo_ocorrencia, cd_tipo, nm_tipo, ds_tipo)
VALUES (5, 'LESAO_CORPORAL', 'Lesão corporal', 'Agressão física registrada como lesão corporal dolosa');


-- ---------------------------------------------------------------------
-- 9. PH_INDICADOR_OCORRENCIA - DADOS SIMULADOS (fonte 4)
-- Raio de 250 m, ano 2025. Substituir pelo recálculo com os boletins da
-- SSP-SP por alternativa (pendência do relatório de validação do DP).
-- ---------------------------------------------------------------------
INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (1, 1, 1, 4, 2025, 'NOITE', 250, 14);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (2, 1, 1, 4, 2025, 'MANHA', 250, 9);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (3, 1, 2, 4, 2025, 'NOITE', 250, 6);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (4, 1, 4, 4, 2025, 'TARDE', 250, 5);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (5, 2, 1, 4, 2025, 'NOITE', 250, 27);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (6, 2, 1, 4, 2025, 'MANHA', 250, 15);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (7, 2, 2, 4, 2025, 'NOITE', 250, 11);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (8, 2, 4, 4, 2025, 'TARDE', 250, 8);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (9, 5, 1, 4, 2025, 'NOITE', 250, 6);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (10, 5, 1, 4, 2025, 'MANHA', 250, 4);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (11, 5, 2, 4, 2025, 'NOITE', 250, 3);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (12, 5, 4, 4, 2025, 'TARDE', 250, 2);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (13, 6, 1, 4, 2025, 'NOITE', 250, 9);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (14, 6, 1, 4, 2025, 'MANHA', 250, 5);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (15, 6, 2, 4, 2025, 'NOITE', 250, 4);

INSERT INTO ph_indicador_ocorrencia (id_indicador, id_alternativa, id_tipo_ocorrencia, id_fonte, nr_ano, tp_faixa_horaria, nr_raio_m, qt_ocorrencias)
VALUES (16, 6, 4, 4, 2025, 'TARDE', 250, 3);


-- ---------------------------------------------------------------------
-- 10. PH_CONSULTA - DADOS SIMULADOS (fl_teste = S)
-- Regra de negócio validada na API (camada BO): a alternativa escolhida
-- precisa pertencer ao mesmo par da consulta.
-- ---------------------------------------------------------------------
INSERT INTO ph_consulta (id_consulta, id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao,
                         dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste)
VALUES (1, 1, 1, 'TEMPO', TIMESTAMP '2026-11-10 07:42:10', 180, 5, 'S');

INSERT INTO ph_consulta (id_consulta, id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao,
                         dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste)
VALUES (2, 1, 1, 'OCORRENCIAS', TIMESTAMP '2026-11-10 21:15:03', 205, 4, 'S');

INSERT INTO ph_consulta (id_consulta, id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao,
                         dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste)
VALUES (3, 3, NULL, 'DISTANCIA', TIMESTAMP '2026-11-11 06:58:41', 210, NULL, 'S');

INSERT INTO ph_consulta (id_consulta, id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao,
                         dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste)
VALUES (4, 4, 8, 'BALDEACOES', TIMESTAMP '2026-11-11 08:20:00', 155, 4, 'S');

INSERT INTO ph_consulta (id_consulta, id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao,
                         dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste)
VALUES (5, 7, NULL, 'TEMPO', TIMESTAMP '2026-11-11 22:05:37', 95, 2, 'S');

INSERT INTO ph_consulta (id_consulta, id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao,
                         dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste)
VALUES (6, 5, 9, 'TEMPO', TIMESTAMP '2026-11-12 07:10:12', 230, 4, 'S');

INSERT INTO ph_consulta (id_consulta, id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao,
                         dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste)
VALUES (7, 6, NULL, 'TEMPO', TIMESTAMP '2026-11-12 18:40:55', 90, NULL, 'S');


COMMIT;


-- ---------------------------------------------------------------------
-- CONFERÊNCIA: quantidade de registros gravados em cada tabela.
-- ---------------------------------------------------------------------
SELECT 'PH_FONTE_DADOS' AS tabela, COUNT(*) AS registros FROM ph_fonte_dados
UNION ALL SELECT 'PH_PARADA', COUNT(*) FROM ph_parada
UNION ALL SELECT 'PH_LINHA', COUNT(*) FROM ph_linha
UNION ALL SELECT 'PH_CENARIO', COUNT(*) FROM ph_cenario
UNION ALL SELECT 'PH_PAR_ORIGEM_DESTINO', COUNT(*) FROM ph_par_origem_destino
UNION ALL SELECT 'PH_ALTERNATIVA', COUNT(*) FROM ph_alternativa
UNION ALL SELECT 'PH_ETAPA_TRAJETO', COUNT(*) FROM ph_etapa_trajeto
UNION ALL SELECT 'PH_TIPO_OCORRENCIA', COUNT(*) FROM ph_tipo_ocorrencia
UNION ALL SELECT 'PH_INDICADOR_OCORRENCIA', COUNT(*) FROM ph_indicador_ocorrencia
UNION ALL SELECT 'PH_CONSULTA', COUNT(*) FROM ph_consulta;
