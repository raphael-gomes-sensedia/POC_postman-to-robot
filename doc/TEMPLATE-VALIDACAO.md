# Template de Validação: Testes Gerados POC

## 1. Objetivo

Este documento define o template de validação para a POC do gerador de testes Robot Framework a partir de Postman Collections. Serve como referência de como cada teste `.robot` gerado deve ser construído e como validar se o output está aceitável.

---

## 2. Template de Validação (10 Checkpoints)

Cada teste gerado deve passar nos seguintes checkpoints:

| # | Checkpoint | O que validar | Status |
|---|-----------|---------------|--------|
| 1 | **Estrutura de seções** | Arquivo possui `*** Settings ***`, `*** Variables ***`, `*** Test Cases ***` | [ ] |
| 2 | **Resource base-api.robot** | `Resource  ../api-tests/base-api.robot` presente em Settings | [ ] |
| 3 | **Documentation** | Documentação multi-linha com nome da API, operações e comando de execução | [ ] |
| 4 | **Variáveis resolvidas** | Todas as `{{variaveis}}` da collection substituídas por `${variavel}` com valor | [ ] |
| 5 | **Test Cases cobrem requests** | Cada request do Postman tem um Test Case correspondente | [ ] |
| 6 | **HTTP correto** | Method correto (GET/POST/PUT/DELETE), URL resolvida, session criada | [ ] |
| 7 | **Headers presentes** | `client_id` e `access_token` presentes quando exigidos pelo request | [ ] |
| 8 | **Status Should Be** | `Status Should Be` com código HTTP correto presente | [ ] |
| 9 | **Assertions do JS** | Mesmas validações do script JS do Postman (body, campos, schemas) | [ ] |
| 10 | **Executável** | Pode ser executado com `robot` sem erro de sintaxe | [ ] |

**Score mínimo**: 8/10 checkpoints para aceite da POC.

---

## 3. Template de Arquivo `.robot` Gerado

### 3.1. Estrutura Completa

```robot
*** Settings ***
Documentation    {NOME_GRUPO} - {DESCRICAO}
...              Collection: {NOME_COLLECTION}
...              command to run tests:
...              robot -d results/{nome_grupo} {caminho_do_arquivo}.robot

Resource        ../api-tests/base-api.robot
{TEST_SETUP}    {SE_HOUVER}

*** Variables ***
{VARIAVEIS_DA_COLLECTION_RESOLVIDAS}

*** Test Cases ***
{NOME_TESTE_1}
    {PASSOS_DO_TESTE_1}

{NOME_TESTE_2}
    {PASSOS_DO_TESTE_2}

*** Keywords ***
{KEYWORDS_REUTILIZAVEL}
```

### 3.2. Regras de Preenchimento

#### Settings

```robot
*** Settings ***
Documentation    [F001] GET /pedidos - Sucesso e Erros
...              Collection: API Conecta Pedidos v1.6
...              Operations:
...              - GET /pedidos (sucesso, body vazio, erros 400/401/403)
...              - GET /pedidos/{id} (sucesso, erros 400/401/403/404)
...              command to run tests:
...              robot -d results\f001_pedidos api-tests\f001_pedidos.robot

Resource        ../api-tests/base-api.robot
```

#### Variables

```robot
*** Variables ***
${client_id_og}         883b0194-10a8-451e-bb38-1e61828c6f8b
${client_secret_og}     f977d249-2b62-4ce8-aa50-08c75d0afd0a
${oauth}                0308eea9-7e6e-4fe3-80ee-42c988acb48e
${baseUrl}              https://api.essilor.com.br
${enviroment}           dev
${api}                  conecta-pedidos
${version}              v1
${random_id_pedido}     a30887d1-b9d7-45b8-801f-0e1b1e2a4c98
${token_invalido}       eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
${client_id_invalido}   883b0194-10a8-451e-bb38-1e61828c6f00
${oauth_invalido}       i000e937-2b75-4d73-9a72-acb1c7w00j00
${laboratorio_og}       04693846000105
${id_pedido}            a30887d1-b9d7-45b8-801f-0e1b1e2a4c98
${lab_nao_autorizado}   40506388000111
```

