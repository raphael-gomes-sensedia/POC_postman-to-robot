---
name: robot-framework-knowledge
description: Conhecimento completo do framework Robot usado pelo time de QA Essilor: bibliotecas, keywords base, sessões HTTP, autenticação JWT/OAuth, validação de schemas, mensagens de erro e mapeamento Postman→Robot
license: MIT
compatibility: opencode
metadata:
  audience: qa-engineers
  workflow: robot-test-automation
  version: "2.0"
  last_updated: "2026-07-13"
---

## O que eu faço
- Documento a estrutura do projeto Robot Framework usado pelo time de QA Essilor
- Forneço as bibliotecas, variáveis e keywords base do arquivo `api-tests/base-api.robot`
- Explico como criar sessões HTTP, autenticar (JWT/OAuth), validar respostas e schemas
- Descrevo o padrão de organização de diretórios, variáveis globais e nomes de APIs
- **Mapeio cada elemento de uma Collection Postman para seu equivalente em Robot Framework**

## Quando usar
Use esta skill sempre que precisar entender como o time Essilor estrutura testes Robot: quais bibliotecas importar, como configurar sessões, como autenticar, como validar respostas e como usar schemas. Também use ao gerar novos arquivos .robot para garantir que sigam o padrão estabelecido.

## Projeto Robot (Essilor_backend)

### Estrutura de diretórios
```
projeto/
├── api-tests/
│   └── base-api.robot          (arquivo central: bibliotecas + keywords + variáveis)
├── api-<modulo>/
│   └── <teste>.robot           (testes por módulo de API)
├── schemas/
│   └── <nome>_schema.json      (schemas JSON para validação)
├── resources/
│   └── payload_<nome>.json     (templates de payload)
├── data/                        (arquivos CSV para DataDriver)
├── logs/                        (output robot: log.html, report.html)
└── results/                     (resultados de execução)
```

## Mapeamento Postman → Robot Framework

### Request → Test Case
| Postman | Robot Framework |
|---------|----------------|
| Collection Item (request) | Test Case (dentro de `*** Test Cases ***`) |
| `item.name` | Nome do Test Case (formatado conforme padrão T<NN>) |
| `request.method` | Verbo HTTP: `GET On Session`, `POST On Session`, `PUT On Session`, `DELETE On Session` |
| `request.url.raw` | URL construída via `Create Session` + path (`${oper_*}`) |
| `request.header[]` | `&{headers}= Create Dictionary key1=val1 key2=val2` |
| `request.body.raw` | Payload JSON salvo em `resources/` e carregado via `Get Payload Orcamento` |
| `request.auth` | Define qual autenticação usar (JWT, OAuth, ou nenhuma) |

### Test Script → Keywords de Validação
| Postman Script | Robot Equivalent |
|----------------|------------------|
| `pm.response.to.have.status(XXX)` | `Status Should Be XXX ${api_response}` |
| `pm.response.to.have.jsonSchema(schema)` | `Validate Json By Schema File ${json} ${EXECDIR}/schemas/<nome>.json` |
| `pm.expect(json.xxx).to.equal("yyy")` | `Should Be Equal As Strings ${json}[xxx] yyy` |
| `pm.expect(json.xxx).to.not.be.empty` | `Should Not Be Empty ${json}[xxx]` |
| `pm.expect(json.xxx).to.include("yyy")` | `Should Contain ${json}[xxx] yyy` |
| `pm.expect(json.xxx).to.be.true` | `Should Be True ${json}[xxx]` |
| `pm.expect(array).to.have.lengthOf(N)` | `Length Should Be ${array} N` |
| `pm.response.to.have.header("X-Custom")` | `Get From Dictionary ${api_response.headers} x-custom` |
| Extrair campo para variável | `Set Global Variable / Set Test Variable` |

### Regras de Autenticação
| Indício na Collection | Tipo | Sessão Robot |
|----------------------|------|-------------|
| Pasta da API contém "Proxy" | Proxy (JWT) | `Create Session API Proxy` + `POST Autenticação JWT` |
| Pasta da API contém "Adapter" | Adapter (OAuth) | `POST Autenticação Oauth` + `Create Session API Adapter` |
| Request usa /token com usuario/senha | JWT | `POST Autenticação JWT` |
| Request usa /access-token?grant_type=client_credentials | OAuth | `POST Autenticação Oauth` |
| URL contém "health" | Sem auth | Apenas `Create Session` + chamada HTTP |

