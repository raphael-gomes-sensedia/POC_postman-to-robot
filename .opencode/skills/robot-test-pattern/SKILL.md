---
name: robot-test-pattern
description: Padrões de escrita de testes Robot Framework do time Essilor: nomenclatura, estrutura de arquivos, fluxo de teste, estratégia de dados e keywords
license: MIT
compatibility: opencode
metadata:
  audience: qa-engineers
  workflow: robot-test-automation
  version: "1.0"
  last_updated: "2026-07-10"
---

## O que eu faço
- Documento os padrões de nomenclatura, estrutura e organização dos testes .robot do time Essilor
- Forneço templates exatos de como cada seção (.robot) deve ser escrita
- Descrevo o fluxo típico de um teste: setup → autenticação → consulta → montagem → operação → validação
- Explico como usar `Skip` condicional, propagação de variáveis e ajuste dinâmico de dados

## Quando usar
Use esta skill sempre que for criar ou modificar um arquivo .robot de teste para garantir que siga o padrão estabelecido pelo time. Esta skill define o formato que o código gerado deve seguir.

---

## 1. Arquivo de Resource Base: `api-tests/base-api.robot`

Este é o **único resource verdadeiramente compartilhado** e é importado por praticamente todos os arquivos de teste:

```robot
Resource        ../api-tests/base-api.robot
```

### 1.1 Libraries Disponibilizadas

O `base-api.robot` importa todas as libraries necessárias, de modo que os arquivos de teste **não precisam declarar libraries**:

| Library | Uso |
|---------|-----|
| `Collections` | Manipulação de listas e dicionários |
| `DateTime` | Geração de datas para payloads |
| `ImapLibrary2` | Leitura de emails (para OTP/MFA) |
| `JSONLibrary` | Load e busca em JSON (JSONPath) |
| `OperatingSystem` | Manipulação de arquivos |
| `RequestsLibrary` | Chamadas HTTP (GET, POST, PUT, DELETE) |
| `String` | Geração de strings aleatórias |

### 1.2 Variáveis Globais de Configuração

Definidas no `base-api.robot`:

```robot
${client_id}              3b98e212-cc00-3deb-b2d9-2c7dfb7d2ca5
${client_secret}          5876deaa-e1f4-3951-a1bd-f0737e934c23
${client_id_shop9}         aaa07714-3861-4185-bcbd-4664f05a2071
${client_secret_shop9}    9b672894-0a27-4b90-9ceb-671b29f486ae
${pwd_teste}              Essilor@2019
${EXPECTED_MAX_TIME_MS}   15000
```

### 1.3 Variáveis de Operações (Endpoints)

Todas as operações (paths) são definidas como `${oper_*}`:

```robot
${oper_token}             /token
${oper_oauth}             /access-token?grant_type=client_credentials
${oper_health}            /health
${oper_orcamentos}         /orcamentos
${oper_pedidos}           /pedidos
${oper_orcamentos_atacado}  /orcamentos-atacado
${oper_pedidos_atacado}    /pedidos-atacado
${oper_lp_orcamentos}     /lente-pronta/orcamentos
${oper_lp_pedidos}        /lente-pronta/pedidos
${oper_mfa_solicitacao}   /mfa/solicitacao
${oper_mfa_token}         /mfa/token
${oper_conecta_pedidos}   /conecta-pedidos
${oper_voucher}           /voucher
```

### 1.4 Variáveis de APIs (Arrays com nome + versão dev + versão hml)

Cada API é representada como uma `@{list}` com 3 elementos: `[api_name, version_dev, version_hml]`:

```robot
@{api_auth_jwt}           autenticacao-jwt                v1.58         v1.58
@{api_certificados}        certificados-rastreabilidade    v1.2          v1.2
@{api_produtos_proxy}      gestao-produtos-laboratorio     v1.31         v1.30
@{api_pedidos_proxy}       gestao-pedidos-laboratorio      v1.107        v1.104
@{api_financeiro_proxy}    gestao-financeira-cliente-laboratorio  v1.10  v1.10
@{api_onboarding_labog}    on-boarding                     v1.2          v1.2
@{api_oracle_idcs}         idcs                            v1.9          v1.7
```

**Uso:** Quando passadas como argumento para keywords, usa-se `@{api_pedidos_proxy}` que se desempacota em 3 argumentos: `${api_proxy}`, `${api_version_dev}`, `${api_version_hml}`.

### 1.5 Variáveis de Credenciais de Laboratórios (Arrays)

Cada laboratório tem um array `@{user_<lab>}` com 4 posições:

```robot
##                          |user login                      |pwd            |cnpj otica       |cnpj lab        |
@{user_ceditop}             user_ceditop@teste.com           ceditop2021      95427308000124     03113110000158
@{user_comprol}             user_comprol@teste.com           comprol2021      15321752000121     27175413001135
@{user_labrio}              proprietario_labrio@teste.com    Essilor@2019     18070598000150     27175413000163
@{user_rx}                  proprietario_rx3@teste.com       Essilor@2019     11921550000160     11774798000145
@{user_unilab}              proprietario_unilab2@teste.com  Essilor@2019     05472947000461     08038666000140
@{user_otica_lab_og}        multiplos_cnpj_04@teste.com     Essilor@2019     26156910000151     04693846000105
```

**Posições do array:**
- `[0]` = usuário (email)
- `[1]` = senha
- `[2]` = CNPJ da Ótica
- `[3]` = CNPJ do Laboratório

Perfis especiais:
```robot
@{user_adm_essilor}         administrador_essilor@teste.com  Essilor@2019
@{user_colab_lab}           colaborador_laboratorio@teste.com Essilor@2019
@{user_lab_og}              user_alliance@teste.com          Essilor@2019
```

### 1.6 Variáveis de Mensagens de Erro (Arrays)

Mensagens de erro seguem o padrão `@{msg_*}` com 3 posições: `[status_code, codigo_erro, mensagem]`:

```robot
##                            |status_code  |codigo        |mensagem
@{msg_token_invalido}         401           401            Access Token inválido.
@{msg_lab_nao_autorizado}     403           403            Consulta com laboratório não autorizado.
@{msg_header_sem_laboratorio} 422           422            É necessário informar o laboratório.
@{msg_requisicao_invalida}   422           422            Requisição inválida. Existem campos...
@{msg_produto_nao_encontrado} 400           10.8.ORC15    O Produto itemSequence: 1, SKU: 010203...
```

### 1.7 Keywords de Infraestrutura Compartilhadas

 Todas as keywords abaixo estão em `base-api.robot` e são reutilizadas por todos os arquivos de teste:

#### Create Session API Proxy
Cria sessão HTTP autenticada com client_id/client_secret:
```robot
Create Session API Proxy
    [Arguments]    ${api}
    # Internamente:
    # Create Session api-in-test  https://api.essilor.com.br/${env}/${api}/v1  auth=...  verify=${True}
```

#### POST Autenticação JWT
Faz login via API de autenticação e armazena o JWT na variável `${jwt}`:
```robot
POST Autenticação JWT
    [Arguments]    ${usuario}    ${senha}
    # Internamente faz POST /token na API autenticacao-jwt
    # e armazena ${jwt} via Set Test Variable
```

#### Validate ResponseTime
Valida que o tempo de resposta da última chamada (`${api_response}`) é menor que `${EXPECTED_MAX_TIME_MS}`:
```robot
Validate ResponseTime
    # Avalia ${api_response.elapsed.total_seconds()} * 1000
    # Compara com ${EXPECTED_MAX_TIME_MS}
```

#### Validate Header Content Type
```robot
Validate Header Content Type
    [Arguments]    ${content_type}
    # Verifica o header content-type da response (${api_response})
```

#### Validate Header API Version
```robot
Validate Header API Version
    [Arguments]    ${api_version_dev}    ${api_version_hml}    ${param_header}
    # Compara o header conforme o ${env} (dev ou hml)
```

#### Validar Mensagem de Erro
Keyword genérica para validação de erros (status, código, mensagem):
```robot
Validar Mensagem de Erro
    [Arguments]    ${status_code}    ${codigo_erro}    ${msg_erro}
    # 1. Status Should Be    ${status_code}    ${api_response}
    # 2. Validate Json By Schema File contra error_response_schema.json
    # 3. Itera sobre o array de erros validando codigo e mensagem
```

#### Get Payload Orcamento
Carrega um payload JSON template da pasta `resources/`:
```robot
Get Payload Orcamento
    [Arguments]    ${file_name}
    # Retorna ${json_dict} lendo ${EXECDIR}/resources/${file_name}
```

#### Gerar Id Pedido Aleatorio
Gera um ID único baseado em data/hora atual + número aleatório:
```robot
Gerar Id Pedido Aleatorio
    # Monta número a partir de month+day+hour+random_4_digits
    # Set Global Variable    ${id_pedido_otica}
```

#### Definir Dados do Laboratorio
Configura credenciais de laboratório, ambiente e perfil para a suite de testos:
```robot
Definir Dados do Laboratorio
    [Arguments]    ${lab_teste}    ${arg_perfil}    ${test_env}
    # Set Global Variable ${env}        ${test_env}
    # Set Global Variable ${laboratorio} ${lab_teste}
    # Set Global Variable @{dados_login} @{user_<lab>}
    # Ajusta mensagens de erro conforme o laboratório
    # Se perfil Essilor: usa user_adm_essilor
    # Se perfil Laboratorio: usa user_colab_lab
```

---

## 2. Padrões de Estrutura de Arquivos .robot

### 2.1 Estrutura Base de um Arquivo de Teste

Todo arquivo `.robot` segue esta estrutura:

```robot
*** Settings ***
Documentation    [ESSL-XXXX] [Módulo] Título da Funcionalidade
...              Descrição adicional das operações testadas
...              - Operação POST /endpoint
...              - Operação GET /endpoint
...    
...        command to run tests:
...        robot -d results\<pasta_saida> <pasta_api>\<arquivo>.robot

Resource        ../api-tests/base-api.robot

Suite Setup      Definir Dados do Laboratorio     LabRio     Otica     hml


*** Variables ***
# Variáveis específicas do arquivo de teste (especificações de dados de teste)


*** Test Cases ***
# Cenários de teste


*** Keywords ***
# Keywords específicas do arquivo
```

### 2.2 Documentation

Sempre inclui:
1. **Módulo/Funcionalidade**
2. **Operações testadas** (endpoints)
3. **Comando para rodar os testes** (com caminho de output)

### 2.3 Suite Setup

Quase todos os arquivos usam `Suite Setup` para configurar o laboratório de teste e ambiente:

```robot
Suite Setup      Definir Dados do Laboratorio     Comprol     Otica     hml
```

Parâmetros:
- **Lab:** `Comprol`, `LabRio`, `Unilab`, `RX`, `LabOG`, etc.
- **Perfil:** `Otica` (padrão), `Laboratorio`, `Essilor`, `LabOG`
- **Ambiente:** `dev`, `hml`

### 2.4 Section Variables — Padrões de Declaração

Variáveis locais do arquivo podem ser:

**Scalar (`${}`):**
```robot
${voucher_com_certificado}      213KNRI1NX
${montagem_codRef_00}           00
```

**List (`@{}`) — para dados tabulares/estruturados:**
```robot
##                                |RPL               0|tipoProducao      1|tipoProduto  2|tipo     3|servico    4|
@{produto_surf_digital_01}       3H2C6810023148B      SURFACAGEM_DIGITAL   MULTIFOCAL    ANTIRREFLEXO  01
```

**Mensagens de erro locais:**
```robot
##                            |status_code  |codigo  |mensagem
@{msg_lab_invalido}            403          403      Consulta permitida somente...
```

**Comentários de coluna:**
```robot
##                |login/usuario        0|senha        1|cpf       2|papel usuario  3|
@{user_labog_sem_app}   onda4-novouser@teste.com   Essilor@2019   598.347.261-55   Gerente Lab Independente
```

---

## 3. Padrões de Cenários de Teste

### 3.1 Nomenclatura de Test Cases

- **Prefixo `T##` para testes positivos:** `T01 -`, `T02 -`, `T03 -`
- **Prefixo `T##_NEG` ou `T##_Neg` para negativos dentro do arquivo positivo:** `T09_NEG -`
- **Arquivos negativos usam `T##_Neg -`:** `T01_Neg -`, `T02_Neg -`
- **Descrição após o prefixo:** `Perfil X - Módulo Y - Descrição do Cenário`

Exemplos:
```robot
T01 - Conecta - Modulo Pedidos - Receita Padrao - Sem Montagem - Com Cor Armacao
T02 - Perfil Essilor - Modulo Conecta Consulta - Consulta Lista de Pedidos LabOG
T01_Neg - Perfil LabOG - Modulo Conecta Consulta - Laboratorio Diferente LabOG
Teste Negativo - Token Invalido - Orcamento Lente Pronta
```

### 3.2 Estrutura Típica de um Test Case Positivo (POST)

```robot
T01 - Conecta - Modulo Pedidos - Receita Padrao - Sem Montagem - Com Cor Armacao
    Dados de Teste - Pedido Sem Promo      T01

    Consulta RPL Detalhes do Produto        @{dados_login}    @{api_produtos_proxy}    @{produto_surf_digital_01}
    Montagem do Payload        ${produto_surf_digital_01}[3]    ${produto_surf_digital_01}[4]     nao     sim

        POST Sucesso - Modulo Pedidos        @{dados_login}    @{api_pedidos_proxy}     ${oper_orcamentos}
        Response 200 - Orcamento

    POST Sucesso - Modulo Pedidos           @{dados_login}    @{api_pedidos_proxy}      ${oper_pedidos}
    Response 200 - Pedido
```

### 3.3 Estrutura Típica de um Test Case Negativo

```robot
POST /mfa/solicitacao - Usuario Invalido
    POST Autenticação /mfa/solicitacao        ${usuario_invalido}    ${pwd_teste}
    Validar Mensagem de Erro       @{msg_token_invalido}
```

```robot
T01_Neg - Perfil LabOG - Modulo Conecta Consulta - Laboratorio Diferente
    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set List Value          ${dados_login}    3    ${user_rx}[3]
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_lab_invalido}
```

### 3.4 Uso de Skip para Laboratórios que Não Suportam o Teste

```robot
Verifica Lab para Pular Teste
    IF     '${laboratorio}' == 'Riachuelo' or '${laboratorio}' == 'LabMinas'
         Skip     msg = Lab ${laboratorio} não valida idPedidoOtica Duplicado
    END
```

