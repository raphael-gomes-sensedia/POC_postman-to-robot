# POC: Gerador de Testes Robot Framework a partir de Postman Collections

## 1. Contexto

### 1.1. Problema

O time de QA da Essilor desenvolveu testes em Robot Framework para validar APIs REST. Antes, esses testes eram executados no Postman. O surgimento desse projeto se deu pela necessidade de conseguir executar vários ou todos os testes para validar se alterações de desenvolvimento tiveram impacto nos demais endpoints, validações e APIs.

As collections do Postman contêm centenas de cenários de teste. Migrá-los manualmente para o Robot Framework é um processo lento, propenso a erros e difícil de manter. Cada nova versão de uma collection exigiria reescrever todos os testes manualmente.

### 1.2. Estado Atual

**Projeto Robot Framework existente**: `robot/Essilor_backend/`

```
robot/Essilor_backend/
├── api-tests/
│   ├── base-api.robot          # Keywords reutilizáveis (RECURSO PRINCIPAL)
│   ├── common.robot            # Dados comuns de teste
│   ├── get_health.robot        # Testes GET /health
│   ├── get_produtos.robot      # Testes GET /produtos
│   ├── post_pedido_proxy.robot # Testes POST /pedidos
│   └── ...
├── api-autenticacao-jwt/
│   └── conecta_mfa.robot       # Testes MFA
├── api-oracle-idcs/
│   └── post_token.robot        # Testes Oracle IDCS
├── schemas/
│   ├── error_response_schema.json
│   ├── post_pedido_schema.json
│   ├── autenticacao_jwt.json
│   └── ...
├── testData/
└── logs/
```

**Collections Postman de entrada**:
- `API Conecta Pedidos v1.postman_collection.json` (~50 requests, 5 grupos)
- `API OnBoarding Integração Laboratório - OG.postman_collection.json` (~8 requests, 4 grupos)
- `MS Rastreabilidade Dev.postman_collection.json` (~10 requests, 5 grupos)

### 1.3. Coleção Foco da POC

`API Conecta Pedidos v1.postman_collection.json` — estrutura completa:

```
API Conecta Pedidos v1.6
├── [F000] Autenticação
│   └── Gerar Token (POST /oauth/access-token)
├── [F001] GET /pedidos
│   ├── Sucesso [200,206]
│   │   ├── [200] sem params (data=hoje)
│   │   ├── [200] com dataInicio/dataFim
│   │   ├── [200] integradoLab=false
│   │   ├── [200] laboratorio=lab do App
│   │   └── [200] cliente=CNPJ Otica
│   ├── Sucesso (200) - body vazio
│   │   ├── [200] integradoLab=true
│   │   └── [200] cliente=CNPJ invalido
│   └── Erros
│       ├── 400 (intervalo de datas, apenas dataInicio, apenas dataFim)
│       ├── 401 (access token inválido, app inválido)
│       └── 403 (laboratorio <> lab do app)
├── [F002] GET /pedidos/{id}
│   ├── Sucesso (200)
│   └── Erros (400, 401, 403, 404)
├── [F003] POST /integracao-laboratorio
│   ├── Sucesso (202)
│   └── Erros (401, 404)
└── fluxo integracao-laboratorio (cadeia de 4 requests)
```

Total: ~30+ cenários de teste, 5 tipos de HTTP method (GET, POST), 5 status codes de erro (400, 401, 403, 404, 202).

---

## 2. Objetivo

Construir uma POC de um **gerador em Python** que, dado um arquivo de collection do Postman (formato v2.1 JSON), produza automaticamente arquivos `.robot` o mais próximo possível de testes escritos manualmente pelo time de QA.

### 2.1. Objetivo Específico

Criar um template para validação e padronização dos testes gerados, de forma que o output do gerador seja aceitável quando seguir os mesmos padrões estruturais dos testes existentes em `Essilor_backend`.

---

## 3. Critério de Aceite

O teste `.robot` gerado será considerado **aceitável** quando:

