*** Settings ***
Documentation    [ESSL-4360][Rastreabilidade][Onda 5] APIs - Consulta de pedidos LABs OG
...              Novo modulo - Conecta Consulta
...              Consulta Pedidos LabOG na base MS/AWS
...                - validacao de resposes de erro
...    
...              API Gestão de Pedidos Laboratório
...              - GET /conecta-pedidos
...              - GET /conecta-pedidos/{id}
...    
...        command to run tests:
...        robot -d results\hml-22-06\LabOG-neg-ESSL-4360-conecta-pedidos api-modulo-tracking\neg-ESSL-4360-conecta-pedidos.robot


Resource        ../api-tests/base-api.robot

Suite Setup      Definir Dados do Laboratorio     LabOG     LabOG     hml


*** Variables ***
@{user_lab_og}          user_alliance@teste.com             Essilor@2019     26156910000151     04693846000105
@{user_lab_og}          user_alliance@teste.com             Essilor@2019     26156910000151     04693846000105
@{user_adm_essilor}     administrador_essilor@teste.com     Essilor@2019     26156910000151     04693846000105


## mensagens de erro            |status_code 0|codigo      1|mensagem        2
@{msg_lab_invalido}                403          403           Consulta permitida somente para o laboratório da conta.
@{msg_param_invalido}              400          400           Parâmetro enviado no formato incorreto.
@{msg_params_data_invalido}        400          400           Ao filtrar por data, é obrigatório o envio de ambas as datas ('dataInicio' e 'dataFim')
@{msg_data_fmt_invalido1}          400          400           O parâmetro 'dataInicio' está no formato inválido ('2026/05/01'). O formato de data esperado é 'yyyy-MM-dd' (ex: 2025-01-30).
@{msg_data_fmt_invalido2}          400          400           O parâmetro 'dataFim' está no formato inválido ('19-06-2026'). O formato de data esperado é 'yyyy-MM-dd' (ex: 2025-01-30).
@{msg_data_invalida}               400          400           A 'dataInicio' deve ser menor ou igual à 'dataFim'
@{msg_pagina_invalida}             400          400           A página deve ser maior ou igual a 1.
@{msg_limite_invalido}             400          400           O limite deve ser maior ou igual a 1.
@{msg_id_invalido}                 400          400           O id do Pedido está vazio ou com formato inválido. Tente novamente.
@{msg_id_outro_lab}                403          403           O pedido não pertence ao laboratório informado no header.
@{msg_id_nao_encontrado}           404          404           O pedido não foi encontrado.

@{msg_header_sem_lab}              422          422           É necessário informar o laboratório.
@{msg_header_sem_jwt}              401          401           Access_token inválido.
@{msg_header_sem_clientid}         401          401           App inválido.



*** Test Cases ***
T01_Neg - Perfil LabOG - Modulo Conecta Consulta - Laboratorio Diferente LabOG

    # altera dados - header - cnpjLab
    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set List Value          ${dados_login}    3    ${user_rx}[3]
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_lab_invalido}


T02_Neg - Perfil LabOG - Modulo Conecta Consulta - dataInicio

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?dataInicio=2026-05-01
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_params_data_invalido}


T03_Neg - Perfil Essilor - Modulo Conecta Consulta - dataInicio
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_params_data_invalido}


T04_Neg - Perfil LabOG - Modulo Conecta Consulta - dataFim

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?dataFim=2026-05-01
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_params_data_invalido}


T05_Neg - Perfil Essilor - Modulo Conecta Consulta - dataFim
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_params_data_invalido}

T06_Neg - Perfil LabOG - Modulo Conecta Consulta - dataInicio Maior Que A dataFim

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?dataInicio=2026-05-01&dataFim=2026-03-19
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_data_invalida}

T07_Neg - Perfil Essilor - Modulo Conecta Consulta - dataInicio Maior Que A dataFim
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_data_invalida}

T08_Neg - Perfil LabOG - Modulo Conecta Consulta - Pagina 0

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?pagina=0
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_pagina_invalida}

T09_Neg - Perfil Essilor - Modulo Conecta Consulta - Pagina 0
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_pagina_invalida}

T10_Neg - Perfil LabOG - Modulo Conecta Consulta - Pagina ab

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?pagina=ab
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_param_invalido}

T11_Neg - Perfil Essilor - Modulo Conecta Consulta - Pagina ab
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_param_invalido}

T12_Neg - Perfil LabOG - Modulo Conecta Consulta - Limite 0

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?limite=0
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_limite_invalido}

T13_Neg - Perfil Essilor - Modulo Conecta Consulta - Limite 0
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_limite_invalido}

T14_Neg - Perfil LabOG - Modulo Conecta Consulta - Limite @d

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?limite=@d
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_param_invalido}

T15_Neg - Perfil Essilor - Modulo Conecta Consulta - Limite @d
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_param_invalido}

T16_Neg - Perfil LabOG - Modulo Conecta Consulta - integradoLab Invalido

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?integradoLab=manga
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_param_invalido}

T17_Neg - Perfil Essilor - Modulo Conecta Consulta - integradoLab Invalido
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_param_invalido}

T18_Neg - Perfil LabOG - Modulo Conecta Consulta - Datas com Separador Invalido

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?dataInicio=2026/05/01&dataFim=2026/06/19
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_data_fmt_invalido1}

T19_Neg - Perfil Essilor - Modulo Conecta Consulta - Datas com Separador Invalido
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_data_fmt_invalido1}