### Cabeçalhos de Autenticação
```robot
# Para APIs Proxy (JWT)
&{headers}=    Create Dictionary    Content-Type=application/json
...    client_id=${client_id}    access_token=${jwt}    laboratorio=${@{dados_login}[3]}

# Para APIs Adapter (OAuth)
&{headers}=    Create Dictionary    Content-Type=application/json
...    client_id=${client_id}    access_token=${oauth}
```

### Mapeamento de Variáveis Postman → Robot
| Postman | Robot |
|---------|-------|
| `{{base_url}}` | `https://api.essilor.com.br` (hardcoded na sessão) |
| `{{env}}` | `${env}` (definido por Suite Setup) |
| `{{client_id}}` | `${client_id}` (definido no base-api.robot) |
| `{{client_secret}}` | `${client_secret}` (definido no base-api.robot) |
| `{{jwt}}` / `{{oauth}}` | `${jwt}` / `${oauth}` (definido na autenticação) |
| Variáveis de ambiente `{{var}}` | Extrair para `${var}` ou `@{var}` no .robot |

## Arquivo principal: api-tests/base-api.robot

### Bibliotecas importadas (obrigatórias)
```robot
Library         Collections
Library         DateTime
Library         ImapLibrary2
Library         JSONLibrary
Library         OperatingSystem
Library         RequestsLibrary
Library         String
```

### Variáveis de Ambiente e URLs
O projeto usa URLs no formato:
```
https://api.essilor.com.br/{env}/{api-name}/v1
```
Onde `env` pode ser: `dev`, `hml`, `sandbox`.

### Constantes de endpoints (${oper_*})
```robot
${oper_token}                   /token
${oper_oauth}                   /access-token?grant_type=client_credentials
${oper_health}                  /health
${oper_voucher}                 /voucher
${oper_orcamentos}              /orcamentos
${oper_pedidos}                 /pedidos
${oper_orcamentos_atacado}      /orcamentos-atacado
${oper_pedidos_atacado}         /pedidos-atacado
${oper_lp_orcamentos}           /lente-pronta/orcamentos
${oper_lp_pedidos}              /lente-pronta/pedidos
${oper_mfa_solicitacao}         /mfa/solicitacao
${oper_mfa_token}               /mfa/token
```

### Definição de APIs (@{api_*} - arrays de 3 elementos)
Cada API é um array: `[nome_api, versao_dev, versao_hml]`
```robot
@{api_auth_jwt}             autenticacao-jwt                      v1.58    v1.58
@{api_produtos_proxy}       gestao-produtos-laboratorio           v1.31    v1.30
@{api_pedidos_proxy}        gestao-pedidos-laboratorio            v1.107   v1.104
@{api_financeiro_proxy}     gestao-financeira-cliente-laboratorio v1.10    v1.10
@{api_conecta_pedidos}      conecta-pedidos                       v1.4     v1.4
@{api_produtos_sgo}         gestao-produtos-sgo                   v1.45    v1.45
@{api_pedidos_sgo}          gestao-pedidos-sgo                    v1.73    v1.73
@{api_financeiro_sgo}       gestao-financeira-sgo                 v1.12    v1.11
@{api_produtos_dataweb}     gestao-produtos-dataweb               v1.16    v1.16
@{api_pedidos_dataweb}      gestao-pedidos-dataweb                v1.19    v1.19
@{api_financeiro_dataweb}   gestao-financeira-dataweb             v1.8     v1.8
@{api_produtos_aco}         gestao-produtos-aco                   v1.5     v1.5
@{api_pedidos_aco}          gestao-pedidos-aco                    v1.9     v1.9
@{api_produtos_tecnolens}   gestao-produtos-tecnolens             v1.10    v1.10
@{api_pedidos_tecnolens}    gestao-pedidos-tecnolens              v1.13    v1.13
@{api_oracle_idcs}          idcs                                  v1.9     v1.7
@{api_onboarding_labog}     on-boarding                           v1.2     v1.2
```