1. **Estrutura**: Seguir o mesmo padrão de seções (`*** Settings ***`, `*** Variables ***`, `*** Test Cases ***`, `*** Keywords ***`)
2. **Resource**: Incluir `Resource  ../api-tests/base-api.robot` na seção Settings
3. **Documentation**: Incluir documentação multi-linha com nome da API, operações e comando de execução
4. **Variables**: Todas as variáveis da collection presentes e resolvidas (`{{var}}` -> `${var}`)
5. **Test Cases**: Cada request do Postman gera um Test Case correspondente
6. **HTTP**: Método correto (GET/POST/PUT/DELETE), URL resolvida com variáveis, session criada
7. **Headers**: `client_id` e `access_token` presentes quando exigidos
8. **Status**: `Status Should Be` com código HTTP correto
9. **Assertions**: Mesmas validações que existiam no script JS do Postman (body, campos, schemas)
10. **Schemas**: `Validate Json By Schema File` quando houver schema de validação
11. **Variáveis encadeadas**: `Set Test Variable` quando um teste extrai valor de resposta de outro
12. **Keywords reutilizáveis**: Usar keywords do `base-api.robot` quando aplicável
13. **Executável**: Pode ser executado com `robot` sem erro de sintaxe

---

## 4. Escopo

### In Escopo

- Testes de back-end (APIs REST)
- Parser de Postman Collection v2.1 JSON
- Geração de arquivos `.robot`
- Geração de schemas JSON de validação
- Integração com IA para tarefas que script não cobre

### Fora de Escopo

- Testes de front-end
- Testes de UI
- Testes de banco de dados
- Testes de performance (exceto validação básica de response time)
- Testes de integração com sistemas externos (exceto APIs HTTP)

---

## 5. Fluxo de Geração

### 5.1. Fluxo Geral

```
Postman Collection JSON
         │
         ▼
┌─────────────────────────────────┐
│ FASE 1: 100% COMPUTACIONAL      │
│ (Script Python)                 │
│                                 │
│ • Parsear JSON                  │
│ • Navegar estrutura aninhada    │
│ • Extrair method, URL, headers  │
│ • Resolver {{variaveis}}        │
│ • Gerar Settings, Variables     │
│ • Gerar chamadas HTTP           │
│ • Gerar assertions básicas      │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ FASE 2: IA NECESSÁRIA           │
│ (API call - OpenAI)             │
│                                 │
│ • Extrair schemas JSON inline   │
│   do JavaScript                 │
│ • Traduzir lógica complexa      │
│   (if/else, loops, Math.)       │
│ • Decidir keyword Robot         │
│   mais adequada                 │
│ • Gerar documentação legível    │
│ • Decidir quando Skip           │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ FASE 3: 100% COMPUTACIONAL      │
│ (Script Python)                 │
│                                 │
│ • Montar arquivo .robot final   │
│ • Salvar schemas JSON           │
│ • Escrever no filesystem        │
└────────────────┬────────────────┘
                 │
                 ▼
        .robot files gerados
        + schemas JSON (opcional)
```

### 5.2. Regra de Divisão: Computacional vs. IA

| 100% Computacional (Script) | IA Necessária (API call) |
|---|---|
| Parsear JSON da collection | Extrair schemas JSON inline do JS |
| Navegar estrutura aninhada | Traduzir lógica complexa (if/else, loops) |
| Extrair method, URL, headers, body | Decidir qual keyword Robot é mais adequada |
| Resolver `{{variaveis}}` | Gerar documentação legível |
| Gerar Settings, Variables | Decidir quando Skip vs. gerar teste |
| Gerar chamadas HTTP | Interpretar intenção do teste |
| Gerar `Status Should Be` | |
| Gerar assertions básicas | |
| Gerar `Set Test Variable` | |

**Regra prática**: Se envolve **estrutura** (formato fixo, mapeamento direto) = script. Se envolve **compreensão** (interpretar intenção, decidir contexto, gerar texto significativo) = IA.

### 5.3. Mapeamento Postman -> Robot

| Postman Field | Robot Equivalent | Tratamento |
|---|---|---|
| `request.method` | Keyword HTTP (`GET On Session`, `POST On Session`) | Direto |
| `request.url.raw` | URL da session | Resolver variáveis, extrair path + query |
| `request.header[]` | `Create Dictionary` para headers | Array -> dict |
| `request.body.raw` | `json=` param | Parsear JSON -> dict |
| `request.auth.type` | Keyword de auth (OAuth, JWT) | Condicional |
| `event[].script.exec` | Assertions em Robot | JS -> Robot keywords |
| `variable[]` | `${var}` no Robot | Resolver e injetar |

---

## 6. Arquitetura

### 6.1. Estrutura do Projeto