Ou condicional dentro de keyword de setup de teste:
```robot
IF     '${cenario_teste}' == 'T02' and '${laboratorio}' == 'LabRio'
    Skip     msg = Lab ${laboratorio} - não possui produtos com Montagem com codigoRef <> [00,01]
END
```

### 3.5 Data-Driven com Test Template e CSV (DataDriver)

Alguns arquivos específicos usam data-driven via CSV:

```robot
Library            DataDriver    ../data/DadosLabs.csv     encoding=utf_8

Test Template      Consulta Produtos RX

*** Test Cases ***
Gerar Orcamento Laboratorio     using ${nome_lab} and ${cnpj_otica} and ${cnpj_lab} and ${LMS}
```

---

## 4. Padrões de Keywords

### 4.1 Nomenclatura

- **Keywords de ação HTTP:** `POST Sucesso - <contexto>`, `GET Sucesso - <contexto>`, `POST Erro - <contexto>`
- **Keywords de validação de response:** `Response 200 - <entidade>`, `Response 200/206 - <entidade>`
- **Keywords de montagem:** `Montagem do Payload`, `Montagem do Payload Fixo`
- **Keywords de negócio:** `Dados de Teste - <cenario>`, `Verifica Lab para Pular Teste`
- **Keywords de consulta auxiliar:** `Consulta RPL Detalhes do Produto`, `Encontra Produto com RPL`

### 4.2 Estrutura Padrão de Keyword de Ação POST

```robot
POST Sucesso - Modulo Pedidos
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}    ${api_proxy}    ${api_version_dev}    ${api_version_hml}    ${api_path}

    POST Autenticação JWT        ${user}    ${pwd}
    Create Session API Proxy     ${api_proxy}

    IF     '${teste_perfil}' == 'Laboratorio'
        &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
        ...    otica=${cnpjOtica}
    ELSE
        &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
    END

    ${response}=    POST On Session         api-in-test      ${api_path}       json=${payload}
    ...     headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}

    Validate ResponseTime
    Validate Header API Version    ${api_version_dev}      ${api_version_hml}     proxy
    Validate Header Content Type        application/json
```

### 4.3 Estrutura Padrão de Keyword de Ação GET

```robot
GET Sucesso - Conecta Consulta - Params
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}    ${api_proxy}    ${api_version_dev}    ${api_version_hml}    ${api_oper}

    POST Autenticação JWT        ${user}    ${pwd}
    Create Session API Proxy     ${api_proxy}

    &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
    ${response}=    GET On Session         api-in-test      ${api_oper}       headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}

    ${status_code}=    Convert To String    ${api_response.status_code}
    Should Contain Any        ${status_code}     200     206

    Validate ResponseTime
    Validate Header API Version      ${api_version_dev}      ${api_version_hml}     proxy
    Validate Header Content Type     application/json
```

### 4.4 Estrutura Padrão de Keyword de Validação de Response

```robot
Response 200 - Pedido
    Status Should Be    201    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/post_pedido_schema.json

    Should Be Equal As Strings     ${json_response}[idPedidoOtica]     ${id_pedido_otica}
    Should Not Be Empty            ${json_response}[id]

    ${orcamento_array}=    Get From Dictionary    ${json_response}    orcamento
    Should Not Be Empty     ${orcamento_array}[dataEntregaPrevista]
    Should Contain          ${orcamento_array}    valorLiquido
```

### 4.5 Estrutura Padrão de Keyword de Validação de Erro

Para erros cujo body é um **array** (schema `error_response_schema.json`):
```robot
Validar Mensagem de Erro - Conecta Consulta
    [Arguments]      ${status_code}      ${codigo_erro}    ${msg_erro}

    Status Should Be    ${status_code}    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_schema.json

    ${response_erro}=    Evaluate       json.loads($api_response.content)    json

    FOR    ${item}    IN    @{response_erro}
        Should Be Equal As Strings     ${item}[codigo]       ${codigo_erro}
        Should Be Equal As Strings     ${item}[mensagem]     ${msg_erro}
    END
```

Para erros cujo body é um **objeto** (schema `error_response_object_schema.json`):
```robot
Validar Mensagem de Erro Objeto
    [Arguments]      ${status_code}      ${msg_erro}

    Status Should Be    ${status_code}    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_object_schema.json

    Should Be Equal As Strings     ${json_response}[codigo]       ${status_code}
    Should Be Equal As Strings     ${json_response}[mensagem]     ${msg_erro}
```

---

## 5. Padrões de Mecanismos de Autenticação e Headers

### 5.1 Autenticação Padrão (JWT via /token)

Sempre executada por:
```robot
POST Autenticação JWT        ${user}    ${pwd}
```

Após execução, a variável `${jwt}` contém o access_token (Set Test Variable).

### 5.2 Headers Padrão