### Usuários de Teste (@{user_*} - arrays de 4 elementos)
Cada usuário é um array: `[email, senha, cnpjOtica, cnpjLab]`
```robot
@{user_ceditop}     user_ceditop@teste.com     ceditop2021     95427308000124   03113110000158
@{user_comprol}     user_comprol@teste.com     comprol2021     15321752000121   27175413001135
@{user_grown}       teste_grown_rede@teste.com Essilor@2019    59189712000143   60570108000141
@{user_labminas}    proprietario_labminas@teste.com  Essilor@2019  26075599000388  27175413001054
@{user_labrio}      proprietario_labrio@teste.com    Essilor@2019  18070598000150  27175413000163
@{user_optilab}     proprietario_optilab2@teste.com  Essilor@2019  00506721000178  05266329000112
@{user_repro}       proprietario_repro@teste.com     Essilor@2019  21154956000207  83087056000152
@{user_rx}          proprietario_rx3@teste.com       Essilor@2019  11921550000160  11774798000145
@{user_tecnolens}   user_tecnolens@teste.com         tecnolens2021 26582805000184  40506388000111
@{user_unilab}      proprietario_unilab2@teste.com   Essilor@2019  05472947000461  08038666000140
```

### Mensagens de Erro (@{msg_*} - arrays de 3 elementos)
```robot
@{msg_token_invalido}             401  401       Access Token inválido.
@{msg_token_invalido_cert}        401  401       Access_token inválido.
@{msg_lab_nao_autorizado}         403  403       Consulta com laboratório não autorizado.
@{msg_header_sem_laboratorio}     422  422       É necessário informar o laboratório.
@{msg_erro_500}                   500  500       Tivemos uma falha momentânea...
@{msg_produto_nao_encontrado}     400  10.8.ORC15  O Produto ... não foi encontrado.
@{msg_id_pedido_otica_duplicado}  422  10.19.ORC33 Ordem de Compra já foi utilizada!...
@{msg_requisicao_invalida}        422  422       Requisição inválida...
@{msg_cor_armacao}                422  422       Cor não informada. (Olho esquerdo).
```

---

## Keywords Base (do base-api.robot)

### Criação de Sessões HTTP

**Create Session API Proxy** — Para APIs Proxy (requerem Basic Auth + JWT):
```robot
Create Session API Proxy
    [Arguments]         ${api}
    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/${api}/v1    auth=${auth}    verify=${True}
```

**Create Session API Adapter** — Para APIs Adapter (sem auth na URL):
```robot
Create Session API Adapter
    [Arguments]         ${api}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/${api}/v1    verify=${True}
```

**Create Session API Oauth** — Para OAuth client_credentials:
```robot
Create Session API Oauth
    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/oauth    auth=${auth}    verify=${True}
```

**Create Session API Oracle Proxy** — Para Oracle IDCS:
```robot
Create Session API Oracle Proxy
    [Arguments]         ${api}
    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/${api}    auth=${auth}    verify=${True}
```

**Create Session API Onboarding Proxy** — Para onboarding (sem arg):
```robot
Create Session API Onboarding Proxy
    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/on-boarding/v1    auth=${auth}    verify=${True}
```

### Autenticação

**POST Autenticação JWT** — Fluxo completo:
```robot
POST Autenticação JWT
    [Arguments]         ${usuario}     ${senha}
    Create Session API Proxy      ${api_auth_jwt}[0]
    &{body_login}=    Create Dictionary    usuario=${usuario}     senha=${senha}
    &{headers}=       Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ${response}=      POST On Session      api-in-test    ${oper_token}    json=${body_login}    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header Content Type    application/json
    ${status_code}=    Convert To String    ${response.status_code}
    IF    '${status_code}' == '201'
        ${json_response}=    Set Variable    ${response.json()}
        Set Test Variable    ${jwt}    ${json_response}[access_token]
    END
```

**POST Autenticação Oauth** — Para APIs Adapter:
```robot
POST Autenticação Oauth
    Create Session API Oauth
    &{headers}=     Create Dictionary    Content-Type=application/x-www-form-urlencoded    accept=application/json
    ${response}=    POST On Session    api-in-test    ${oper_oauth}    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header Content Type    application/json
    ${status_code}=    Convert To String    ${response.status_code}
    IF    '${status_code}' == '201'
        ${json_response}=    Set Variable    ${response.json()}
        Set Test Variable    ${oauth}    ${json_response}[access_token]
    END
```