```
postman-to-robot/
├── main.py                    # Entry point (CLI com click)
├── parser.py                  # Parseia JSON + resolve variáveis
├── generator.py               # Gera .robot (lógica computacional)
├── assertions.py              # Traduz pm.expect() -> Robot keywords
├── ai_helper.py               # Wrapper para OpenAI API
├── templates/
│   ├── settings.robot.j2      # Template da seção Settings
│   ├── variables.robot.j2     # Template da seção Variables
│   ├── test_case.robot.j2     # Template de cada Test Case
│   └── keywords.robot.j2      # Template de Keywords
├── config.py                  # Configurações
└── requirements.txt
```

### 6.2. CLI

```bash
python main.py \
    --input "API Conecta Pedidos v1.postman_collection.json" \
    --output robot/Essilor_backend/generated/ \
    --base-resource robot/Essilor_backend/api-tests/base-api.robot \
    --env dev \
    --ai-api opencode \
    --ai-model opencode/oci
```

### 6.3. Dependências

```
click>=8.0          # CLI interface
jinja2>=3.1         # Templates para geração de .robot
openai>=1.0         # API de IA
jsonschema>=4.0     # Validação de schemas JSON
```

---

## 7. Referências do Projeto Existente

### 7.1. Resource Principal: `base-api.robot`

Arquivo `robot/Essilor_backend/api-tests/base-api.robot` — contém todas as keywords reutilizáveis que o gerador DEVE aproveitar:

**Keywords de Session:**
- `Create Session API Proxy` — cria sessão com auth basic (client_id/secret)
- `Create Session API Adapter` — cria sessão sem auth
- `Create Session API Oauth` — cria sessão OAuth
- `Create Session API Onboarding Proxy` — cria sessão onboarding
- `Create Session API Oracle Proxy` — cria sessão Oracle IDCS

**Keywords de Autenticação:**
- `POST Autenticação JWT` — fluxo de login JWT (usuario + senha -> access_token)
- `POST Autenticação Oauth` — fluxo OAuth client_credentials -> access_token

**Keywords de Validação:**
- `Validate ResponseTime` — valida performance (< 15000ms)
- `Validate Header Content Type` — valida content-type header
- `Validate Header API Version` — valida version header
- `Validate Json By Schema File` — valida response contra schema JSON
- `Validar Mensagem de Erro` — valida estrutura de erro (codigo + mensagem)

**Keywords de Dados:**
- `Get Payload Orcamento` — carrega payload de arquivo JSON
- `Gerar Id Pedido Aleatorio` — gera ID aleatório para pedidos
- `Montar Datas` — gera datas relativas
- `Definir Dados do Laboratorio` — configura dados de teste por lab

**Variáveis Globais:**
- `${client_id}`, `${client_secret}` — credenciais OAuth
- `${env}` — ambiente (dev/hml)
- `${EXPECTED_MAX_TIME_MS}` — limite de response time (15000ms)
- `@{api_*}` — listas de APIs com versões dev/hml
- `@{user_*}` — listas de usuários de teste (login, pwd, cnpj otica, cnpj lab)
- `${client_id_invalido}`, `${client_secret_invalido}`, `${pwd_invalida}` — dados inválidos para testes de erro

### 7.2. Padrão de Arquivo Robot Existente

**Exemplo 1: `get_health.robot`**

```robot
*** Settings ***
Documentation       Teste GET /health _ API Proxy
...                 - API Produtos Proxy e Adapter
...                 - API Pedidos  Proxy e Adapter
...    command to run tests:
...    robot -d results\unit_test_dev\SGO-get_health api-tests\get_health.robot

Resource        ../api-tests/base-api.robot

***Variables***
##                              |user login                           |pwd             |cnpj otica       |cnpj lab        |
@{user_otica_sgo}               proprietario_labminas@teste.com       Essilor@2019     26075599000388    27175413001054

*** Test Cases ***
GET Health - Perfil Otica - API Produtos Proxy - Com Autenticação JWT [200]
    GET Health Proxy    @{user_otica}    @{api_produtos_proxy}
    Validate Header Content Type        application/json
    Response 200 - Body Vazio
```

**Exemplo 2: `post_pedido_proxy.robot`**