#### Test Cases

```robot
*** Test Cases ***
[200] GET /pedidos Sucesso - sem params - retorna pedidos data=hoje
    Create Session API Oauth
    &{headers}=    Create Dictionary    client_id=${client_id_og}    access_token=${oauth}
    ${response}=    GET On Session    api-in-test    /pedidos    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    # Assertions traduzidas do Postman
    Status Should Be    200    ${api_response}
    Run Keyword And Continue On Failure    Should Be Equal As Numbers    ${response.status_code}    200
    Run Keyword And Continue On Failure    Should Be Equal As Numbers    ${response.status_code}    206

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Not Be Empty    ${json_response}[pedidos]
    ${totalItens}=    Get Length    ${json_response}[pedidos]
    Should Be True    ${totalItens} > 0

    Validate ResponseTime
    Validate Header Content Type    application/json

[400] GET /pedidos Intervalo de datas invalido
    Create Session API Oauth
    &{headers}=    Create Dictionary    client_id=${client_id_og}    access_token=${oauth}
    ${response}=    GET On Session    api-in-test    /pedidos?dataInicio=2025-09-22&dataFim=2025-09-18    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    # Assertions traduzidas do Postman
    Status Should Be    400    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Be Equal As Strings    ${json_response}[0][codigo]    400
    Should Be Equal As Strings    ${json_response}[0][mensagem]    A 'dataInicio' deve ser menor ou igual à 'dataFim'

    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_schema.json

[401] GET /pedidos Access Token inválido
    Create Session API Oauth
    &{headers}=    Create Dictionary    client_id=${client_id_og}    access_token=${token_invalido}
    ${response}=    GET On Session    api-in-test    /pedidos    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    # Assertions traduzidas do Postman
    Status Should Be    401    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Be Equal As Strings    ${json_response}[0][codigo]    401
    Should Be Equal As Strings    ${json_response}[0][mensagem]    Access_token inválido.

    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_schema.json
```

#### Keywords (quando aplicável)

```robot
*** Keywords ***
Response 200 - Pedidos
    Status Should Be    200    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Not Be Empty    ${json_response}[pedidos]
    Should Contain    ${json_response}    pedidos

    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/f001_pedidos_schema.json

Response 200 - Body Vazio
    Status Should Be    200    ${api_response}

    ${body}=    Convert To String    ${api_response.content}
    ${response-length}=    Get Length    ${api_response.content}

    IF    '${response-length}' == '0'
        Should Be Empty    ${body}
    ELSE
        ${json_response}=    Set Variable    ${api_response.json()}
        Should Be Equal As Strings    ${json_response}[0][codigo]    200
        Should Be Equal As Strings    ${json_response}[0][mensagem]    Servico disponivel.
    END

Response 400 - Erro
    [Arguments]    ${codigo_erro}    ${msg_erro}
    Status Should Be    400    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Be Equal As Strings    ${json_response}[0][codigo]    ${codigo_erro}
    Should Be Equal As Strings    ${json_response}[0][mensagem]    ${msg_erro}

    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_schema.json

Response 401 - Token Invalido
    Status Should Be    401    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Be Equal As Strings    ${json_response}[0][codigo]    401
    Should Be Equal As Strings    ${json_response}[0][mensagem]    Access_token inválido.

    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_schema.json
```

---

## 4. Exemplo de Input (Postman) e Output (.robot) Esperado

### 4.1. Input: Postman Collection

