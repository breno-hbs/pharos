# Guia de Contribuição — Pharos

Este documento estabelece as regras de colaboração e versionamento para os quatro integrantes da equipe da Global Solution FIAP 2026.2.

## 1. Estratégia de branches

**main**
- Contém a versão estável e validada do projeto.
- Recebe alterações somente por Pull Request a partir de `dev`.
- Não deve receber commits diretamente.

**dev**
- Branch de integração das funcionalidades.
- Recebe Pull Requests das branches de desenvolvimento.
- As alterações devem ser revisadas antes do merge.

**feature/**
- Branches utilizadas para implementar funcionalidades e tarefas específicas.
- Devem ser criadas a partir de `dev`.
- Devem ter nomes claros e objetivos.

Exemplos:
- `feature/java-api`
- `feature/database-schema`
- `feature/frontend-routes`
- `feature/python-routing`
- `feature/network-topology`

## 2. Fluxo de desenvolvimento

1. Atualizar a branch `dev` local.
2. Criar uma branch `feature/*` a partir de `dev`.
3. Implementar a tarefa.
4. Realizar commits com mensagens descritivas.
5. Enviar a branch para o GitHub.
6. Abrir um Pull Request com destino à `dev`.
7. Solicitar revisão de outro integrante.
8. Corrigir os problemas apontados.
9. Realizar o merge após revisão e testes aplicáveis.

**Promoção para produção:** quando uma versão estiver validada na `dev`, abrir um Pull Request de `dev` para `main`.

## 3. Padrão de commits

Utilizar mensagens curtas e descritivas.

Padrão recomendado:

`tipo: descrição`

Exemplos:
- `feat: adiciona endpoint de consulta de rotas`
- `fix: corrige validação de parâmetros`
- `docs: atualiza documentação da API`
- `test: adiciona testes de serviços`
- `refactor: reorganiza camada de negócio`
- `chore: configura projeto Spring Boot`

## 4. Regras de Pull Request

Todo Pull Request deverá informar:

- Qual tarefa está sendo implementada.
- O que foi alterado.
- Como a alteração foi testada.
- Se existem limitações ou pendências.
- Se há impacto em outras partes do projeto.

**Regras de revisão:**
- Preferencialmente, pelo menos um integrante diferente do autor deve revisar.
- Não aprovar o próprio código sem revisão quando houver outro integrante disponível.
- Resolver comentários relevantes antes do merge.
- Não integrar alterações que comprometam funcionalidades existentes.
- Não realizar force push nas branches `main` e `dev`.

## 5. Segurança

- Nunca enviar senhas, tokens ou credenciais para o repositório.
- Utilizar variáveis de ambiente para informações sensíveis.
- Não versionar arquivos `.env` contendo segredos.
- Não utilizar dados pessoais reais sem autorização e necessidade justificada.
- Identificar claramente dados fictícios ou simulados.

## 6. Organização das entregas

Cada integrante é responsável por versionar os arquivos técnicos de suas tarefas e manter sua documentação atualizada.

As entregas devem respeitar a estrutura de pastas definida pela equipe.

Os status, responsáveis e prazos continuarão sendo acompanhados no Notion.

## 7. Regras finais

- Não realizar merges diretamente na `main` ou `dev` fora do fluxo combinado.
- Não excluir branches de outros integrantes sem alinhamento.
- Comunicar alterações que afetem APIs, banco de dados ou integrações.
- Corrigir conflitos de merge antes de integrar funcionalidades.
- Manter a branch `main` estável para a entrega final da Global Solution.

**Prazo oficial:** 19/11/2026, às 23h55.
