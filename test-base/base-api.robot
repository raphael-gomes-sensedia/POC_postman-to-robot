*** Settings ***
Documentation       common test data, libraries, paths

Library         Collections
Library         DateTime
Library         ImapLibrary2
Library         JSONLibrary
Library         OperatingSystem
Library         RequestsLibrary                                                                             
Library         String 

*** Variables ***
# ${env}        dev
# ${env}        hml

${client_id}        3b98e212-cc00-3deb-b2d9-2c7dfb7d2ca5
${client_secret}    5876deaa-e1f4-3951-a1bd-f0737e934c23

${client_id_shop9}        aaa07714-3861-4185-bcbd-4664f05a2071
${client_secret_shop9}    9b672894-0a27-4b90-9ceb-671b29f486ae

${pwd_teste}        Essilor@2019

${oper_token}       /token
${oper_oauth}       /access-token?grant_type=client_credentials
${oper_health}      /health
${oper_voucher}     /voucher

${oper_orcamentos}             /orcamentos
${oper_pedidos}                /pedidos
${oper_orcamentos_atacado}     /orcamentos-atacado
${oper_pedidos_atacado}        /pedidos-atacado
${oper_lp_orcamentos}          /lente-pronta/orcamentos
${oper_lp_pedidos}             /lente-pronta/pedidos
${oper_mfa_solicitacao}        /mfa/solicitacao
${oper_mfa_token}              /mfa/token


###                        |api                            |version dev|version hml|
@{api_auth_jwt}             autenticacao-jwt                v1.58         v1.58
@{api_certificados}         certificados-rastreabilidade    v1.2          v1.2
                                                                      
@{api_produtos_proxy}       gestao-produtos-laboratorio               v1.31         v1.30
@{api_pedidos_proxy}        gestao-pedidos-laboratorio                v1.107        v1.104
@{api_financeiro_proxy}     gestao-financeira-cliente-laboratorio     v1.10         v1.10

@{api_conecta_pedidos}      conecta-pedidos                 v1.4          v1.4
                                                                      
@{api_produtos_sgo}         gestao-produtos-sgo             v1.45         v1.45
@{api_pedidos_sgo}          gestao-pedidos-sgo              v1.73         v1.73
@{api_financeiro_sgo}       gestao-financeira-sgo           v1.12         v1.11
                                                                      
@{api_produtos_dataweb}     gestao-produtos-dataweb         v1.16         v1.16
@{api_pedidos_dataweb}      gestao-pedidos-dataweb          v1.19         v1.19
@{api_financeiro_dataweb}   gestao-financeira-dataweb       v1.8          v1.8
                                                                      
@{api_produtos_aco}         gestao-produtos-aco             v1.5          v1.5
@{api_pedidos_aco}          gestao-pedidos-aco              v1.9          v1.9
                                                                      
@{api_produtos_tecnolens}   gestao-produtos-tecnolens       v1.10         v1.10
@{api_pedidos_tecnolens}    gestao-pedidos-tecnolens        v1.13         v1.13

@{api_oracle_idcs}          idcs                            v1.9          v1.7
@{api_onboarding_labog}     on-boarding                     v1.2          v1.2



${EXPECTED_MAX_TIME_MS}     15000     # Tempo máximo esperado em milissegundos (15 segundos)

##                             |user login                           |pwd             |cnpj otica       |cnpj lab        | 
@{user_ceditop}                user_ceditop@teste.com                ceditop2021      95427308000124     03113110000158
@{user_comprol}                user_comprol@teste.com                comprol2021      15321752000121     27175413001135
@{user_embrapol}               proprietario2_embrapol@teste.com      Essilor@2019     30726569000361     00533787000157
@{user_grown}                  teste_grown_rede@teste.com            Essilor@2019     59189712000143     60570108000141
@{user_labminas}               proprietario_labminas@teste.com       Essilor@2019     26075599000388     27175413001054
@{user_labrio}                 proprietario_labrio@teste.com         Essilor@2019     18070598000150     27175413000163
@{user_optilab}                proprietario_optilab2@teste.com       Essilor@2019     00506721000178     05266329000112
@{user_repro}                  proprietario_repro@teste.com          Essilor@2019     21154956000207     83087056000152
@{user_riachuelo}              proprietario_riachuelo@teste.com      Essilor@2019     04690985000185     39049481000165
@{user_rx}                     proprietario_rx3@teste.com            Essilor@2019     11921550000160     11774798000145
@{user_technopark}             teste_redes_tkp@teste.com             Essilor@2019     64490709000103     10472499000193
@{user_tecnolens}              user_tecnolens@teste.com              tecnolens2021    26582805000184     40506388000111
@{user_unilab}                 proprietario_unilab2@teste.com        Essilor@2019     05472947000461     08038666000140
@{user_visolab}                proprietario_visolab4@teste.com       Essilor@2019     32751315000167     08964737000136

