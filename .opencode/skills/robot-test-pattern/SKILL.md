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

## Template de Arquivo .robot

```robot
*** Settings ***
Documentation    <Modulo> _ <Descricao>
...              <Detalhamento dos cenarios>
...
...        command to run tests:
...        robot -d results\<env>-<data>\<Lab>-<arquivo> api-<modulo>\<arquivo>.robot

Resource        ../api-tests/base-api.robot

Suite Setup      Definir Dados do Laboratorio     <Lab>     <Perfil>     <env>


*** Variables ***
##                              |<campo>              |<campo>       |<campo>    |
@{<dado_array_01>}              <valor1>              <valor2>       <valor3>
${<dado_simples>}               <valor>


*** Test Cases ***
T<NN> - <Contexto> - <Modulo> - <Variacao1> - <Variacao2>
    Dados de Teste - <Contexto>      T<NN>

    <Keyword de Acao 1>        ${arg1}    ${arg2}
    <Keyword de Acao 2>        ${arg1}    ${arg2}

        <Keyword de Operacao>        ${arg1}    ${arg2}
        <Keyword de Validacao>

    <Keyword de Operacao 2>        ${arg1}
    <Keyword de Validacao 2>


T<NN>_NEG - <Contexto> - <Modulo> - <Variacao>
    Dados de Teste - <Contexto>      T<NN>

    <Keyword de Acao 1>
    <Keyword de Acao 2>

        <Keyword de Operacao>        ${arg1}    ${arg2}
        Validar Mensagem de Erro     @{msg_<erro_esperado>}


*** Keywords ***
<Keyword Principal>
    [Arguments]    ${arg1}    ${arg2}
    POST Autenticação JWT        @{dados_login}[0]    @{dados_login}[1]
    Create Session API Proxy     ${api_proxy}[0]

    &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt}      laboratorio=${@{dados_login}[3]}

    ${response}=    POST On Session         api-in-test    ${path}    json=${payload}
    ...     headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header API Version    ${api_proxy}[1]    ${api_proxy}[2]    proxy
    Validate Header Content Type    application/json

Response <STATUS> - <Contexto>
    Status Should Be    <STATUS>    ${api_response}
    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/<schema>.json
    Should Not Be Empty    ${json_response}[<campo>]
    Should Be Equal As Strings    ${json_response}[<campo>]    ${valor_esperado}
```

---

## Nomenclatura de Testes

### Padrão Geral
```
T<NN>[-_NEG] - <Contexto> - <Modulo> - <Variacao1> - <Variacao2> - ...
```

### Regras
- `T<NN>`: número sequencial do cenário (T01, T02, ..., T99)
- `_NEG`: sufixo para cenários negativos (T09_NEG, T10_NEG)
- `<Contexto>`: origem do fluxo (Conecta, Shop9, LabOG, etc)
- `<Modulo>`: nome do módulo (Modulo Pedidos, Modulo Lente Pronta, etc)
- `<VariacaoN>`: detalhes específicos do cenário (Sem Montagem, Com Cor Armacao, MPV, etc)

### Exemplos Reais
```robot
T01 - Conecta - Modulo Pedidos - Receita Padrao - Sem Montagem - Com Cor Armacao
T02 - Conecta - Modulo Pedidos - Receita Padrao - Com Montagem 07 - Com Cor Armacao
T05 - Shop9 - Modulo Pedidos - Receita Padrao - Com Montagem 07 - Sem Cor Armacao
T09_NEG - Conecta - Modulo Pedidos - Receita Padrao - Com Montagem 07 - Sem Cor Armacao
T01 Shop9-Otica - Orcamento de Pedido Promo - MPV - Cupom Apenas Espacos
```

---

## Nomenclatura de Keywords

