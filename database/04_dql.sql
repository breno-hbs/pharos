-- =====================================================================
-- PHAROS - Global Solution 2026 (2º semestre) - FIAP - Database Design
-- Script 04 - DQL (consultas) - Oracle Database
-- Executar depois do 02_ddl.sql e do 03_dml.sql.
-- Cada consulta corresponde a uma funcionalidade do MVP.
-- =====================================================================


-- ---------------------------------------------------------------------
-- CONSULTA 1 - INNER JOIN entre duas tabelas
-- Funcionalidade: detalhes do percurso (etapas e conexões do trajeto).
-- Lista as etapas de cada alternativa calculada com a linha de ônibus
-- usada. Alternativas com duas etapas têm baldeação no Terminal
-- Capão Redondo (parada 1).
-- ---------------------------------------------------------------------
SELECT e.id_alternativa,
       e.nr_sequencia          AS etapa,
       l.cd_linha              AS linha,
       l.tp_modal              AS modal,
       e.id_parada_embarque    AS parada_embarque,
       e.id_parada_desembarque AS parada_desembarque,
       l.ds_itinerario         AS itinerario
  FROM ph_etapa_trajeto e
 INNER JOIN ph_linha l
    ON l.id_linha = e.id_linha
 ORDER BY e.id_alternativa, e.nr_sequencia;


-- ---------------------------------------------------------------------
-- CONSULTA 2 - INNER JOIN + funções de grupo + GROUP BY
-- Funcionalidade: comparação de alternativas (indicador histórico).
-- Soma as ocorrências registradas a até 250 m do traçado de cada
-- alternativa em 2025, separa o período noturno e calcula ocorrências por
-- km, já que um trajeto mais longo naturalmente passa por mais área.
-- Atenção: com o 03_dml.sql atual, os indicadores são SIMULADOS (fonte 4).
-- ---------------------------------------------------------------------
SELECT a.id_par_od,
       a.id_alternativa,
       a.nr_ordem,
       a.nr_tempo_total_min                                   AS tempo_min,
       a.nr_distancia_km                                      AS distancia_km,
       SUM(i.qt_ocorrencias)                                  AS total_ocorrencias,
       SUM(CASE WHEN i.tp_faixa_horaria = 'NOITE'
                THEN i.qt_ocorrencias ELSE 0 END)             AS ocorrencias_noite,
       ROUND(SUM(i.qt_ocorrencias) / a.nr_distancia_km, 1)    AS ocorrencias_por_km,
       COUNT(*)                                               AS registros_agregados
  FROM ph_alternativa a
 INNER JOIN ph_indicador_ocorrencia i
    ON i.id_alternativa = a.id_alternativa
 WHERE i.nr_raio_m = 250
   AND i.nr_ano = 2025
 GROUP BY a.id_par_od, a.id_alternativa, a.nr_ordem, a.nr_tempo_total_min, a.nr_distancia_km
 ORDER BY a.id_par_od, a.nr_ordem;


-- ---------------------------------------------------------------------
-- CONSULTA 3 - LEFT OUTER JOIN + WHERE + ORDER BY
-- Funcionalidade: planejamento do trajeto (resposta para uma origem).
-- Mostra o que o Pharos responde para quem sai da parada GTFS 32960
-- (id 4, Estr. M’Boi Mirim, 5780B) no cenário dia útil de manhã (id 1).
-- O LEFT OUTER JOIN mantém também os destinos SEM trajeto, que aparecem
-- com as colunas da alternativa em NULL: a plataforma informa "sem
-- trajeto" em vez de esconder o destino ou inventar um resultado.
-- ---------------------------------------------------------------------
SELECT p.id_par_od,
       p.id_parada_destino,
       p.st_resultado,
       a.nr_ordem,
       a.nr_tempo_total_min AS tempo_min,
       a.nr_distancia_km    AS distancia_km,
       a.qt_baldeacoes      AS baldeacoes
  FROM ph_par_origem_destino p
  LEFT OUTER JOIN ph_alternativa a
    ON a.id_par_od = p.id_par_od
 WHERE p.id_cenario = 1
   AND p.id_parada_origem = 4
 ORDER BY p.id_parada_destino, a.nr_ordem;