@{user_otica_lab_og}           multiplos_cnpj_04@teste.com           Essilor@2019     26156910000151     04693846000105     

@{user_adm_essilor}            administrador_essilor@teste.com       Essilor@2019     
@{user_colab_lab}              colaborador_laboratorio@teste.com     Essilor@2019     
@{user_lab_og}                 user_alliance@teste.com               Essilor@2019
    
## dados invalidos
${jwt_expirado}     eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzYjk4ZTIxMi1jYzAwLTNkZWItYjJkOS0yYzdkZmI3ZDJjYTUiLCJyZWRlT3RpY2FzIjpmYWxzZSwibXVsdGlwbGFzT3RpY2FzIjp0cnVlLCJpc3MiOiI1NC4yMzMuMTc3LjExMCIsImNvbnRhIjoiMzAyNjA4NzEwMDAxMDUiLCJDb2RlOiAiOiIwMWRiOWY0YS1lMDVkLTRmOTUtOGU1Yy03MzVhYjE1ZTNiODYiLCJwYXBlbENhdGVnb3JpYSI6IkVTU0lMT1IiLCJsYWJvcmF0b3Jpb3MiOlsiMDg5NjQ3MzcwMDAxMzYiLCI4MzA4NzA1NjAwMDE1MiIsIjQwNTA2Mzg4MDAwMTExIiwiMzkwNDk0ODEwMDAxNjUiLCIyNzE3NTQxMzAwMDE2MyIsIjA4MDM4NjY2MDAwMTQwIiwiNjA1NzAxMDgwMDAxNDEiLCIwODcxMzUzMzAwMDEyMiIsIjEwNDcyNDk5MDAwMTkzIiwiMTE3NzQ3OTgwMDAxNDUiLCI4OTUzNDc1NDAwMDEzNSIsIjAyNjE3MzcxMDAwMTQyIiwiMDA1MzM3ODcwMDAxNTciLCIwMzExMzExMDAwMDE1OCIsIjA1MjY2MzI5MDAwMTEyIiwiMjcxNzU0MTMwMDExMzUiLCIyNzE3NTQxMzAwMTA1NCJdLCJBcHA6ICI6Ik5vZW15IC0gU2Vuc2VkaWEiLCJhdWQiOiJhdXRob3JpemF0aW9uLnQwLnByb2R1Y3Rpb24uc2EtZWFzdC0xLmF3cy5zZW5zZWRpYS5uZXQiLCJtb2R1bG9zIjpbIkNvbmVjdGEgVmFudGFnZW5zIiwiVmFyaWx1eCBFc3BlY2lhbGlzdGEiLCJUcmFja2luZyIsIlBlZGlkb3MiLCJHZXN0w6NvIFBhcMOpaXMiLCJNYXJrZXRpbmcgQ2VudGVyIiwiR2VzdMOjbyBMYWJvcmF0w7NyaW9zIiwiRXNzaWxvciBTb2x1dGlvbnMiLCJTaW11bGFkb3IgVHJhbnNpdGlvbnMiLCJQZWRpZG9zIFByb21vw6fDo28iLCJQZWRpZG9zIFByb21vw6fDo28gRGV0YWxoYWRhIiwiUGVkaWRvcyBWYWxvcmVzIiwiUGVkaWRvcyBTaW11bGHDp8OjbyIsIkNvbnN1bHRhIENvbGFib3JhZG9yIiwiU1NPIiwiUGFjdG8iLCJDb25zdWx0YSBQcm9kdXRvcyBwb3IgTGFiIiwiQ29uc3VsdGEgQ3Vwb20iLCJQcm9kdXRvcyIsIkZpbmFuY2Vpcm8iLCJTdXBvcnRlIiwiUHJlw6dvcyBlIFNlcnZpw6dvcyIsIkF0YWNhZG8iLCJMZW9uYXJkbyIsIkRhc2hib2FyZCBQZWRpZG9zIiwiRXNzaWxvciBQcm9tbyIsIk15RXNzaWxvckx1eG90dGljYSIsIk1ldXMgQ29sYWJvcmFkb3JlcyIsIlNjcmlwdCBTaXR1YcOnw6NvIENhZGFzdHJhbCIsIldlYiBQZWRpZG9zIDQuMCIsIkdhcmFudGlhcyBFc3NpbG9yTHV4b3R0aWNhIiwiR2VyYXIgQ3Vwb25zIiwiTWlkaWEgTEFCcyIsIlByb21vw6fDo28gTGFib3JhdMOzcmlvIl0sImFwaXMiOlsiZ2VzdGFvLXBlZGlkb3MtbGFib3JhdG9yaW8iLCJnZXN0YW8tcHJvZHV0b3MtbGFib3JhdG9yaW8iLCJnZXN0YW8tbGFib3JhdG9yaW9zIiwiZ2VzdGFvLWZpbmFuY2VpcmEtY2xpZW50ZS1sYWJvcmF0b3JpbyIsImdlc3Rhby1wcm9tb2Nhby1sYWJvcmF0b3JpbyJdLCJ1c3VhcmlvIjp7ImVtYWlsIjoiYWRtaW5pc3RyYWRvcl9lc3NpbG9yQHRlc3RlLmNvbSIsImNwZiI6bnVsbCwibm9tZSI6IkFkbWluaXN0cmFkb3IiLCJzb2JyZW5vbWUiOiJFc3NpbG9yIiwiRmluYW5jaWFsQ2VudGVyX2MiOmZhbHNlfSwic2VnbWVudGFjYW8iOiIiLCJtdWx0aXBsb3NMYWJvcmF0b3Jpb3MiOnRydWUsImV4cCI6MzYwMCwiaWF0IjoxNzcyMDQ1Nzk4LCJqdGkiOiI4YTMzYmRmMS0xY2MzLTQ5MWMtODE0OS1iMzJiNDUzNTk0NzQiLCJwYXBlbCI6IkFkbWluaXN0cmFkb3IgRXNzaWxvciJ9.jhIP1n9TUwlqIAIawamPs8yJmM4D2azYEKGV_otFKYI
${client_id_invalido}        3b98e212-0000-3deb-b2d9-2c7dfb7d2ca5
${client_secret_invalido}    5876deaa-0000-3951-a1bd-f0737e934c23
${pwd_invalida}        123abcd