```robot
*** Settings ***
Documentation    Chamada para a API Gestão de Pedidos Proxy v1
...              Operação POST /orcamentos
...              Operação POST /pedidos
...              Consulta o Produto para montar o payload do pedido
...        command to run tests:
...        robot -d results\unit_test_dev\post_pedido_proxy api-tests\post_pedido_proxy.robot

Resource        ../api-tests/base-api.robot
Test Setup        Montar Datas

***Variables***
${path_orcamentos}      /orcamentos
${path_pedidos}         /pedidos
@{produto_surf_digital}          34779420021788H        SURFACAGEM_DIGITAL     MULTIFOCAL      ANTIRREFLEXO   37    ## CRIZAL PREVENCIA

*** Test Cases ***
POST Pedido - Perfil Otica - Surfacagem Digital
    Consulta RPL Detalhes do Produto        @{user_otica_sgo}    @{api_produtos_proxy}    @{produto_surf_digital}
    Montagem do Payload        ${produto_surf_digital}[3]    ${produto_surf_digital}[4]
    POST Orcamento        @{user_otica_sgo}    @{api_pedidos_proxy}
    Response 200 - Orcamento
    POST Pedido           @{user_otica_sgo}    @{api_pedidos_proxy}
    Response 200 - POST Pedido
```

**Exemplo 3: `conecta_mfa.robot`**

```robot
*** Settings ***
Documentation    [ESSL-3689] [Autenticação] Conecta MFA
...              Implementção de Autenticação MFA no login do Portal Conecta
...              Novas operações na API Autenticação JWT 1.0
...                  Operação POST /mfa/solicitacao
...                  Operação POST /mfa/token
...        command to run tests:
...        robot -d results\dev-12-03\conecta_mfa api-autenticacao-jwt\conecta_mfa.robot

Resource        ../api-tests/base-api.robot

*** Variables ***
${usuario_qa}            noemy.rosario@sensedia.com
${otp_valido}                664099       # codigo recebido via email

*** Test Cases ***
Autenticacao MFA - Login Conecta - Sucesso
    POST Autenticação /mfa/solicitacao        ${usuario_qa}    ${pwd_teste}
    Response 200 - /mfa/solicitacao
    Busca OTP no Email
    POST Autenticação /mfa/token        ${usuario_qa}    ${codigo_otp_valido}     ${valid_tokenMFA}
    Response 200 - /mfa/token
```

### 7.3. Convenções de Nomenclatura

- **Arquivos**: `snake_case.robot` (ex: `get_health.robot`, `post_pedido_proxy.robot`)
- **Test Cases**: `{Metodo} {Endpoint} - {Cenario} [{Status Code}]`
- **Keywords**: `Verbo Substantivo` (ex: `POST Pedido`, `GET Health`, `Response 200 - Body Vazio`)
- **Variáveis**: `${snake_case}` para escalares, `@{array_name}` para listas, `&{dict_name}` para dicionários
- **Documentação**: Multi-linha com `...`, incluindo comando de execução sugerido
- **Comentários**: `##` para comentários de código, `#` para comentários inline

### 7.4. Padrão de Keywords de Resposta

Keywords de validação de resposta seguem o padrão:

```robot
Response {STATUS} - {DESCRICAO}
    Status Should Be    {STATUS}    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}

    # Validações específicas
    Should Not Be Empty     ${json_response}[campo_especifico]
    Should Be Equal As Strings     ${json_response}[campo]    valor_esperado
    Should Contain          ${json_response}    campo_esperado

    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/schema.json
```

### 7.5. Schemas JSON Existentes

**`error_response_schema.json`** — padrão de erro da API:
```json
{
  "type": "array",
  "minItems": 1,
  "items": {
    "type": "object",
    "required": ["codigo", "mensagem"],
    "properties": {
      "codigo": { "type": "string", "minLength": 3 },
      "mensagem": { "type": "string", "minLength": 10 }
    }
  }
}
```

**`autenticacao_jwt.json`** — padrão de resposta JWT:
```json
{
  "type": "object",
  "required": ["access_token", "token_type", "expires_in"],
  "properties": {
    "access_token": { "type": "string" },
    "token_type": { "type": "string" },
    "expires_in": { "type": "number" }
  }
}
```

---

## 8. Mapeamento de Assertions: Postman JS -> Robot Framework

### 8.1. Assertions Básicas (100% Computacional)