T20_Neg - Perfil LabOG - Modulo Conecta Consulta - Datas com Formato Invalido

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos?dataInicio=2026-05-01&dataFim=19-06-2026
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_data_fmt_invalido2}

T21_Neg - Perfil Essilor - Modulo Conecta Consulta - Datas com Formato Invalido
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_data_fmt_invalido2}

T22_Neg - Perfil LabOG - Modulo Conecta Consulta - Header Sem Laboratorio

    Set Suite Variable      @{dados_login}        @{user_lab_og}
        GET Erro Header - Conecta Consulta      @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}     sem_lab
        Validar Mensagem de Erro - Conecta Consulta     @{msg_header_sem_lab}

T23_Neg - Perfil Essilor - Modulo Conecta Consulta - Header Sem Laboratorio
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro Header - Conecta Consulta      @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}     sem_lab
        Validar Mensagem de Erro - Conecta Consulta     @{msg_header_sem_lab}

T24_Neg - Perfil LabOG - Modulo Conecta Consulta - Header Sem Access Token

    Set Suite Variable      @{dados_login}        @{user_lab_og}
        GET Erro Header - Conecta Consulta      @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}     sem_jwt
        Validar Mensagem de Erro - Conecta Consulta     @{msg_header_sem_jwt}

T25_Neg - Perfil Essilor - Modulo Conecta Consulta - Header Sem Access Token
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro Header - Conecta Consulta      @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}     sem_jwt
        Validar Mensagem de Erro - Conecta Consulta     @{msg_header_sem_jwt}

## ajustado no swagger, client_id não é obrigatório
# TXX_Neg - Perfil LabOG - Modulo Conecta Consulta - Header Sem Client ID

#     Set Suite Variable      @{dados_login}        @{user_lab_og}
#         GET Erro Header - Conecta Consulta      @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}     sem_clientid
#         Validar Mensagem de Erro - Conecta Consulta     @{msg_header_sem_clientid}

# TXX_Neg - Perfil Essilor - Modulo Conecta Consulta - Header Sem Client ID
#     # altera dados - login
#     Set Suite Variable      @{dados_login}        @{user_adm_essilor}
#         GET Erro Header - Conecta Consulta      @{dados_login}    @{api_pedidos_proxy}     ${oper_conecta_pedidos}     sem_clientid
#         Validar Mensagem de Erro - Conecta Consulta     @{msg_header_sem_clientid}

T26_Neg - Perfil LabOG - Modulo Conecta Consulta - Consulta por /{id} Invalido

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos/31d446ef
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_id_invalido}

T27_Neg - Perfil Essilor - Modulo Conecta Consulta - Consulta por /{id} Invalido
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_id_invalido}

T28_Neg - Perfil LabOG - Modulo Conecta Consulta - Consulta por /{id} Outro Lab

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos/49cc8a14-abef-4b6a-a219-8a657049b477
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_id_outro_lab}

T29_Neg - Perfil Essilor - Modulo Conecta Consulta - Consulta por /{id} Outro Lab
    # altera dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_id_outro_lab}

T30_Neg - Perfil LabOG - Modulo Conecta Consulta - Consulta por /{id} Inexistente

    Set Suite Variable      @{dados_login}        @{user_lab_og}
    Set Suite Variable      ${test_operacao}      /conecta-pedidos/49cc8a14-0000-4b6a-a219-8a657049b477
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_id_nao_encontrado}

T31_Neg - Perfil Essilor - Modulo Conecta Consulta - Consulta por /{id} Inexistente
    # atualiza dados - login
    Set Suite Variable      @{dados_login}        @{user_adm_essilor}
        GET Erro - Conecta Consulta        @{dados_login}    @{api_pedidos_proxy}     ${test_operacao}
        Validar Mensagem de Erro - Conecta Consulta     @{msg_id_nao_encontrado}

*** Keywords ***
GET Erro - Conecta Consulta
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}     ${api_proxy}    ${api_version_dev}      ${api_version_hml}     ${api_oper}

    POST Autenticação JWT        ${user}    ${pwd}
    Create Session API Proxy     ${api_proxy}

    &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
    ${response}=    GET On Session         api-in-test           ${api_oper}       headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}

    ${status_code}=    Convert To String    ${api_response.status_code}

    Validate ResponseTime
    Validate Header API Version      ${api_version_dev}      ${api_version_hml}     proxy
    Validate Header Content Type     application/json

GET Erro Header - Conecta Consulta
    [Arguments]    ${user}    ${pwd}    ${cnpjOtica}    ${cnpjLab}     ${api_proxy}    ${api_version_dev}      ${api_version_hml}     ${api_oper}     ${test_header}

    POST Autenticação JWT        ${user}    ${pwd}
    Create Session API Proxy     ${api_proxy}

    IF     '${test_header}' == 'sem_lab'
        &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}
    ELSE IF      '${test_header}' == 'sem_jwt'
        &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      laboratorio=${cnpjLab}
    ELSE
        &{headers}=     Create Dictionary      Content-Type=application/json    access_token=${jwt}         laboratorio=${cnpjLab}
    END

    # &{headers}=     Create Dictionary      Content-Type=application/json    client_id=${client_id}      access_token=${jwt}      laboratorio=${cnpjLab}
    ${response}=    GET On Session         api-in-test           ${api_oper}       headers=${headers}    expected_status=any

    Set Global Variable    ${api_response}    ${response}

    ${status_code}=    Convert To String    ${api_response.status_code}

    Validate ResponseTime
    Validate Header API Version      ${api_version_dev}      ${api_version_hml}     proxy
    Validate Header Content Type     application/json

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