## mensagens de erro            |status_code    |codigo          |mensagem
@{msg_token_invalido}                 401         401             Access Token inválido.
@{msg_token_invalido_cert}            401         401             Access_token inválido.
@{msg_lab_nao_autorizado}             403         403             Consulta com laboratório não autorizado.
@{msg_header_sem_laboratorio}         422         422             É necessário informar o laboratório.
@{msg_erro_500}                       500         500             Tivemos uma falha momentânea de comunicação com o laboratório. Por favor, tente novamente mais tarde ou entre em contato através do nosso canal de suporte na Ferramenta Requestia (https://essilorluxottica.requestia.com/ ).
@{msg_produto_nao_encontrado}         400         10.8.ORC15      O Produto itemSequence: 1, SKU: 010203 não foi encontrado.
@{msg_id_pedido_otica_duplicado}      422         10.19.ORC33     Ordem de Compra já foi utilizada! Pedido Id: (352285) de (2026-03-03).
@{msg_requisicao_invalida}            422         422             Requisição inválida. Existem campos do formulário com formato violado. Por favor, verifique o preenchimento e o valor dos campos, e tente novamente.

@{msg_cor_armacao}                    422         422             Cor não informada. (Olho esquerdo).


*** Keywords ***
Create Session API Proxy
    [Arguments]         ${api}

    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/${api}/v1        auth=${auth}         verify=${True}


Create Session API Onboarding Proxy
    # [Arguments]         ${api}

    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/on-boarding/v1        auth=${auth}         verify=${True}

Create Session API Oracle Proxy
    [Arguments]         ${api}

    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/${api}        auth=${auth}         verify=${True}

Create Session API Adapter
    [Arguments]         ${api}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/${api}/v1                 verify=${True}

Create Session API Oauth
    ${auth}=            Create List     ${client_id}    ${client_secret}
    Create Session      api-in-test     https://api.essilor.com.br/oauth        auth=${auth}         verify=${True}

Validate ResponseTime
    ${response_time_ms}=    Evaluate    ${api_response.elapsed.total_seconds()} * 1000
    # Log To Console    Tempo de resposta da API: ${response_time_ms} ms
    Run Keyword And Ignore Error     Should Be True    ${response_time_ms} < ${EXPECTED_MAX_TIME_MS}
    # Should Be True    ${response_time_ms} < ${EXPECTED_MAX_TIME_MS}

Validate Header Content Type
    [Arguments]        ${content_type}
    ${header_content-type}=    Get From Dictionary    ${api_response.headers}    content-type

    ${content-type_length}=       Get Length    ${header_content-type}
    ##  valida se content-type <> null
    IF     '${content-type_length}' != '4'
        Should Contain     ${header_content-type}      ${content_type}
    END

Validate Header API Version
    [Arguments]        ${api_version_dev}      ${api_version_hml}      ${param_header}
    ${header_api_version}=    Get From Dictionary    ${api_response.headers}    ${param_header}

    IF      '${env}' == 'dev'
        Should Be Equal     ${header_api_version}    ${api_version_dev}
    ELSE
        Should Be Equal     ${header_api_version}    ${api_version_hml}
    END

POST Autenticação JWT
    [Arguments]         ${usuario}     ${senha}

    Create Session API Proxy      ${api_auth_jwt}[0]

    &{body_login}=    Create Dictionary    usuario=${usuario}     senha=${senha}
    &{headers}=       Create Dictionary    Content-Type=application/json    client_id=${client_id}
    ${response}=      POST On Session      api-in-test      ${oper_token}    json=${body_login}     headers=${headers}    expected_status=any

    Set Test Variable    ${api_response}    ${response}

    Validate ResponseTime
    Validate Header Content Type        application/json

    Run Keyword If      '${env}' != 'sandbox'     Validate Header API Version     ${api_auth_jwt}[1]      ${api_auth_jwt}[2]     version

    ${status_code}=    Convert To String    ${response.status_code}
    IF        '${status_code}' == '201'
        ${json_response}=    Set Variable    ${response.json()}
        Set Test Variable    ${jwt}    ${json_response}[access_token]
    ELSE
        Log To Console      Erro na Autenticação JWT status_code = ${status_code}
    END


POST Autenticação Oauth

    Create Session API Oauth

    &{headers}=     Create Dictionary       Content-Type=application/x-www-form-urlencoded    accept=application/json
    ${response}=    POST On Session         api-in-test      ${oper_oauth}    headers=${headers}    expected_status=any

    Set Test Variable    ${api_response}    ${response}

    Validate ResponseTime
    Validate Header Content Type        application/json

    ${status_code}=    Convert To String    ${response.status_code}
    IF        '${status_code}' == '201'
        ${json_response}=    Set Variable    ${response.json()}
        Set Test Variable    ${oauth}    ${json_response}[access_token]
        # Log To Console        ${oauth}
    ELSE
        # Log To Console        ${status_code}
        Set Test Variable    ${oauth}    ${EMPTY}
    END

Get Payload Orcamento
    [Arguments]     ${file_name}

    ${json_file}=   Get File    ${EXECDIR}/resources/${file_name}
    ${json_dict}=   Evaluate    json.loads($json_file)      json

    [Return]    ${json_dict}

Gerar Id Pedido Aleatorio
    ${hoje}=             Get Current Date    result_format=datetime
    ${random_number} =    Generate Random String       4        [NUMBERS]

    ${random_idpedido}=    Catenate       SEPARATOR=    ${hoje.month}    ${hoje.day}    ${hoje.hour}    ${random_number}
    Set Global Variable    ${id_pedido_otica}    ${random_idpedido}
        # Log To Console        id_pedido_otica = ${id_pedido_otica}

    ${idpedido_parc}=    Catenate       SEPARATOR=    ${hoje.month}    ${hoje.day}
    Set Global Variable    ${id_pedido_otica_parcial}    ${idpedido_parc}

    ${random_number} =    Generate Random String       2        [NUMBERS]
    ${id_numerico}=  Convert To Integer    ${random_number}
    Set Global Variable    ${qtde_atacado}    ${id_numerico}
    

Montar Datas
    ${hoje}=             Get Current Date    result_format=%Y-%m-%d
    Set Global Variable    ${data_hoje}    ${hoje}
        # Log To Console        hoje = ${data_hoje}

    ${data_1_semana}=         Subtract Time From Date     ${data_hoje}    7 days    result_format=%Y-%m-%d
    Set Global Variable    ${data_inicio}    ${data_1_semana}


Validar Mensagem de Erro
    [Arguments]      ${status_code}      ${codigo_erro}    ${msg_erro}

    Status Should Be    ${status_code}    ${api_response}

    ${json_response}=    Set Variable    ${api_response.json()}
    Validate Json By Schema File    ${json_response}    ${EXECDIR}/schemas/error_response_schema.json

    ${response_erro}=    Evaluate       json.loads($api_response.content)    json

    Ajustar Mensagem de Erro      ${codigo_erro}     ${msg_erro}

    FOR    ${item}    IN    @{response_erro}

        Should Be Equal As Strings     ${item}[codigo]       ${codigo_erro}
        Should Be Equal As Strings     ${item}[mensagem]     ${msg_erro}

    END

Ajustar Mensagem de Erro
    [Arguments]      ${codigo_erro}     ${msg_erro}

    IF     '${codigo_erro}' == 'CAMPO_INVALIDO'
        ${concat_msg}=    Catenate     ${msg_erro}      ${id_pedido_otica}
        Set Test Variable      ${msg_erro}     ${concat_msg}    
    END

    IF     '${codigo_erro}' == '10.19.ORC33'
        Montar Datas
        Set Test Variable    ${msg_erro}       Ordem de Compra já foi utilizada! Pedido Id: (${id_pedido_lab}) de (${data_hoje}).
    END

Definir Dados do Laboratorio
    [Arguments]      ${lab_teste}        ${arg_perfil}     ${test_env}

#     Labs sem modulo Atacado: Embrapol, Tecnolens, Visolab

    Set Global Variable     ${env}             ${test_env}
    Set Global Variable     ${laboratorio}     ${lab_teste}
    

    IF          '${lab_teste}' == 'Ceditop'
        Set Global Variable    @{dados_login}        @{user_ceditop}
        Set List Value    ${msg_produto_nao_encontrado}    1    CAMPO_INVALIDO
        Set List Value    ${msg_produto_nao_encontrado}    2    Produto com código 010203 não encontrado. idPedidoOtica:
        Set List Value    ${msg_id_pedido_otica_duplicado}    0    400
        Set List Value    ${msg_id_pedido_otica_duplicado}    1    CAMPO_INVALIDO
        Set List Value    ${msg_id_pedido_otica_duplicado}    2    Já existe um pedido com o idPedidoOtica informado. idPedidoOtica:
    ELSE IF     '${lab_teste}' == 'Comprol'
        Set Global Variable    @{dados_login}        @{user_comprol}
        Set List Value    ${msg_produto_nao_encontrado}    0    404
        Set List Value    ${msg_produto_nao_encontrado}    1    10.8.ORC16
        Set List Value    ${msg_produto_nao_encontrado}    2    O Serviço itemSequence: 1, SKU: 010203 não foi encontrado.
    ELSE IF     '${lab_teste}' == 'Embrapol'
        Skip      msg= ${lab_teste} não possui ambiente de teste
        # Set Global Variable    @{dados_login}        @{user_embrapol}
    ELSE IF     '${lab_teste}' == 'Grown'
        Set Global Variable    @{dados_login}        @{user_grown}
    ELSE IF     '${lab_teste}' == 'LabMinas'
        IF      '${env}' == 'dev'
            Skip      msg= ${lab_teste} configurado como LabOG em Dev
        END
        Set Global Variable    @{dados_login}        @{user_labminas}
    ELSE IF     '${lab_teste}' == 'LabRio'
        Set Global Variable    @{dados_login}        @{user_labrio}
    ELSE IF     '${lab_teste}' == 'Optilab'
        Set Global Variable    @{dados_login}        @{user_optilab}
    ELSE IF     '${lab_teste}' == 'Repro'
        Set Global Variable    @{dados_login}        @{user_repro}
    ELSE IF     '${lab_teste}' == 'Riachuelo'
        Set Global Variable    @{dados_login}        @{user_riachuelo}
    ELSE IF     '${lab_teste}' == 'RX'
        Set Global Variable    @{dados_login}        @{user_rx}
        Set List Value    ${msg_produto_nao_encontrado}    1    CAMPO_INVALIDO
        Set List Value    ${msg_produto_nao_encontrado}    2    Produto com código 010203 não encontrado. idPedidoOtica:
        Set List Value    ${msg_id_pedido_otica_duplicado}    0    400
        Set List Value    ${msg_id_pedido_otica_duplicado}    1    CAMPO_INVALIDO
        Set List Value    ${msg_id_pedido_otica_duplicado}    2    Já existe um pedido com o idPedidoOtica informado. idPedidoOtica:
    ELSE IF     '${lab_teste}' == 'Technopark'
        Set Global Variable    @{dados_login}        @{user_technopark}
    ELSE IF     '${lab_teste}' == 'Tecnolens'
        Skip      msg= ${lab_teste} - API Adapter não foi adaptada para este lab, não possui modulo Atacado
        # Set Global Variable    @{dados_login}        @{user_tecnolens}
    ELSE IF     '${lab_teste}' == 'Unilab'
        Set Global Variable    @{dados_login}        @{user_unilab}
        Set List Value    ${msg_produto_nao_encontrado}    1    CAMPO_INVALIDO
        Set List Value    ${msg_produto_nao_encontrado}    2    Produto com código 010203 não encontrado. idPedidoOtica:
        Set List Value    ${msg_id_pedido_otica_duplicado}    0    400
        Set List Value    ${msg_id_pedido_otica_duplicado}    1    CAMPO_INVALIDO
        Set List Value    ${msg_id_pedido_otica_duplicado}    2    Já existe um pedido com o idPedidoOtica informado. idPedidoOtica:
    ELSE IF     '${lab_teste}' == 'LabOG'
        Set Global Variable    @{dados_login}        @{user_otica_lab_og}
    ELSE IF     '${lab_teste}' == 'Visolab'
        Skip      msg= ${lab_teste} - API Adapter não foi adaptada para este lab, não possui modulo Atacado
        Set Global Variable    @{dados_login}        @{user_visolab}
    END


    IF          '${arg_perfil}' == 'Essilor'
        Set List Value    ${dados_login}    0    ${user_adm_essilor}[0]
        Set List Value    ${dados_login}    1    ${user_adm_essilor}[1]
    ELSE IF     '${arg_perfil}' == 'Laboratorio'
        Set List Value    ${dados_login}    0    ${user_colab_lab}[0]
        Set List Value    ${dados_login}    1    ${user_colab_lab}[1]
    ELSE IF     '${arg_perfil}' == 'LabOG'
        Set List Value    ${dados_login}    0    ${user_lab_og}[0]
        Set List Value    ${dados_login}    1    ${user_lab_og}[1]
    END

    # Log To Console        lab_teste = ${lab_teste}
    # Log To Console        arg_perfil = ${arg_perfil}
    Set Global Variable    ${teste_perfil}        ${arg_perfil}
    Log To Console        dados_login = @{dados_login}