### Validações

**Validate ResponseTime** — Valida < 15s:
```robot
Validate ResponseTime
    ${response_time_ms}=    Evaluate    ${api_response.elapsed.total_seconds()} * 1000
    Run Keyword And Ignore Error    Should Be True    ${response_time_ms} < ${EXPECTED_MAX_TIME_MS}
```

**Validate Header Content Type** — Valida application/json:
```robot
Validate Header Content Type
    [Arguments]     ${content_type}
    ${header}=    Get From Dictionary    ${api_response.headers}    content-type
    ${length}=    Get Length    ${header}
    IF    '${length}' != '4'
        Should Contain    ${header}    ${content_type}
    END
```

**Validate Header API Version** — Valida versão por ambiente:
```robot
Validate Header API Version
    [Arguments]    ${api_version_dev}    ${api_version_hml}    ${param_header}
    ${header}=    Get From Dictionary    ${api_response.headers}    ${param_header}
    IF    '${env}' == 'dev'
        Should Be Equal    ${header}    ${api_version_dev}
    ELSE
        Should Be Equal    ${header}    ${api_version_hml}
    END
```

### Utilitários

**Get Payload Orcamento** — Carrega template JSON:
```robot
Get Payload Orcamento
    [Arguments]     ${file_name}
    ${json_file}=   Get File    ${EXECDIR}/resources/${file_name}
    ${json_dict}=   Evaluate    json.loads($json_file)    json
    [Return]    ${json_dict}
```

**Gerar Id Pedido Aleatorio** — Gera ID único:
```robot
Gerar Id Pedido Aleatorio
    ${hoje}=             Get Current Date    result_format=datetime
    ${random_number}=    Generate Random String    4    [NUMBERS]
    ${random_idpedido}=  Catenate    SEPARATOR=    ${hoje.month}    ${hoje.day}    ${hoje.hour}    ${random_number}
    Set Global Variable    ${id_pedido_otica}    ${random_idpedido}
```

**Montar Datas** — Gera datas relativas:
```robot
Montar Datas
    ${hoje}=             Get Current Date    result_format=%Y-%m-%d
    Set Global Variable    ${data_hoje}    ${hoje}
    ${data_1_semana}=    Subtract Time From Date    ${data_hoje}    7 days    result_format=%Y-%m-%d
    Set Global Variable    ${data_inicio}    ${data_1_semana}
```

**Validar Mensagem de Erro** — Valida erro completo (status + schema + mensagem):
```robot
Validar Mensagem de Erro
    [Arguments]    ${status_code}    ${codigo_erro}    ${msg_erro}
    Status Should Be    ${status_code}    ${api_response}
    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_schema.json
    Ajustar Mensagem de Erro    ${codigo_erro}    ${msg_erro}
    FOR    ${item}    IN    @{response_erro}
        Should Be Equal As Strings    ${item}[codigo]    ${codigo_erro}
        Should Be Equal As Strings    ${item}[mensagem]    ${msg_erro}
    END
```

**Ajustar Mensagem de Erro** — Ajusta mensagem dinamicamente por laboratório:
```robot
Ajustar Mensagem de Erro
    [Arguments]    ${codigo_erro}    ${msg_erro}
    IF    '${codigo_erro}' == 'CAMPO_INVALIDO'
        ${concat_msg}=    Catenate    ${msg_erro}    ${id_pedido_otica}
        Set Test Variable    ${msg_erro}    ${concat_msg}
    END
    IF    '${codigo_erro}' == '10.19.ORC33'
        Montar Datas
        Set Test Variable    ${msg_erro}    Ordem de Compra já foi utilizada! Pedido Id: (${id_pedido_lab}) de (${data_hoje}).
    END
```

**Definir Dados do Laboratorio** — Configura laboratório e perfil (Suite Setup):
```robot
Definir Dados do Laboratorio
    [Arguments]    ${lab_teste}    ${arg_perfil}    ${test_env}
    Set Global Variable    ${env}    ${test_env}
    Set Global Variable    ${laboratorio}    ${lab_teste}
    # Mapeia o lab para @{dados_login} correspondente
    # Ajusta dinamicamente mensagens de erro específicas do lab
    # Configura perfil: Otica / Laboratorio / Essilor / LabOG
```