```json
{
  "name": "[200] GET /pedidos Sucesso - sem params - retorna pedidos data=hoje",
  "request": {
    "method": "GET",
    "header": [
      {"key": "client_id", "value": "{{client_id_og}}", "type": "text"},
      {"key": "access_token", "value": "{{oauth}}", "type": "text"}
    ],
    "url": {
      "raw": "{{baseUrl}}/{{enviroment}}/{{api}}/{{version}}/pedidos",
      "protocol": "https",
      "host": ["{{baseUrl}}"],
      "path": ["{{enviroment}}", "{{api}}", "{{version}}", "pedidos"]
    }
  },
  "event": [
    {
      "listen": "test",
      "script": {
        "exec": [
          "var jsonData = pm.response.json();",
          "",
          "var codigo = \"200\";",
          "pm.test(\"Status code is 200\", function () {",
          "    pm.expect(pm.response.code).to.eql(codigo);",
          "});",
          "",
          "pm.test(\"JSON Schema is valid\", function () {",
          "    pm.response.to.have.jsonSchema(jsonSchema);",
          "});",
          "",
          "pm.test(\"Calcula a quantidade de itens\", function () {",
          "    const pedidos = jsonData.pedidos;",
          "    const totalItens = pedidos.length;",
          "    pm.expect(totalItens, \"O array 'pedidos' deve conter itens\").to.be.above(0);",
          "});"
        ]
      }
    }
  ]
}
```

### 4.2. Output: Arquivo `.robot` Gerado

```robot
*** Settings ***
Documentation    [F001] GET /pedidos - Sucesso [200,206]
...              Collection: API Conecta Pedidos v1.6
...              Operations:
...              - GET /pedidos (sem params, com filtros, body vazio)
...              command to run tests:
...              robot -d results\f001_pedidos api-tests\f001_pedidos.robot

Resource        ../api-tests/base-api.robot

*** Variables ***
${client_id_og}         883b0194-10a8-451e-bb38-1e61828c6f8b
${oauth}                0308eea9-7e6e-4fe3-80ee-42c988acb48e

*** Test Cases ***
[200] GET /pedidos Sucesso - sem params - retorna pedidos data=hoje
    Create Session API Oauth
    &{headers}=    Create Dictionary    client_id=${client_id_og}    access_token=${oauth}
    ${response}=    GET On Session    api-in-test    /pedidos    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    # Assertions traduzidas do Postman
    Status Should Be    200    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Not Be Empty    ${json_response}[pedidos]
    ${totalItens}=    Get Length    ${json_response}[pedidos]
    Should Be True    ${totalItens} > 0

    Validate ResponseTime
    Validate Header Content Type    application/json
```

---

## 5. Exemplo de Input com Schema Inline e Output com IA

### 5.1. Input: Postman com Schema Inline no JS

```json
{
  "name": "[200] GET /pedidos Sucesso - sem params",
  "event": [
    {
      "listen": "test",
      "script": {
        "exec": [
          "const jsonSchema = {",
          "    \"type\": \"object\",",
          "    \"properties\": {",
          "        \"pedidos\": {",
          "            \"type\": \"array\",",
          "            \"items\": {",
          "                \"type\": \"object\",",
          "                \"properties\": {",
          "                    \"id\": { \"type\": \"string\", \"format\": \"uuid\" },",
          "                    \"dataCriacao\": { \"type\": \"string\", \"minLength\": 1 },",
          "                    \"integradoLab\": { \"type\": \"boolean\" },",
          "                    \"laboratorio\": { \"type\": \"string\" },",
          "                    \"otica\": { \"type\": \"string\" }",
          "                },",
          "                \"required\": [\"id\", \"dataCriacao\", \"integradoLab\", \"laboratorio\", \"otica\"]",
          "            }",
          "        }",
          "    },",
          "    \"required\": [\"pedidos\"]",
          "};"
        ]
      }
    }
  ]
}
```

### 5.2. Output: Arquivo `.robot` Gerado (com IA extraindo schema)

