# PHAROS — API REST (Java / Spring Boot)

Global Solution 2026.2 · FIAP · Domain Driven Design – Java

**Equipe:** Pharos · **Deploy:** https://pharos-api-kaxr.onrender.com (teste rápido: `/saude`)

API REST que serve o front-end do PHAROS. O cálculo das rotas (Floyd-Warshall) roda antes, em Python
(módulo Dynamic Programming), e o resultado fica no Oracle. **A API só consulta os trajetos calculados**,
mantém o cadastro de paradas e linhas e registra as consultas.

## Requisitos
- JDK 21
- Maven 3.9+ (ou o Maven do IntelliJ IDEA)
- Acesso ao Oracle da FIAP (`oracle.fiap.com.br:1521`, SID `ORCL`) com as tabelas `PH_*` criadas pelos scripts `database/02_ddl.sql` e `03_dml.sql`. Quem mantém o banco já executou os scripts; **não rode o `02_ddl.sql` de novo**, ele apaga e recria as tabelas.

## Variáveis de ambiente (nunca versionar credenciais)

| Variável | Exemplo |
|---|---|
| `ORACLE_URL` | `jdbc:oracle:thin:@oracle.fiap.com.br:1521:ORCL` |
| `ORACLE_USER` | usuário do schema onde as tabelas `PH_*` foram criadas (peça ao responsável pelo banco) |
| `ORACLE_PASSWORD` | senha do usuário |
| `PORT` | opcional (padrão 8080; o Render define sozinho) |

Veja `.env.example`. No IntelliJ: *Run > Edit Configurations > Environment variables*.

## Executar localmente
```bash
cd backend/java
mvn spring-boot:run
# ou
mvn package && java -jar target/pharos-api.jar
```
Teste: `GET http://localhost:8080/saude` → `{"api":"UP","banco":"UP"}`.

## Testes unitários (camada de negócio, sem banco)
```bash
mvn test
```

## Estrutura (padrão visto em aula)
```
br.com.pharos
├── dominio/          Model: 10 classes espelhando as tabelas PH_* + objetos de resposta
├── infraestrutura/   ConexaoOracle (JDBC) e DAOs
├── servico/          Regras de negócio (BO)
├── controller/       Endpoints REST
├── excecao/          Exceções e tratamento padronizado de erros
└── config/           CORS
```
Fluxo: Controller → Service (BO) → DAO → Oracle.

## Endpoints

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| GET | `/saude` | API e banco disponíveis | 200 / 503 |
| GET | `/paradas?selecionavel=S` | lista paradas (filtro opcional) | 200 |
| GET | `/paradas/{id}` | uma parada | 200 / 404 |
| POST | `/paradas` | cadastra parada | 201 |
| PUT | `/paradas/{id}` | atualiza parada | 200 |
| DELETE | `/paradas/{id}` | exclui parada (409 se em uso) | 204 |
| GET/POST/PUT/DELETE | `/linhas`, `/linhas/{id}` | CRUD de linhas | idem |
| GET | `/trajetos?origem=&destino=&cenario=&ordenar=` | alternativas, etapas e indicadores (informe `cenario` **ou** `dia` + `hora`) | 200 / 400 / 404 |
| GET | `/trajetos?origem=&destino=&dia=UTIL&hora=7` | idem, escolhendo o cenário por dia e hora | 200 |
| GET | `/cenarios`, `/fontes`, `/tipos-ocorrencia` | tabelas de apoio | 200 |
| GET | `/consultas`, `/consultas/{id}` | consultas registradas | 200 / 404 |
| POST | `/consultas` | registra consulta anônima | 201 |
| PUT | `/consultas/{id}` | avaliação (1 a 5) e alternativa escolhida | 200 |
| DELETE | `/consultas/{id}` | exclui consulta | 204 |

`ordenar`: `TEMPO` (padrão), `DISTANCIA`, `BALDEACOES` ou `OCORRENCIAS`.

Erros seguem sempre o formato `{timestamp, status, erro, mensagem, caminho}` com 400, 404, 405, 409 ou 500.

## Exemplos de chamada
```bash
curl https://pharos-api-kaxr.onrender.com/saude
curl "https://pharos-api-kaxr.onrender.com/trajetos?origem=2&destino=1&cenario=UTIL_MANHA"
curl -X POST https://pharos-api-kaxr.onrender.com/paradas -H "Content-Type: application/json" \
  -d '{"cdParadaGtfs":"TESTE01","nmParada":"Parada de teste","nmMunicipio":"São Paulo","flTerminal":"N","flSelecionavel":"N","idFonte":4}'
```
No plano gratuito do Render a API dorme após um tempo sem uso: a primeira chamada pode levar cerca de 50 segundos.
Os ids são gerados pelo banco: não envie `idParada` / `idLinha` no POST.

## Escopo do protótipo
Relatos comunitários (pins, confirmar/contestar, moderação) e etapas a pé são **simulados no front-end**;
não há tabelas para eles no banco.

## Deploy (Render)
O Render não tem ambiente Java nativo: criar um *Web Service* com ambiente **Docker**, diretório raiz
`backend/java`, e cadastrar `ORACLE_URL`, `ORACLE_USER` e `ORACLE_PASSWORD` em *Environment*.