---

## Estrutura de Saída Esperada para Conversão Postman→Robot

Para cada API na Collection, gerar:
```
<diretorio_raiz>/
├── api-<modulo>/
│   └── <endpoint>.robot          (arquivo de teste)
├── schemas/
│   └── <endpoint>_schema.json    (schemas extraídos)
└── resources/
    └── payload_<nome>.json       (payloads extraídos)
```

### Regras de Organização
1. Cada `[F<NNN>]` da Collection vira **um arquivo .robot**
2. Requests de `Sucesso` viram **cenários positivos** (T01, T02...)
3. Requests de `Erro` viram **cenários negativos** (T01_NEG, T02_NEG...)
4. Schemas idênticos devem ser **deduplicados** em um único arquivo
5. Payloads devem ser **normalizados** (remoção de comentários, formatação consistente)

---

## Exemplo Completo de Conversão

### Collection Item (Postman)
```json
{
  "name": "[201] POST /orcamentos Sucesso - Receita Padrao",
  "request": {
    "method": "POST",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": { "mode": "raw", "raw": "{ \"idPedidoOtica\": \"12345\", \"receita\": {...} }" },
    "url": { "raw": "{{base_url}}/{{env}}/gestao-pedidos-laboratorio/v1/orcamentos" }
  },
  "event": [{
    "listen": "test",
    "script": {
      "exec": [
        "pm.test(\"Status 201\", function() { pm.response.to.have.status(201); });",
        "pm.test(\"Schema\", function() { pm.response.to.have.jsonSchema(schemaOrcamento); });"
      ]
    }
  }]
}
```

### Resultado (Robot)
```robot
*** Settings ***
Resource    ../api-tests/base-api.robot
Suite Setup    Definir Dados do Laboratorio    Ceditop    Otica    hml

*** Test Cases ***
T01 - Modulo Pedidos - Orcamento - Receita Padrao
    POST Autenticação JWT    @{dados_login}[0]    @{dados_login}[1]
    Create Session API Proxy    @{api_pedidos_proxy}[0]
    &{headers}=    Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt}    laboratorio=@{dados_login}[3]
    ${payload}=    Get Payload Orcamento    payload_orcamento.json
    ${response}=    POST On Session    api-in-test    ${oper_orcamentos}    json=${payload}
    ...    headers=${headers}    expected_status=any
    Set Global Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header API Version    @{api_pedidos_proxy}[1]    @{api_pedidos_proxy}[2]    proxy
    Validate Header Content Type    application/json
    Status Should Be    201    ${api_response}
    ${json}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json}    ${EXECDIR}/schemas/orcamento_schema.json
```

---

## Execução de Testes

Comando padrão para executar um arquivo .robot:
```bash
robot -d results\<ambiente>-<data>\<Laboratorio>-<descricao> api-<modulo>\<arquivo>.robot
```

---

## Observações Importantes
- Todo o código está em **Português do Brasil** (keywords, variáveis, comentários)
- O projeto **não usa** arquivos `.resource` — o compartilhamento é via `Resource` apontando para `.robot`
- O projeto **não usa** bibliotecas Python customizadas (`.py`)
- As variáveis `@{dados_login}` são sempre expandidas com `@` nos argumentos das keywords
- Usuários e mensagens de erro são ajustados dinamicamente pela keyword `Definir Dados do Laboratorio`
- **Variáveis ${oper_*}** já existem no base-api.robot para os paths comuns. Use-as sempre que possível.
- **Variáveis @{api_*}** já existem no base-api.robot. Mapeie o nome da API da Collection para o array correspondente.
- **Variáveis @{user_*}** já existem no base-api.robot. Use `@{dados_login}` que é configurado pelo Suite Setup.
- **Dados sensíveis** (client_id, client_secret, senhas) nunca devem ser hardcoded nos testes — use as variáveis do base-api.robot.
- Quando um endpoint não existir em nenhum `@{api_*}`, criar um novo array seguindo o padrão: `[nome_api, versao_dev, versao_hml]`.

## Versão desta skill
- **Versão atual: 2.0**