```robot
*** Settings ***
Documentation    [F001] GET /pedidos - Sucesso [200,206]
...              Collection: API Conecta Pedidos v1.6
...        command to run tests:
...        robot -d results\f001_pedidos api-tests\f001_pedidos.robot

Resource        ../api-tests/base-api.robot

*** Variables ***
${client_id_og}         883b0194-10a8-451e-bb38-1e61828c6f8b
${oauth}                0308eea9-7e6e-4fe3-80ee-42c988acb48e

*** Test Cases ***
[200] GET /pedidos Sucesso - sem params - retorna pedidos data=hoje
    Create Session API Oauth
    &{headers}=    Create Dictionary    client_id=${client_id_og}    access_token=${oauth}
    ${response}=    GET On Session    api-in-test    /pedidos    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    # Assertions traduzidas do Postman
    Status Should Be    200    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Not Be Empty    ${json_response}[pedidos]
    ${totalItens}=    Get Length    ${json_response}[pedidos]
    Should Be True    ${totalItens} > 0

    # Schema validation (IA extraiu o schema inline do JS)
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/f001_pedidos_schema.json

    Validate ResponseTime
    Validate Header Content Type    application/json
```

### 5.3. Schema JSON Gerado pela IA

Arquivo `schemas/f001_pedidos_schema.json`:
```json
{
  "type": "object",
  "required": ["pedidos"],
  "properties": {
    "pedidos": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "dataCriacao", "integradoLab", "laboratorio", "otica"],
        "properties": {
          "id": {"type": "string", "format": "uuid"},
          "dataCriacao": {"type": "string", "minLength": 1},
          "integradoLab": {"type": "boolean"},
          "laboratorio": {"type": "string"},
          "otica": {"type": "string"}
        }
      }
    }
  }
}
```

---

## 6. Exemplo de Input com Variável Encadeada e Output

### 6.1. Input: Postman com Variável Encadeada

**Teste 1 - F001 GET /pedidos (extrai random_id_pedido):**
```json
{
  "name": "[200] GET /pedidos Sucesso - sem params",
  "event": [{
    "listen": "test",
    "script": {
      "exec": [
        "const jsonData = pm.response.json();",
        "const pedidos = jsonData.pedidos;",
        "const randomIndex = Math.floor(Math.random() * pedidos.length);",
        "const randomId = pedidos[randomIndex].id;",
        "pm.collectionVariables.set(\"random_id_pedido\", randomId);"
      ]
    }
  }]
}
```

**Teste 2 - F002 GET /pedidos/{id} (usa random_id_pedido):**
```json
{
  "name": "[200] GET /pedidos/{id} Sucesso",
  "request": {
    "method": "GET",
    "header": [
      {"key": "client_id", "value": "{{client_id_og}}"},
      {"key": "access_token", "value": "{{oauth}}"}
    ],
    "url": {"raw": "{{baseUrl}}/{{enviroment}}/{{api}}/{{version}}/pedidos/{{random_id_pedido}}"}
  }
}
```

### 6.2. Output: Arquivos `.robot` Gerados

**Arquivo 1 - `f001_pedidos.robot`:**
```robot
*** Settings ***
Documentation    [F001] GET /pedidos
...              Collection: API Conecta Pedidos v1.6
...        command to run tests:
...        robot -d results\f001_pedidos api-tests\f001_pedidos.robot

Resource        ../api-tests/base-api.robot

*** Variables ***
${client_id_og}         883b0194-10a8-451e-bb38-1e61828c6f8b
${oauth}                0308eea9-7e6e-4fe3-80ee-42c988acb48e
${random_id_pedido}     ${EMPTY}

*** Test Cases ***
[200] GET /pedidos Sucesso - sem params - retorna pedidos data=hoje
    Create Session API Oauth
    &{headers}=    Create Dictionary    client_id=${client_id_og}    access_token=${oauth}
    ${response}=    GET On Session    api-in-test    /pedidos    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    Status Should Be    200    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Not Be Empty    ${json_response}[pedidos]
    ${totalItens}=    Get Length    ${json_response}[pedidos]
    Should Be True    ${totalItens} > 0

    # Variável encadeada: IA traduziu Math.random() + collectionVariables.set()
    IF    ${totalItens} > 0
        ${randomIndex}=    Evaluate    int(${totalItens} * 0.5)
        ${randomId}=    Get From List    ${json_response}[pedidos]    ${randomIndex}
        Set Test Variable    ${random_id_pedido}    ${randomId}
    END

    Validate ResponseTime
```

