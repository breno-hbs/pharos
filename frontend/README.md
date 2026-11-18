# PHAROS Frontend

Interface web do piloto no Capão Redondo com Next.js e TypeScript.

```sh
npm ci
npm run dev
```

Abra [localhost:3000](http://localhost:3000).

## Integração com a API

O front consome a API Java do PHAROS (`backend/java`), publicada no Render. A URL padrão é `https://pharos-api-kaxr.onrender.com`; para apontar para outra (por exemplo, a API rodando local), crie `frontend/.env.local` com:

```
NEXT_PUBLIC_API_URL=http://localhost:8080
```

| Tela | Chamada |
| --- | --- |
| Planejamento (origem e destino) | `GET /paradas?selecionavel=S` |
| Comparação e detalhes | `GET /trajetos?origem=&destino=&dia=UTIL&hora=&ordenar=` (`ordenar`: TEMPO, DISTANCIA ou BALDEACOES, vindo da preferência escolhida) |
| Registro anônimo da consulta | `POST /consultas` ao abrir os trajetos e `PUT /consultas/{id}` com a alternativa aberta nos detalhes (`flTeste=S`) |

Pontos de atenção:

- O plano gratuito do Render dorme. A primeira chamada pode levar cerca de um minuto, e a tela avisa enquanto carrega.
- O banco de exemplo só tem trajetos calculados para o pico da manhã de dia útil (6h às 9h), por isso o horário padrão é 07:30. Fora dessa janela, ou para pares sem cadastro, a API responde `SEM_DADOS` e a tela mostra a mensagem dela.
- A API não calcula caminhada. Por isso a preferência "Menos caminhada" virou "Menor distância" e as etapas a pé saíram dos detalhes; baldeações acontecem sempre na mesma parada.
- Continuam simulados: relatos comunitários, pins, confirmações e o mapa ilustrativo (o banco de exemplo não tem coordenadas). Indicadores de ocorrências vêm da API e aparecem marcados como simulados quando a fonte é a de testes.
- Os relatos (observações) não têm endpoint na API; o envio continua em memória.

Para verificar o projeto, execute `npm run typecheck` e `npm run build`.

O cenário padrão vai de uma parada comum ao Terminal Metrô Capão Redondo. Inverta origem e destino para inspecionar o estado sem alternativas cadastradas. Envio de relatos, confirmações e contestações são simulações da interface e ficam em memória durante o uso.