| Postman JS | Robot Framework |
|---|---|
| `pm.response.to.have.status(200)` | `Status Should Be    200    ${api_response}` |
| `pm.expect(x).to.not.be.empty` | `Should Not Be Empty    ${x}` |
| `pm.expect(x).to.be.null` | `Should Be Empty    ${x}` |
| `pm.expect(x).to.eql(y)` | `Should Be Equal As Strings    ${x}    ${y}` |
| `pm.expect(x).to.be.a('string')` | `Should Not Be Empty    ${x}` |
| `pm.expect(x).to.be.a('number')` | `Should Be Equal As Numbers    ${x}` |
| `pm.expect(x).to.contain(y)` | `Should Contain    ${x}    ${y}` |
| `pm.expect(pm.response.text()).to.be.empty` | `Should Be Empty    ${api_response.content}` |
| `pm.expect(x).to.be.above(0)` | `Should Be True    ${x} > 0` |
| `pm.collectionVariables.set("key", value)` | `Set Test Variable    ${key}    ${value}` |
| `pm.environment.set("key", value)` | `Set Test Variable    ${key}    ${value}` |

### 8.2. Assertions Complexas (Precisa de IA)

| Postman JS | Tratamento |
|---|---|
| `pm.expect(pm.response.code).to.be.oneOf([200,206])` | IA decide: gerar `Run Keyword And Continue On Failure` múltiplos ou usar `Should Be One Of` |
| `pm.response.to.have.jsonSchema(jsonSchema)` | IA extrai o schema inline e gera `Validate Json By Schema File` |
| `pm.expect(jsonData.erros[0].codigo).to.eql("401")` | Computacional: mapeamento direto |
| `if (totalItens > 0) { ... }` | IA traduz para `IF ... END` no Robot |
| `Math.floor(Math.random() * totalItens)` | IA traduz para lógica Robot equivalente |
| `pm.test("Nome do teste", function(){...})` | IA decide se cria Test Case separado ou integra ao existente |

---

## 9. Plano de Desenvolvimento

### Fase 1: Gerador Básico (5 dias)

**Objetivo**: Gerar arquivos `.robot` com estrutura correta, requests e assertions básicas.

#### Tarefas

1. **Setup** (0.5 dia)
   - Criar estrutura do projeto `postman-to-robot/`
   - `requirements.txt`: `click>=8.0`, `jinja2>=3.1`, `openai>=1.0`, `jsonschema>=4.0`
   - CLI com `click`

2. **Parser** (1 dia)
   - Ler JSON da collection
   - Navegar recursivamente pelo array `item` (suporte a pastas aninhadas)
   - Extrair: nome do grupo, nome do teste, método, URL, headers, body, auth
   - Resolver `{{variaveis}}` com valores do array `variable[]`
   - Marcar requests com `disabled: true` para skip

3. **Gerador de Estrutura** (1 dia)
   - Template `*** Settings ***` com `Resource` para `base-api.robot`
   - Template `*** Variables ***` com variáveis resolvidas da collection
   - Template `*** Test Cases ***` com um caso por request
   - Gerar 1 arquivo `.robot` por grupo de primeiro nível

4. **Gerador de Requests** (1 dia)
   - Mapear `method` -> keyword Robot (`GET On Session`, `POST On Session`, etc.)
   - Gerar `Create Session` com URL resolvida (base_url + env + api + version + path)
   - Gerar `Create Dictionary` para headers
   - Gerar `Status Should Be` baseado no status code esperado
   - Gerar `Set Test Variable    ${api_response}    ${response}`

5. **Gerador de Assertions Básicas** (0.5 dia)
   - Parser de `pm.test()` e `pm.expect()` via regex
   - Mapeamento das assertions básicas (tabela da seção 8.1)
   - Gerar `Set Test Variable` para `pm.collectionVariables.set()` e `pm.environment.set()`

**Critério de Aceite**: Gerar `.robot` para `API Conecta Pedidos v1` com estrutura correta. Executar `robot` sem erro de sintaxe.

---

### Fase 2: IA Integration (3 dias)

**Objetivo**: Integrar IA para tarefas que script não consegue cobrir.

#### Tarefas

1. **AI Helper** (1 dia)
   - Wrapper para OpenAI API (`ai_helper.py`)
   - Prompt template para extração de schema JSON
   - Prompt template para tradução de assertions complexas
   - Prompt template para escolha de keyword Robot

