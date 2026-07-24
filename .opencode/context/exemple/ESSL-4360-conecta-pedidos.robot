*** Settings ***
Documentation    [ESSL-4360][Rastreabilidade][Onda 5] APIs - Consulta de pedidos LABs OG
...              Novo modulo - Conecta Consulta
...              Consulta Pedidos LabOG na base MS/AWS
...               - Lab = LabOG, cliente = otica
...    
...              API Gestão de Pedidos Laboratório
...              - GET /conecta-pedidos
...              - GET /conecta-pedidos/{id}
...    
...        command to run tests:
...        robot -d results\hml-22-06\LabOG-ESSL-4360-conecta-pedidos api-modulo-tracking\ESSL-4360-conecta-pedidos.robot

Resource        ../api-tests/base-api.robot

Suite Setup      Definir Dados do Laboratorio     LabOG     LabOG     hml


*** Variables ***


*** Test Cases ***
T01 - Perfil LabOG - Modulo Conecta Consulta - Consulta Lista de Pedidos LabOG

    GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}
    Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T02 - Perfil Essilor - Modulo Conecta Consulta - Consulta Lista de Pedidos LabOG
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T03 - Perfil LabOG - Modulo Conecta Consulta - Pagina 5

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?pagina=5
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     5

    Salvar Quantidade Pedidos Encontrados

T04 - Perfil Essilor - Modulo Conecta Consulta - Pagina 5
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     5

    Validar Quantidade Pedidos Encontrados

T05 - Perfil LabOG - Modulo Conecta Consulta - Limite 10
    Set Suite Variable          ${test_operacao}     /conecta-pedidos?limite=10
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T06 - Perfil Essilor - Modulo Conecta Consulta - Limite 10
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T07 - Perfil LabOG - Modulo Conecta Consulta - Cliente Informado
    IF     '${env}' == 'dev'
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cliente=64762321000106
    ELSE
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cliente=18070598000150
    END
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T08 - Perfil Essilor - Modulo Conecta Consulta - Cliente Informado
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados
    Salvar idPedidoOpticlick

T09 - Perfil LabOG - Modulo Conecta Consulta - idPedidoOpticlick

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?idPedidoOpticlick=${var_idPedidoOpticlick}
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T10 - Perfil Essilor - Modulo Conecta Consulta - idPedidoOpticlick
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T11 - Perfil LabOG - Modulo Conecta Consulta - idPedidoOtica

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?idPedidoOtica=${var_idPedidoOtica}
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T12 - Perfil Essilor - Modulo Conecta Consulta - idPedidoOtica
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T13 - Perfil LabOG - Modulo Conecta Consulta - integradoLab=true

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?integradoLab=true
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T14 - Perfil Essilor - Modulo Conecta Consulta - integradoLab=true
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T15 - Perfil LabOG - Modulo Conecta Consulta - integradoLab=false

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?integradoLab=false
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T16 - Perfil Essilor - Modulo Conecta Consulta - integradoLab=false
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T17 - Perfil LabOG - Modulo Conecta Consulta - dataInicio e dataFim

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?dataInicio=2026-05-01&dataFim=2026-06-19
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T18 - Perfil Essilor - Modulo Conecta Consulta - dataInicio e dataFim
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T19 - Perfil LabOG - Modulo Conecta Consulta - cupomPromocional
    IF     '${env}' == 'dev'
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cupomPromocional=215KJH8SRG
    ELSE
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cupomPromocional=21SJIX4T6X
    END
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T20 - Perfil Essilor - Modulo Conecta Consulta - cupomPromocional
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T21 - Perfil LabOG - Modulo Conecta Consulta - idParCupom

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?idParCupom=2
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T22 - Perfil Essilor - Modulo Conecta Consulta - idParCupom
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T23 - Perfil LabOG - Modulo Conecta Consulta - nomeCampanha

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?nomeCampanha=Varilux em Dobro
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Salvar Quantidade Pedidos Encontrados

T24 - Perfil Essilor - Modulo Conecta Consulta - nomeCampanha
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Validar Quantidade Pedidos Encontrados

T25 - Perfil LabOG - Modulo Conecta Consulta - Cliente Sem Pedidos

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?cliente=40506388000111
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Lista Vazia

T26 - Perfil Essilor - Modulo Conecta Consulta - Cliente Sem Pedidos
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Lista Vazia

T25 - Perfil LabOG - Modulo Conecta Consulta - Cliente Sem Pedidos - CNPJ Alfanumerico

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?cliente=QO5ZWS1Q000169
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Lista Vazia

T26 - Perfil Essilor - Modulo Conecta Consulta - Cliente Sem Pedidos - CNPJ Alfanumerico
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Lista Vazia

T27 - Perfil LabOG - Modulo Conecta Consulta - Cliente Invalido

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?cliente=ab12000
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Lista Vazia

T28 - Perfil Essilor - Modulo Conecta Consulta - Cliente Invalido
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Lista Vazia

T29 - Perfil LabOG - Modulo Conecta Consulta - Consulta por /{id}

    Set Suite Variable          ${test_operacao}     /conecta-pedidos?dataInicio=2026-05-01&dataFim=2026-06-19
    GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1
        Salvar Quantidade Pedidos Encontrados

    Set Suite Variable          ${test_operacao}     /conecta-pedidos/${var_id}
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Detalhes do Pedido       sem_opticlick