### Regras
- **Português do Brasil** com acentos
- Primeira letra maiúscula em cada palavra significativa
- Keywords de ação começam com verbo: `POST`, `GET`, `Consulta`, `Monta`, `Preenche`, `Busca`, `Define`
- Keywords de validação começam com `Response <STATUS>`: `Response 200 - Orcamento`, `Validar Mensagem de Erro`
- Keywords de suporte começam com descrição do que fazem: `Gerar Id Pedido Aleatorio`, `Montar Datas`

### Exemplos Reais
```robot
POST Autenticação JWT
Create Session API Proxy
Validate ResponseTime
Validate Header API Version
Validate Header Content Type
Get Payload Orcamento
Gerar Id Pedido Aleatorio
Montar Datas
Validar Mensagem de Erro
Ajustar Mensagem de Erro
Definir Dados do Laboratorio
Montagem do Payload
POST Sucesso - Modulo Pedidos
Response 200 - Orcamento
Response 200 - Pedido
Consulta RPL Detalhes do Produto
Response 200 - Detalhes do Produto
Busca Dados do Servico
Preenche Dados do Servico
Preencher ProgramaLaboratorio
Dados de Teste - Pedido Sem Promo
Define Autenticacao Shop9
Consulta Dados do Cupom iPremios
Response 200 - Dados do Cupom iPremios
```

---

## Fluxo Típico de um Teste

### Fluxo Padrão (Pedido/Orçamento)
```
1. Suite Setup: Definir Dados do Laboratorio (configura env, dados_login, msgs)
2. Dados de Teste (configura variáveis do cenário específico, verifica Skips)
3. [Opcional] Define Autenticação (Shop9, perfil diferente)
4. Consulta RPL Detalhes do Produto (GET /produtos/{rpl}/parametros)
5. Montagem do Payload (carrega JSON, preenche com dados da consulta)
6. POST Sucesso - Modulo Pedidos (POST /orcamentos ou /pedidos)
7. Response 200 - Orcamento/Pedido (valida status, schema, campos)
```

### Fluxo de Consulta Apenas
```
1. Suite Setup: Definir Dados do Laboratorio
2. POST Autenticação JWT
3. Create Session API Proxy
4. GET On Session (endpoint de consulta)
5. Validate ResponseTime, Header API Version, Header Content Type
6. Response <STATUS> - <Contexto> (valida schema e campos)
```

---

## Estratégia de Skip Condicional

Usar `Skip` quando um laboratório não suporta determinada feature:
```robot
Dados de Teste - Pedido Sem Promo
    [Arguments]    ${cenario_teste}
    Set Test Variable    ${var_cenario_teste}    ${cenario_teste}

    IF    '${laboratorio}' == 'LabRio'
        IF    '${cenario_teste}' == 'T02'
            Skip    msg = Lab ${laboratorio} - não possui produtos com Montagem com codigoRef <> [00,01]
        END
    ELSE IF    '${laboratorio}' == 'Repro'
        ...
    ELSE
        Skip    msg = Lab ${laboratorio} - ajustar dados de testes antes de executar
    END
```

---

## Propagação de Variáveis

O projeto usa extensivamente `Set Global Variable` e `Set Test Variable` para compartilhar estado entre keywords:

```robot
# Set Global Variable: persiste por toda a suíte (todos os testes)
Set Global Variable    ${payload}          ${payload_original}
Set Global Variable    ${api_response}     ${response}
Set Global Variable    ${id_pedido_otica}  ${random_idpedido}

# Set Test Variable: persiste apenas no teste atual
Set Test Variable    ${jwt}              ${json_response}[access_token]
Set Test Variable    ${var_cenario_teste} ${cenario_teste}
Set Test Variable    ${var_cupom_rpl}    ${cupom_rpl}
```

---

## Ajuste Dinâmico de Mensagens de Erro