2. **Extração de Schema JSON** (1 dia)
   - Identificar schemas inline no campo `event[].script.exec`
   - Enviar trecho JS para IA com prompt: "Extrair o objeto JSON schema deste código JavaScript e retorne apenas o JSON válido"
   - Salvar schema extraído como arquivo `.json` no diretório `schemas/`
   - Inserir `Validate Json By Schema File` nos testes gerados

3. **Assertions Complexas** (0.5 dia)
   - Identificar assertions que regex não traduz:
     - `pm.expect(x).to.be.oneOf([200,206])`
     - `pm.response.to.have.jsonSchema(schema)`
     - `if/else` com lógica condicional
     - `Math.random()`, `Math.floor()`
   - Enviar para IA com prompt: "Traduza esta assertion do Postman para Robot Framework"

4. **Keyword Selection** (0.5 dia)
   - Analisar contexto do teste
   - Enviar para IA: "Dada esta descrição do teste e a lista de keywords disponíveis, qual keyword Robot é mais adequada?"
   - Ex: `Response 200 - Body Vazio` vs `Response 200 - /mfa/token` vs `Response 200 - POST /token`

**Critério de Aceite**: Schemas extraídos corretamente. Assertions complexas traduzidas. Testes gerados com keywords adequadas.

---

### Fase 3: Validação e Refinamento (3 dias)

**Objetivo**: Validar contra o critério de aceite e refinar.

#### Tarefas

1. **Comparação com existentes** (1 dia)
   - Comparar testes gerados com testes hand-written do `Essilor_backend`
   - Validar os checkpoints do template de validação (ver `TEMPLATE-VALIDACAO.md`)
   - Ajustar gerador conforme gaps identificados

2. **Edge Cases** (1 dia)
   - Requests com `disabled: true` -> marcar como `Skip`
   - `fluxo integracao-laboratorio` (cadeia de 4 requests com dependência)
   - Path params `{{random_id_pedido}}` (variável encadeada)
   - Schemas JSON inline complexos (ex: schema de pedido com receita, armacao, orcamento)
   - Múltiplos `pm.test()` dentro de um mesmo script

3. **Polimento** (1 dia)
   - Documentação gerada legível
   - Nomes de arquivo consistentes (`snake_case.robot`)
   - Comando de execução sugerido nos arquivos
   - Tratamento de coleções com variáveis não resolvidas (warning + fallback)

**Critério de Aceite**: Score >= 8/10 no template de validação.

---

## 10. Estimativa Total da POC

| Fase | Dias |
|---|---|
| Fase 1: Gerador Básico | 5 dias |
| Fase 2: IA Integration | 3 dias |
| Fase 3: Validação e Refinamento | 3 dias |
| **Total** | **~11 dias (2-3 semanas)** |

---

## 11. Prompt Templates para IA

### 11.1. Extração de Schema JSON

```
Você é um especialista em JSON Schema. Dado o seguinte código JavaScript extraído
de um teste Postman, extraia o objeto JSON schema e retorne APENAS o JSON válido.

Código JavaScript:
{SCRIPT_JS}

Retorne apenas o JSON, sem markdown, sem explicações.
```

### 11.2. Tradução de Assertions Complexas

```
Você é um especialista em Robot Framework. Dada a seguinte assertion do Postman,
traduza para o equivalente em Robot Framework.

Postman assertion:
{ASSERTION_JS}

Retorne APENAS a linha(s) de código Robot Framework equivalente.
```

### 11.3. Escolha de Keyword Robot

```
Você é um especialista em Robot Framework para testes de API. Dado o seguinte
cenário de teste, qual keyword Robot é mais adequada?

Descrição do teste: {TEST_DESCRIPTION}
Status code esperado: {STATUS_CODE}
Tipo de resposta: {RESPONSE_TYPE}

Keywords disponíveis:
{AVAILABLE_KEYWORDS}

Retorne apenas o nome da keyword mais adequada.
```

---

## 12. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| IA falha na extração de schema | Testes sem validação de schema | Fallback: gerar placeholder com `# TODO: schema manual` |
| Variáveis de ambiente não resolvidas | Testes gerados falham | Manter como `${var}` e gerar warning |
| Scripts JS muito complexos | IA não traduz corretamente | Marcar como `# TODO: manual review` |
| Coleções futuras com estrutura diferente | Gerador quebra | Parser com validação de schema + graceful degradation |
| Custo de IA na POC | Limitado ao escopo | Usar opencode/oci, ~50 chamadas na POC |