T30 - Perfil Essilor - Modulo Conecta Consulta - Consulta por /{id}
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
    Set Suite Variable          ${test_operacao}     /conecta-pedidos?dataInicio=2026-05-01&dataFim=2026-06-19
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1

    Set Suite Variable          ${test_operacao}     /conecta-pedidos/${var_id}
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Detalhes do Pedido       sem_opticlick

T31 - Perfil LabOG - Modulo Conecta Consulta - Consulta por /{id} - Pedido Promo

    IF     '${env}' == 'dev'
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cupomPromocional=215KJH8SRG&idParCupom=2
    ELSE
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cupomPromocional=21SJIX4T6X&idParCupom=2
    END
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1
        Salvar Quantidade Pedidos Encontrados
        Salvar idPedidoOpticlick

    Set Suite Variable          ${test_operacao}     /conecta-pedidos/${var_id}
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Detalhes do Pedido       com_opticlick

T32 - Perfil Essilor - Modulo Conecta Consulta - Consulta por /{id} - Pedido Promo
    # altera dados - login
    Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
    IF     '${env}' == 'dev'
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cupomPromocional=215KJH8SRG&idParCupom=2
    ELSE
        Set Suite Variable          ${test_operacao}     /conecta-pedidos?cupomPromocional=21SJIX4T6X&idParCupom=2
    END
        GET Sucesso - Conecta Consulta - Params        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200/206 - Lista Pedidos     ${dados_login}[3]     1
        Salvar idPedidoOpticlick

    Set Suite Variable          ${test_operacao}     /conecta-pedidos/${var_id}
        GET Sucesso - Conecta Consulta - Params       @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Response 200 - Detalhes do Pedido       com_opticlick



*** Keywords ***
GET Sucesso - Conecta Consulta - Params
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}     ${api_proxy}    ${api_version_dev}      ${api_version_hml}     ${api_oper}

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

GET Sucesso - Conecta Consulta
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}     ${api_proxy}    ${api_version_dev}      ${api_version_hml}

    POST Autenticação JWT        ${user}    ${pwd}
    Create Session API Proxy     ${api_proxy}

    &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
    ${response}=    GET On Session         api-in-test      url=conecta-pedidos       headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}

    ${status_code}=    Convert To String    ${api_response.status_code}
    Should Contain Any        ${status_code}     200     206

    Validate ResponseTime
    Validate Header API Version      ${api_version_dev}      ${api_version_hml}     proxy
    Validate Header Content Type     application/json

Response 200/206 - Lista Pedidos
    [Arguments]     ${test_cnpjLab}      ${test_paginaAtual}
    
    ${status_code}=    Convert To String    ${api_response.status_code}
    Should Contain Any        ${status_code}     200     206

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/lista_pedidos_labog_schema.json

    ${var_paginaAtual}=     Convert To String     ${json_response}[paginaAtual]
    Should Be Equal As Strings     ${var_paginaAtual}     ${test_paginaAtual}

    ${var_lab_1}=    Set Variable    ${{ $json_response['pedidos'][0]['laboratorio'] }}
    Should Be Equal As Strings       ${var_lab_1}     ${test_cnpjLab}

    Set Test Variable     ${var_lista_206}     ${json_response}

Response 200 - Lista Vazia
    
    Status Should Be    200    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/lista_pedidos_labog_schema.json

    ${var_paginaAtual}=     Convert To String     ${json_response}[paginaAtual]
    Should Be Equal As Strings     ${var_paginaAtual}     0

    ${tamanho_pedidos}=    Get Length    ${json_response['pedidos']}
    Should Be Equal As Strings     ${tamanho_pedidos}     0

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

Salvar Quantidade Pedidos Encontrados

    Set Suite Variable     ${var_paginaAtual}     ${var_lista_206}[paginaAtual]
    Set Suite Variable     ${var_paginaTotal}     ${var_lista_206}[paginaTotal]
    Set Suite Variable     ${var_quantidadePedidosTotal}             ${var_lista_206}[quantidadePedidosTotal]
    Set Suite Variable     ${var_quantidadePedidosNaPaginaAtual}     ${var_lista_206}[quantidadePedidosNaPaginaAtual]
    Set Suite Variable     ${var_idPedidoOtica}     ${{ $var_lista_206['pedidos'][0]['idPedidoOtica'] }}
    Set Suite Variable     ${var_id}                ${{ $var_lista_206['pedidos'][0]['id'] }}

Salvar idPedidoOpticlick

    # Filtra a lista e traz o valor do primeiro pedido que tiver o campo populado
    ${id_opticlick}=    Set Variable    ${{ next((p['idPedidoOpticlick'] for p in $var_lista_206['pedidos'] if p.get('idPedidoOpticlick')), None) }}
    
    IF    $id_opticlick is not None
        Log To Console    Encontrado o ID Opticlick: ${id_opticlick}
        Set Suite Variable     ${var_idPedidoOpticlick}     ${id_opticlick}
    ELSE
        Fail    Nenhum pedido nesta página possui o campo idPedidoOpticlick.
    END

Validar Quantidade Pedidos Encontrados

    ${json_response}=    Set Variable    ${api_response.json()}

    Should Be Equal As Strings       ${var_paginaAtual}     ${json_response}[paginaAtual]
    Should Be Equal As Strings       ${var_paginaTotal}     ${json_response}[paginaTotal]
    Should Be Equal As Strings       ${var_quantidadePedidosTotal}             ${json_response}[quantidadePedidosTotal]
    Should Be Equal As Strings       ${var_quantidadePedidosNaPaginaAtual}     ${json_response}[quantidadePedidosNaPaginaAtual]