Mensagens de erro variam por laboratório. A keyword `Definir Dados do Laboratorio` ajusta dinamicamente:
```robot
Definir Dados do Laboratorio
    IF    '${lab_teste}' == 'Ceditop'
        Set List Value    ${msg_produto_nao_encontrado}  1  CAMPO_INVALIDO
        Set List Value    ${msg_produto_nao_encontrado}  2  Produto com código 010203 não encontrado. idPedidoOtica:
    ELSE IF    '${lab_teste}' == 'Comprol'
        Set List Value    ${msg_produto_nao_encontrado}  0  404
        Set List Value    ${msg_produto_nao_encontrado}  1  10.8.ORC16
    END
```

---

## Headers por Perfil

O header `laboratorio` e `otica` variam conforme o perfil:
```robot
IF    '${teste_perfil}' == 'Laboratorio'
    &{headers}=    Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt}    laboratorio=${@{dados_login}[3]}    otica=${@{dados_login}[2]}
ELSE
    &{headers}=    Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt}    laboratorio=${@{dados_login}[3]}
END
```

---

## Validação de Schema

```robot
# Validar resposta completa contra schema
Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/<nome>_schema.json

# Validar campos específicos
Should Not Be Empty    ${json_response}[dataEntregaPrevista]
Should Contain         ${json_response}    valorLiquido
Should Be Equal As Strings    ${json_response}[rpl]    ${rpl_esperado}
```

---

## Perfis de Teste

| Perfil | Descrição | Header `otica` |
|--------|-----------|----------------|
| Otica | Usuário de ótica (default) | Não envia |
| Laboratorio | Colaborador de laboratório | Envia CNPJ da ótica |
| Essilor | Administrador Essilor | Não envia |
| LabOG | Laboratório de grupo | Não envia |

---

---

## Exemplos Completos de Arquivos .robot

### Exemplo 1: Consulta (GET) com validação de schema
```robot
*** Settings ***
Documentation    Gestao Pedidos Proxy _ Consulta de Pedidos
...              [F001] GET /pedidos
...              - [200] GET /pedidos Sucesso
...              - [206] GET /pedidos Parcial
...
...        command to run tests:
...        robot -d results\dev\LabOG-consulta-pedidos api-gestao-pedidos-proxy\pedidos.robot

Resource        ../api-tests/base-api.robot

Suite Setup      Definir Dados do Laboratorio     LabOG     LabOG     hml


*** Test Cases ***
T01 - Conecta - Modulo Pedidos - Consulta - Sem Filtro
    POST Autenticação JWT        @{dados_login}[0]    @{dados_login}[1]
    Create Session API Proxy     ${api_pedidos_proxy}[0]

    &{headers}=    Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt}    laboratorio=@{dados_login}[3]

    ${response}=    GET On Session    api-in-test    ${oper_pedidos}
    ...    headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header API Version    ${api_pedidos_proxy}[1]    ${api_pedidos_proxy}[2]    proxy
    Validate Header Content Type    application/json

    Status Should Be    200    ${api_response}
    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/pedidos_schema.json
    Should Not Be Empty    ${json_response}[0][idPedido]
```