**Para perfil Ótica (default):**
```robot
&{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
```

**Para perfil Laboratorio (multiconta):**
```robot
&{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}      otica=${cnpjOtica}
```

**Para perfil Essilor (financeiro):**
```robot
&{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}      otica=${cnpjOtica}
```

### 5.3 Logout/Testes de JWT Expirado

Usa-se `${jwt_expirado}` (definido no `base-api.robot`) diretamente no header:
```robot
&{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt_expirado}      laboratorio=${cnpjLab}
```

---

## 6. Padrões de Payloads JSON

### 6.1 Localização e Template

Os payloads JSON ficam em `resources/` e são carregados via:
```robot
${get_payload}=    Get Payload Orcamento    payload_pedido.json
Set Global Variable    ${payload_original}    ${get_payload}
```

### 6.2 Manipulação Dinâmica do Payload

Dicionário é modificado via `Set To Dictionary`:
```robot
Set To Dictionary    ${payload_original}    idPedidoOtica=${id_pedido_otica}

&{novo_servico}=    Create Dictionary    codigo=${produto_servico_codigo}    descricao=${produto_servico_descricao}
...    codigoRef=${produto_servico_codigoRef}    tipo=${produto_servico_tipo}

@{servicos_list}=    Create List
Append To List    ${servicos_list}    ${novo_servico}
Set To Dictionary    ${payload_original}    servicos=${servicos_list}
```

### 6.3 Payload Final

Após montagem, o payload é armazenado em `${payload}` (global):
```robot
Set Global Variable    ${payload}    ${payload_original}
```

E enviado na chamada:
```robot
${response}=    POST On Session    api-in-test    ${api_path}    json=${payload}    headers=${headers}    expected_status=any
```

---

## 7. Padrões de Validação com JSON Schema

### 7.1 Localização dos Schemas

Schemas ficam em `schemas/*.json` e são referenciados via `${EXECDIR}`:

```robot
Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/post_pedido_schema.json
```

### 7.2 Schemas Disponíveis

| Schema | Uso |
|--------|-----|
| `error_response_schema.json` | Erro com body em formato array |
| `error_response_object_schema.json` | Erro com body em formato objeto |
| `error_response_oracle_schema.json` | Erro específico da Oracle IDCS |
| `post_pedido_schema.json` | Response de POST /pedidos |
| `post_pedido_v2_schema.json` | Response de POST /pedidos (v2 - montagem sem codRef) |
| `post_pedido_atacado_schema.json` | Response de POST /pedidos-atacado |
| `post_pedido_lente_pronta_schema.json` | Response de POST /lente-pronta/pedidos |
| `orcamento_schema.json` | Response de POST /orcamentos |
| `produto_schema.json` | Response de GET /produtos/{rpl}/parametros |
| `lista_pedidos_schema.json` | Response de GET /conecta-pedidos |
| `lista_pedidos_labog_schema.json` | Response de GET /conecta-pedidos (LabOG) |
| `lista_faturas_schema.json` | Response de GET /faturas |
| `lista_certificados_schema.json` | Response de GET /certificados |
| `autenticacao_jwt.json` | Response de POST /token (JWT) |
| `autenticacao_mfa_solicitacao.json` | Response de POST /mfa/solicitacao |

### 7.3 Estrutura dos Schemas de Erro

**Array (mais comum):** `error_response_schema.json`
```json
{
  "type": "array",
  "minItems": 1,
  "items": {
    "type": "object",
    "required": ["codigo", "mensagem"],
    "properties": {
      "codigo": { "type": "string", "minLength": 3 },
      "mensagem": { "type": "string", "minLength": 10 },
      "etapaErro": { "type": "string" },
      "propagarValidacao": { "type": "boolean" },
      "dadosIndexacao": { "type": ["string", "null"] }
    }
  }
}
```

---

## 8. Boas Práticas de Organização

### 8.1 Separação de Responsabilidades