**Arquivo 2 - `f002_pedidos_id.robot`:**
```robot
*** Settings ***
Documentation    [F002] GET /pedidos/{id}
...              Collection: API Conecta Pedidos v1.6
...        command to run tests:
...        robot -d results\f002_pedidos_id api-tests\f002_pedidos_id.robot

Resource        ../api-tests/base-api.robot

*** Variables ***
${client_id_og}         883b0194-10a8-451e-bb38-1e61828c6f8b
${oauth}                0308eea9-7e6e-4fe3-80ee-42c988acb48e

*** Test Cases ***
[200] GET /pedidos/{id} Sucesso
    Create Session API Oauth
    &{headers}=    Create Dictionary    client_id=${client_id_og}    access_token=${oauth}
    ${response}=    GET On Session    api-in-test    /pedidos/${random_id_pedido}    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    Status Should Be    200    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Should Not Be Empty    ${json_response}[id]
    Should Not Be Empty    ${json_response}[idPedidoOtica]

    Validate ResponseTime
```

---

## 7. Checklist de Validação por Tipo de Teste

### 7.1. Teste GET Simples

- [ ] `Create Session API Oauth` ou `Create Session API Proxy`
- [ ] `&{headers}=    Create Dictionary` com `client_id` e `access_token`
- [ ] `${response}=    GET On Session` com path e headers
- [ ] `Set Test Variable    ${api_response}    ${response}`
- [ ] `Status Should Be    {STATUS}`
- [ ] Validações de body (se houver assertions no JS)
- [ ] `Validate ResponseTime`
- [ ] `Validate Header Content Type    application/json`

### 7.2. Teste POST com Body

- [ ] `Create Session API Oauth` ou `Create Session API Proxy`
- [ ] `&{headers}=    Create Dictionary` com `client_id` e `access_token`
- [ ] `&{body}=    Create Dictionary` com campos do request body
- [ ] `${response}=    POST On Session` com `json=${body}` e headers
- [ ] `Set Test Variable    ${api_response}    ${response}`
- [ ] `Status Should Be    {STATUS}`
- [ ] Validações de body
- [ ] `Validate Json By Schema File` (se houver schema)

### 7.3. Teste de Erro

- [ ] `Create Session API Oauth` ou `Create Session API Proxy`
- [ ] Headers com dados inválidos (token inválido, client_id inválido, etc.)
- [ ] `${response}=    GET/POST On Session` com `expected_status=any`
- [ ] `Status Should Be    {STATUS}`
- [ ] Validação de `erros[].codigo` e `erros[].mensagem`
- [ ] `Validate Json By Schema File    ${EXECDIR}/schemas/error_response_schema.json`

### 7.4. Teste com Variável Encadeada

- [ ] Primeiro teste: `Set Test Variable    ${variavel}    ${json_response}[campo]`
- [ ] Testes subsequentes: usar `${variavel}` na URL ou body
- [ ] Documentação indicando dependência entre testes

---

## 8. Score de Aceite

| Score | Resultado | Ação |
|-------|-----------|------|
| 10/10 | Excelente | Teste gerado idêntico ao hand-written. Pronto para produção. |
| 9/10 | Muito Bom | Pequenos ajustes. Pronto para produção. |
| 8/10 | Bom | Aceitável para POC. Revisão manual recomendada. |
| 7/10 | Razoável | Falhas significativas. Requer ajustes no gerador. |
| < 7/10 | Insuficiente | Rejeitado. Analisar gaps e refatorar gerador. |

**Meta da POC**: Score >= 8/10 em pelo menos 80% dos testes gerados.