### Exemplo 2: Operação POST com payload e validação de campos
```robot
*** Settings ***
Documentation    Gestao Pedidos Proxy _ Criacao de Orcamento
...              [F002] POST /orcamentos
...              - [201] POST /orcamentos Sucesso - Receita Padrao
...              - [201] POST /orcamentos Sucesso - Sem Montagem
...
...        command to run tests:
...        robot -d results\dev\LabOG-orcamentos api-gestao-pedidos-proxy\orcamentos.robot

Resource        ../api-tests/base-api.robot

Suite Setup      Definir Dados do Laboratorio     Ceditop     Otica     dev


*** Variables ***
##                              |rpl                    |descricao
@{dados_produto_01}             123456                  Lente Progressiva
${sku_produto_01}               010203


*** Test Cases ***
T01 - Conecta - Modulo Pedidos - Orcamento - Receita Padrao - Sem Montagem
    Dados de Teste - Pedido Sem Promo      T01

    POST Autenticação JWT              @{dados_login}[0]    @{dados_login}[1]
    Create Session API Proxy           ${api_pedidos_proxy}[0]

    Consulta RPL Detalhes do Produto    ${dados_produto_01}[0]
    Montagem do Payload

    &{headers}=    Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt}    laboratorio=@{dados_login}[3]

    ${response}=    POST On Session    api-in-test    ${oper_orcamentos}
    ...    json=${payload}    headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header API Version    ${api_pedidos_proxy}[1]    ${api_pedidos_proxy}[2]    proxy
    Validate Header Content Type    application/json

    Response 201 - Orcamento


*** Keywords ***
Dados de Teste - Pedido Sem Promo
    [Arguments]    ${cenario_teste}
    Set Test Variable    ${var_cenario_teste}    ${cenario_teste}

    IF    '${laboratorio}' == 'LabRio'
        Skip    msg = Lab ${laboratorio} - não possui produtos com Montagem
    END

Consulta RPL Detalhes do Produto
    [Arguments]    ${rpl}
    &{headers}=    Create Dictionary    Content-Type=application/json
    ...    client_id=${client_id}    access_token=${jwt}
    ...    laboratorio=@{dados_login}[3]
    ${response}=    GET On Session    api-in-test    ${oper_produtos}/${rpl}/parametros
    ...    headers=${headers}    expected_status=any
    Set Test Variable    ${api_response}    ${response}

    Status Should Be    200    ${api_response}
    ${json}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json}    ${EXECDIR}/schemas/produto_parametros_schema.json
    Set Test Variable    ${dados_produto}    ${json}

Montagem do Payload
    ${payload}=    Get Payload Orcamento    payload_orcamento_receita_padrao.json
    Set Test Variable    ${payload}    ${payload_original}
    Set To Dictionary    ${payload}    idPedidoOtica    ${id_pedido_otica}
    Set Global Variable    ${payload}    ${payload_original}

Response 201 - Orcamento
    Status Should Be    201    ${api_response}
    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/orcamento_schema.json
    Should Not Be Empty    ${json_response}[idPedido]
    Should Not Be Empty    ${json_response}[dataEntregaPrevista]
```

### Exemplo 3: Cenário de erro com validação de mensagem
```robot
*** Settings ***
Documentation    Gestao Pedidos Proxy _ Erros de Pedidos
...              [F001] GET /pedidos
...              - [400] GET /pedidos Intervalo invalido
...              - [401] GET /pedidos Token invalido
...
...        command to run tests:
...        robot -d results\dev\LabOG-erros-pedidos api-gestao-pedidos-proxy\neg-pedidos.robot

Resource        ../api-tests/base-api.robot

Suite Setup      Definir Dados do Laboratorio     LabOG     LabOG     hml


*** Test Cases ***
T01_NEG - Conecta - Modulo Pedidos - Consulta - Intervalo Datas Invalido
    POST Autenticação JWT        @{dados_login}[0]    @{dados_login}[1]
    Create Session API Proxy     ${api_pedidos_proxy}[0]

    &{headers}=    Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt}    laboratorio=@{dados_login}[3]

    ${response}=    GET On Session    api-in-test    ${oper_pedidos}
    ...    params=dataInicio=2025-01-01&dataFim=2024-01-01
    ...    headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header API Version    ${api_pedidos_proxy}[1]    ${api_pedidos_proxy}[2]    proxy
    Validate Header Content Type    application/json

    Validar Mensagem de Erro    @{msg_requisicao_invalida}


T02_NEG - Conecta - Modulo Pedidos - Consulta - Token Invalido
    &{headers}=    Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ...    access_token=${jwt_expirado}

    ${response}=    GET On Session    api-in-test    ${oper_pedidos}
    ...    headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}
    Validate ResponseTime
    Validate Header Content Type    application/json

    Validar Mensagem de Erro    @{msg_token_invalido}
```

---

## Versão desta skill
- **Versão atual: 2.0**
