# Database Design

Banco Oracle do Pharos. Ele guarda a rede piloto de transporte, os trajetos já calculados pelo módulo de Dynamic Programming, os indicadores históricos de ocorrências e a origem de cada dado. A API Java (`backend/java`) consulta essas tabelas, mantém o cadastro de paradas e linhas e registra as consultas.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `01_documentacao_modelo.pdf` | Documentação da disciplina (itens 1 e 2): capa da Equipe Pharos, sumário, objetivo, escopo, funcionalidades, tabelas, cardinalidades, os dois diagramas e a execução no Oracle |
| `02_ddl.sql` | Estrutura: 10 tabelas `PH_*`, 10 chaves primárias, 9 UNIQUE, 28 CHECK, 16 chaves estrangeiras (via `ALTER TABLE`), 3 índices e comentários no dicionário de dados |
| `03_dml.sql` | 81 registros de exemplo e uma consulta de conferência no final |
| `04_dql.sql` | As três consultas pedidas na disciplina |
| `diagramas/diagrama_logico.png` | Modelo lógico, exportado do Oracle SQL Developer Data Modeler |
| `diagramas/diagrama_relacional.png` | Modelo relacional, exportado do Oracle SQL Developer Data Modeler |

Os arquivos de 01 a 04 são os entregáveis da disciplina no formato pedido: o PDF com os itens 1 e 2, e os scripts em `.sql` editáveis.

## Como executar

1. Conecte o SQL Developer ao Oracle da FIAP.
2. Execute cada arquivo como script (F5), nesta ordem: `02_ddl.sql`, `03_dml.sql`, `04_dql.sql`.

**Atenção:** o `02_ddl.sql` apaga e recria todas as tabelas `PH_*` do schema. Não execute de novo em um schema que a API já esteja usando sem combinar com a equipe.

## Conexão

Nenhuma credencial fica no repositório (ver `CONTRIBUTING.md`, seção 5). A API lê as variáveis de ambiente `ORACLE_URL`, `ORACLE_USER` e `ORACLE_PASSWORD`, como em `backend/java/.env.example`. As tabelas e os dados de exemplo já estão carregados no schema usado pela equipe no Oracle da FIAP.

## Modelo

Todas as tabelas usam o prefixo `PH_`, para não colidir com outras tabelas do mesmo schema.

| Tabela | Conteúdo | Registros de exemplo |
|---|---|---|
| `PH_FONTE_DADOS` | Origem de cada dado (oficial, calculado ou simulado), período e limitações | 4 |
| `PH_PARADA` | Paradas e terminais da rede piloto (vértices do grafo) | 7 |
| `PH_LINHA` | Linhas de ônibus da rede piloto | 8 |
| `PH_CENARIO` | Tipo de dia e janela de horário do cálculo | 5 |
| `PH_PAR_ORIGEM_DESTINO` | Par origem-destino calculado em um cenário e o status do cálculo | 7 |
| `PH_ALTERNATIVA` | Alternativa de um par: tempo, distância e baldeações | 10 |
| `PH_ETAPA_TRAJETO` | Etapa de uma alternativa: linha, parada de embarque e de desembarque | 12 |
| `PH_TIPO_OCORRENCIA` | Categorias de ocorrência adotadas pela equipe | 5 |
| `PH_INDICADOR_OCORRENCIA` | Contagem histórica agregada por alternativa, tipo, ano, faixa horária e raio | 16 |
| `PH_CONSULTA` | Registro anônimo das consultas feitas na plataforma | 7 |

Decisões principais:

- **O cálculo roda antes.** O Floyd-Warshall (Python) calcula as alternativas e o resultado é gravado em `PH_PAR_ORIGEM_DESTINO`, `PH_ALTERNATIVA` e `PH_ETAPA_TRAJETO`. A API só lê.
- **Sem trajeto também é resultado.** Um par sem caminho fica gravado com o status `SEM_TRAJETO` ou `SEM_TRAJETO_RAZOAVEL` e sem alternativas.
- **Só dado agregado.** As ocorrências entram como contagens. Não há boletim individual nem dado pessoal, e as consultas são anônimas.
- **Chaves geradas pelo banco.** As chaves primárias usam `IDENTITY` a partir de 1000. Os dados de exemplo usam os IDs de 1 a 999.
- **Sem caminhada.** A baldeação acontece sempre na mesma parada.

`PH_FONTE_DADOS` tem 4 registros, e não 5, porque o MVP usa só quatro fontes. A justificativa está no próprio `03_dml.sql`.

## O que a API precisa respeitar

- No `INSERT`, não enviar o ID: o banco gera.
- A alternativa escolhida em `PH_CONSULTA` precisa pertencer ao mesmo par da consulta. O banco não valida isso; a regra fica na camada de negócio.
- Parada, linha, cenário ou fonte em uso não pode ser excluída: a chave estrangeira bloqueia a exclusão.
- Excluir um par apaga em cascata as alternativas, as etapas e os indicadores dele. Se o par tiver consultas registradas, a exclusão é bloqueada.

## Validação

**No Oracle da FIAP, em 16/11/2026** (SQL Developer 26.2, os três scripts executados com F5):

- `02_ddl.sql`: sem erro. A consulta abaixo ao dicionário de dados retornou 10 tabelas, restrições P = 10, U = 9, R = 16, C = 28 e 3 índices.
- `03_dml.sql`: commit concluído, com 4, 7, 8, 5, 7, 10, 12, 5, 16 e 7 registros nas dez tabelas.
- `04_dql.sql`: a consulta 1 retornou 12 linhas, a consulta 2 retornou 4 e a consulta 3 retornou 5, sendo a última um destino sem trajeto, com as colunas da alternativa nulas.

```sql
SELECT 'tabelas' AS item, COUNT(*) AS qtd FROM user_tables WHERE table_name LIKE 'PH\_%' ESCAPE '\'
UNION ALL
SELECT 'restricao ' || constraint_type, COUNT(*) FROM user_constraints
 WHERE table_name LIKE 'PH\_%' ESCAPE '\' AND constraint_name NOT LIKE 'SYS%' GROUP BY constraint_type
UNION ALL
SELECT 'indices', COUNT(*) FROM user_indexes WHERE index_name LIKE 'IX\_PH\_%' ESCAPE '\';
```

Depois dessa execução, só uma linha de comentário do cabeçalho do `02_ddl.sql` foi alterada.

**Antes disso, em 12/11/2026:** os scripts foram testados em PostgreSQL 16, com os tipos de dado convertidos, incluindo 15 inserções e exclusões inválidas que o banco precisa recusar.

**API x banco, em 16/11/2026:** os nomes de tabelas e colunas usados nos DAOs de `backend/java` foram comparados com o `02_ddl.sql`. As 10 tabelas são usadas e todas as colunas referenciadas existem. Essa conferência é só dos nomes: a API não foi executada contra o banco aqui.

## Origem dos dados de exemplo

- **Reais:** paradas, linhas, pares, alternativas e etapas vêm do cálculo do módulo de Dynamic Programming sobre o GTFS da ARTESP (versão 20261007), no cenário "dia útil, das 6h às 9h".
- **Simulados:** os indicadores de ocorrência e as consultas. Estão marcados no próprio banco (`fl_simulado = 'S'` na fonte e `fl_teste = 'S'` nas consultas).
- **Vazias:** as coordenadas das paradas ficam nulas até serem preenchidas com os valores do GTFS.

## Pendências

- Trocar os indicadores simulados pelo cálculo com os dados da SSP-SP.
- Preencher latitude e longitude das paradas a partir do `stops.txt` do GTFS.
- Carregar o resultado completo do módulo de Dynamic Programming, além dos pares de exemplo.