- **base-api.robot**: Tudo que é compartilhado (libraries, variáveis globais, keywords de infra)
- **Arquivos de teste por API**: Keywords específicas do endpoint/funcionalidade
- **resources/*.json**: Templates de payload
- **schemas/*.json**: Contratos de validação

### 8.2 Escopo de Variáveis

| Keyword | Escopo | Uso |
|---------|--------|-----|
| `Set Test Variable` | Apenas no teste atual | Dados específicos de um cenário |
| `Set Suite Variable` | Toda a suite (arquivo) | Dados compartilhados entre testes do arquivo |
| `Set Global Variable` | Todo o projeto | Estado que precisa persistir entre suites |

**Padrões observados:**
- `${api_response}` → sempre `Set Global Variable` (compartilhada entre keywords)
- `${jwt}` → `Set Test Variable` (definido em `POST Autenticação JWT`)
- `${payload}`, `${payload_original}` → `Set Global Variable`
- `${id_pedido_otica}`, `${id_pedido_lab}` → `Set Global Variable`
- `${produto_codigo}`, `${produto_descricao}` → `Set Test Variable`
- `${env}`, `${laboratorio}`, `${dados_login}` → `Set Global Variable` (via Suite Setup)

### 8.3 Uso de `expected_status=any`

Sempre passar `expected_status=any` nas chamadas HTTP para que o Robot Framework não falhe antes da validação:
```robot
${response}=    POST On Session    api-in-test    ${api_path}    json=${payload}    headers=${headers}    expected_status=any
```

### 8.4 Uso de Indentação para Sub-fluxos

Sub-fluxos dentro de um teste (ex: orçamento antes do pedido) usam indentação extra:
```robot
T01 - Teste com Sub-fluxo
    Preparar Dados

        POST Orcamento        @{dados_login}    @{api_pedidos_proxy}    ${oper_orcamentos}
        Response 200 - Orcamento

    POST Pedido              @{dados_login}    @{api_pedidos_proxy}    ${oper_pedidos}
    Response 200 - Pedido
```

### 8.5 Ambientes (dev/hml)

O ambiente é controlado pela variável `${env}`, definida no `Suite Setup` via `Definir Dados do Laboratorio`. Todas as validações de versão e URL base respeitam essa variável:

- `dev` → API de desenvolvimento
- `hml` → API de homologação
- `sandbox` → Ambiente especial (pula validação de version header)

### 8.6 Comandos de Execução

Sempre documentado no `Documentation` do arquivo:
```robot
...        command to run tests:
...        robot -d results\<pasta_saida> <pasta_api>\<arquivo>.robot
```

Exemplos:
```
robot -d results\hml-14-04\Comprol-Otica-pedido_sem_promo api-modulo-pedido\pedido_sem_promo.robot
robot -d results\hml-22-06\LabOG-ESSL-4360-conecta-pedidos api-modulo-tracking\ESSL-4360-conecta-pedidos.robot
```

---

## 9. Exemplos Completos por Verbo HTTP

### 9.1 POST — Criação de Recurso (Pedido)

**Test Case:**
```robot
T01 - Conecta - Modulo Pedidos - Receita Padrao - Sem Montagem
    Dados de Teste - Pedido Sem Promo      T01

    Consulta RPL Detalhes do Produto        @{dados_login}    @{api_produtos_proxy}    @{produto_surf_digital_01}
    Montagem do Payload        ${produto_surf_digital_01}[3]    ${produto_surf_digital_01}[4]     nao     sim

        POST Sucesso - Modulo Pedidos        @{dados_login}    @{api_pedidos_proxy}     ${oper_orcamentos}
        Response 200 - Orcamento

    POST Sucesso - Modulo Pedidos           @{dados_login}    @{api_pedidos_proxy}      ${oper_pedidos}
    Response 200 - Pedido
```

**Keyword de Ação:**
```robot
POST Sucesso - Modulo Pedidos
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}    ${api_proxy}    ${api_version_dev}    ${api_version_hml}    ${api_path}

    POST Autenticação JWT        ${user}    ${pwd}
    Create Session API Proxy     ${api_proxy}

    IF     '${teste_perfil}' == 'Laboratorio'
        &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
        ...    otica=${cnpjOtica}
    ELSE
        &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
    END

    ${response}=    POST On Session         api-in-test      ${api_path}       json=${payload}
    ...     headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}

    Validate ResponseTime
    Validate Header API Version    ${api_version_dev}      ${api_version_hml}     proxy
    Validate Header Content Type        application/json
```

**Keyword de Validação:**
```robot
Response 200 - Pedido
    Status Should Be    201    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/post_pedido_schema.json

    Should Be Equal As Strings     ${json_response}[idPedidoOtica]     ${id_pedido_otica}
    Should Not Be Empty            ${json_response}[id]
```

### 9.2 GET — Consulta com Query Params

**Test Case:**
```robot
T01 - Perfil LabOG - Consulta Lista de Pedidos
    GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}
    Response 200/206 - Lista Pedidos     ${dados_login}[3]     1
    Salvar Quantidade Pedidos Encontrados
```

**Keyword de Ação:**
```robot
GET Sucesso - Conecta Consulta - Params
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}    ${api_proxy}    ${api_version_dev}    ${api_version_hml}    ${api_oper}

    POST Autenticação JWT        ${user}    ${pwd}
    Create Session API Proxy     ${api_proxy}

    &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
    ${response}=    GET On Session         api-in-test      ${api_oper}       headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}

    Validate ResponseTime
    Validate Header API Version      ${api_version_dev}      ${api_version_hml}     proxy
    Validate Header Content Type     application/json
```

**Keyword de Validação:**
```robot
Response 200/206 - Lista Pedidos
    [Arguments]     ${test_cnpjLab}      ${test_paginaAtual}

    ${status_code}=    Convert To String    ${api_response.status_code}
    Should Contain Any        ${status_code}     200     206

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/lista_pedidos_labog_schema.json

    ${var_paginaAtual}=     Convert To String     ${json_response}[paginaAtual]
    Should Be Equal As Strings     ${var_paginaAtual}     ${test_paginaAtual}
```

### 9.3 POST — Autenticação (Body Simples sem Payload JSON)

**Test Case:**
```robot
Oracle IDCS - POST /token - Erro
    Oracle IDCS POST /token         @{api_oracle_idcs}     ${oper_token}
    Response Erro - POST /token     @{msg_invalid_params}
```

**Keyword:**
```robot
Oracle IDCS POST /token
    [Arguments]         ${api_proxy}    ${api_version_dev}    ${api_version_hml}    ${api_oper}

    Create Session API Oracle Proxy      ${api_proxy}

    &{body_login}=    Create Dictionary    grant_type=${post_body}
    &{headers}=       Create Dictionary    Content-Type=application/x-www-form-urlencoded
    ${response}=      POST On Session      api-in-test    ${api_oper}    json=${post_body}    headers=${headers}    expected_status=any

    Set Test Variable    ${api_response}    ${response}
    Validate ResponseTime
```

### 9.4 GET — Consulta por ID (Path Param)

**Test Case:**
```robot
T29 - Consulta por /{id}
    Set Suite Variable          ${test_operacao}     /conecta-pedidos/${var_id}
    GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
    Response 200 - Detalhes do Pedido       sem_opticlick
```

**Keyword de Validação:**
```robot
Response 200 - Detalhes do Pedido
    [Arguments]     ${var_idOpticlick}

    ${status_code}=    Convert To String    ${api_response.status_code}
    Should Contain Any        ${status_code}     200     206

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/get_pedido_labog_schema.json

    Should Be Equal As Strings     ${json_response}[idPedidoOtica]     ${var_idPedidoOtica}

    IF         '${var_idOpticlick}' == 'com_opticlick'
        Should Be Equal As Strings     ${json_response}[idPedidoOpticlick]     ${var_idPedidoOpticlick}
    END
```

### 9.5 Cenários Negativos — Variações de Header

**Token expirado:**
```robot
POST JWT Expirado
    [Arguments]    ${user}    ${pwd}    ...    ${api_path}

    Create Session API Proxy     ${api_proxy}

    &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt_expirado}      laboratorio=${cnpjLab}

    ${response}=    POST On Session         api-in-test      ${api_path}       json=${payload}
    ...     headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}
```

**Header sem laboratório:**
```robot
POST Header Sem Laboratorio
    [Arguments]    ...

    &{headers}=     Create Dictionary      Content-Type=application/json    access_token=${jwt}

    ${response}=    POST On Session    api-in-test    ${api_path}    json=${payload}    headers=${headers}    expected_status=any
```

**Laboratório inválido:**
```robot
POST Laboratorio Invalido
    [Arguments]    ...

    &{headers}=     Create Dictionary      Content-Type=application/json    access_token=${jwt}      laboratorio=30260871000105

    ${response}=    POST On Session    api-in-test    ${api_path}    json=${payload}    headers=${headers}    expected_status=any
```

**Sem payload (body vazio):**
```robot
POST Sem Payload
    [Arguments]    ...

    &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}

    ${response}=    POST On Session    api-in-test    ${api_path}    headers=${headers}    expected_status=any
```

---

## 10. Padrões de Manipulação de Response JSON

### 10.1 Parse via .json()

```robot
${json_response}=    Set Variable    ${api_response.json()}
```

### 10.2 Parse via Evaluate json.loads

```robot
${dados_produto}=    Evaluate       json.loads($api_response.content)    json
```

### 10.3 Acesso a Campos Aninhados

```robot
${orcamento_array}=    Get From Dictionary    ${json_response}    orcamento
Should Not Be Empty     ${orcamento_array}[dataEntregaPrevista]
```

### 10.4 Acesso com JSONPath (JSONLibrary)

```robot
${lista_numeroDocumento}=    Get Value From Json    ${json_response}    $..numeroDocumento
${var_numeroDocumento}=    Set Variable    ${lista_numeroDocumento}[0]
```

### 10.5 Acesso via Expressão Python Inline

```robot
${var_lab_1}=    Set Variable    ${{ $json_response['pedidos'][0]['laboratorio'] }}
```

### 10.6 Filtro com Python Inline

```robot
${id_opticlick}=    Set Variable    ${{ next((p['idPedidoOpticlick'] for p in $var_lista_206['pedidos'] if p.get('idPedidoOpticlick')), None) }}
```

### 10.7 Iteração sobre Array do Response

```robot
FOR    ${item}    IN    @{dados_certificados}
    Should Not Be Empty    ${item}[idPedidoLaboratorio]
    Should Not Be Empty    ${item}[voucher]
    Should Be Equal As Strings     ${item}[voucher]     ${voucher}
END
```

---

## 11. Padrões de Multi-perfil (Ótica vs Laboratório vs Essilor)

Alguns testes validam o mesmo cenário com diferentes perfis de usuário alterando apenas os dados de login:

```robot
T01 - Perfil LabOG - Consulta Lista de Pedidos
    GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}
    Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

T02 - Perfil Essilor - Consulta Lista de Pedidos
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1
```

---

## 12. Padrões de Condicionais por Laboratório

Mensagens de erro podem variar conforme o laboratório. O `Definir Dados do Laboratorio` ajusta as mensagens via `Set List Value`:

```robot
IF    '${lab_teste}' == 'Ceditop'
    Set List Value    ${msg_produto_nao_encontrado}    1    CAMPO_INVALIDO
    Set List Value    ${msg_produto_nao_encontrado}    2    Produto com código 010203 não encontrado. idPedidoOtica:
    Set List Value    ${msg_id_pedido_otica_duplicado}    0    400
    Set List Value    ${msg_id_pedido_otica_duplicado}    1    CAMPO_INVALIDO
    Set List Value    ${msg_id_pedido_otica_duplicado}    2    Já existe um pedido com o idPedidoOtica informado. idPedidoOtica:
END
```

E nos testes, condições podem pular ou ajustar comportamento:
```robot
IF    '${laboratorio}' == 'LabRio'
    Skip    msg = Lab ${laboratorio} - não possui produtos com Montagem com codigoRef <> [00,01]
END
```

---

## 13. Checklist para Criar um Novo Arquivo .robot

Use este checklist ao criar ou implementar um novo arquivo de teste:

1. [ ] **Variables:** Declarar apenas variáveis específicas do arquivo (dados de teste, mensagens de erro locais)
2. [ ] **Test Cases:** Usar prefixo `T## -` para positivos, `T##_Neg -` ou `Teste Negativo -` para negativos
3. [ ] **Keywords:**
   - Keyword de ação HTTP (autenticar → criar sessão → montar headers → chamar endpoint → validar response time/version/content-type)
   - Keyword de validação de response (status → schema → asserts de campos)
   - Keyword de montagem de payload (se POST/PUT)
4. [ ] **Schemas:** Criar schema JSON em `schemas/` se ainda não existir
5. [ ] **Payloads:** Usar/adaptar payload em `resources/` se for POST/PUT
6. [ ] Sempre usar `expected_status=any` nas chamadas HTTP
7. [ ] Armazenar response em `${api_response}` (global) ou test variable
8. [ ] Validar: Status code → JSON Schema → Campos específicos do cenário
92. [ ] Para erros: usar `Validar Mensagem de Erro` (importado do base-api) ou criar keyword local conforme formato do body (array vs objeto)

---

## 14. Resumo de Fluxo Padrão de um Teste

```
Suite Setup: Definir Dados do Laboratorio (Lab, Perfil, Env)
    ↓
Test Case:
    1. [Opcional] Configurar dados específicos do cenário
    2. [Opcional] Consultar dados auxiliares (produtos, RPL, etc.)
    3. Montar payload (GET Payload → modificar dinamicamente)
    4. Autenticar: POST Autenticação JWT (user, pwd)
    5. Criar sessão: Create Session API Proxy (api_name)
    6. Montar headers (Content-Type, client_id, access_token, laboratorio)
    7. Executar chamada HTTP (POST/GET/PUT/DELETE On Session)
    8. Armazenar response em ${api_response}
    9. Validar ResponseTime
    10. Validar Header API Version
    11. Validar Header Content Type
    12. Validar Status Code
    13. Validar JSON Schema
    14. Validar campos específicos do cenário
```

---

## 15. Considerações Adicionais

- **Não declarar libraries** nos arquivos de teste — elas já estão em `base-api.robot`
- **Não redefinir** `${client_id}`, `${client_secret}`, `${pwd_teste}`, `${jwt_expirado}`, etc. — já estão em `base-api.robot`
- **Arquivos legados** `base.robot` (Selenium) e `common.robot` em `api-tests/` não devem ser usados para testes de API
- **Criação de massa** (`create-data-mass/`): Robôs auxiliares para gerar dados de teste antes dos testes principais; podem ser executados separadamente
- **DataDriver**: Uso pontual para data-driven via CSV; principais arquivos que usam: `api-orcamento/valida_nome.robot` e `api-situacao-cadastral/valida_baselabs.robot`
- **Mensagens dinâmicas**: A keyword `Ajustar Mensagem de Erro` (base-api) concatena `${id_pedido_otica}` ou monta data `${data_hoje}` para mensagens que dependem de dados do teste
- **Validação de ResponseTime**: Usa `Run Keyword And Ignore Error` — falhas de timeout não quebram o teste (apenas logam)
- **Status 200 vs 201**: Muitos POST retornam `201` (Created) ao invés de `200` — sempre conferir o status esperado na documentação da API
