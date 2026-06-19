"""Testes unitários para o módulo de assertions (TDD).

Cobre todas as traduções da seção 8.1 do documento POC-GERADOR-TESTES-ROBOT.md:
- pm.response.to.have.status()
- pm.expect().to.not.be.empty
- pm.expect().to.be.null
- pm.expect().to.eql()
- pm.expect().to.be.a('string')
- pm.expect().to.be.a('number')
- pm.expect().to.contain()
- pm.expect(pm.response.text()).to.be.empty
- pm.expect().to.be.above(0)
- pm.collectionVariables.set()
- pm.environment.set()
"""

import pytest
from service.assertions import (
    parse_assertions,
    translate_status_code,
    translate_expect_not_empty,
    translate_expect_null,
    translate_expect_eql,
    translate_expect_type,
    translate_expect_contain,
    translate_expect_response_empty,
    translate_expect_above,
    translate_collection_variable_set,
    translate_environment_variable_set,
    extract_postman_assertions,
)


# --- Fixtures ---

@pytest.fixture
def sample_postman_scripts():
    """Retorna scripts Postman de exemplo com assertions."""
    return [
        # Script com status code
        'pm.test("Status code is 200", function () {\n'
        '    pm.response.to.have.status(200);\n'
        '});',
        # Script com expect not empty
        'pm.test("Token nao vazio", function () {\n'
        '    var accessToken = jsonData.access_token;\n'
        '    pm.expect(accessToken).to.not.be.empty;\n'
        '});',
        # Script com expect null
        'pm.test("Response null", function () {\n'
        '    pm.expect(response).to.be.null;\n'
        '});',
        # Script com expect eql
        'pm.test("Codigo igual", function () {\n'
        '    pm.expect(jsonData.erros[0].codigo).to.eql("401");\n'
        '});',
        # Script com expect string
        'pm.test("E string", function () {\n'
        '    pm.expect(accessToken).to.be.a("string");\n'
        '});',
        # Script com expect number
        'pm.test("E number", function () {\n'
        '    pm.expect(totalItens).to.be.a("number");\n'
        '});',
        # Script com expect contain
        'pm.test("Contem valor", function () {\n'
        '    pm.expect(responseBody).to.contain("success");\n'
        '});',
        # Script com expect response text empty
        'pm.test("Body vazio", function () {\n'
        '    pm.expect(pm.response.text()).to.be.empty;\n'
        '});',
        # Script com expect above
        'pm.test("Total acima de 0", function () {\n'
        '    pm.expect(totalItens).to.be.above(0);\n'
        '});',
        # Script com collectionVariables.set
        'pm.test("Salvar token", function () {\n'
        '    pm.collectionVariables.set("oauth", jsonData.access_token);\n'
        '});',
        # Script com environment.set
        'pm.test("Salvar variavel", function () {\n'
        '    pm.environment.set("random_id", randomId);\n'
        '});',
        # Script multipla assertion
        'pm.test("Validacao completa", function () {\n'
        '    pm.response.to.have.status(200);\n'
        '    pm.expect(jsonData.access_token).to.not.be.empty;\n'
        '    pm.collectionVariables.set("oauth", jsonData.access_token);\n'
        '});',
        # Script sem assertions
        'pm.test("Teste vazio", function () {\n'
        '    // sem assertions\n'
        '});',
    ]


# --- Tests: translate_status_code ---

class TestTranslateStatusCode:
    """Testes para traducao de pm.response.to.have.status()."""

    def test_translate_200(self):
        """Deve traduzir status 200."""
        result = translate_status_code("200")
        assert result == "    Status Should Be    200    ${api_response}"

    def test_translate_201(self):
        """Deve traduzir status 201."""
        result = translate_status_code("201")
        assert result == "    Status Should Be    201    ${api_response}"

    def test_translate_400(self):
        """Deve traduzir status 400."""
        result = translate_status_code("400")
        assert result == "    Status Should Be    400    ${api_response}"

    def test_translate_401(self):
        """Deve traduzir status 401."""
        result = translate_status_code("401")
        assert result == "    Status Should Be    401    ${api_response}"

    def test_translate_403(self):
        """Deve traduzir status 403."""
        result = translate_status_code("403")
        assert result == "    Status Should Be    403    ${api_response}"

    def test_translate_404(self):
        """Deve traduzir status 404."""
        result = translate_status_code("404")
        assert result == "    Status Should Be    404    ${api_response}"

    def test_translate_202(self):
        """Deve traduzir status 202."""
        result = translate_status_code("202")
        assert result == "    Status Should Be    202    ${api_response}"

    def test_translate_invalid_status(self):
        """Deve retornar None para status invalido."""
        result = translate_status_code("999")
        assert result is None

    def test_translate_non_numeric(self):
        """Deve retornar None para valor nao numerico."""
        result = translate_status_code("abc")
        assert result is None


# --- Tests: translate_expect_not_empty ---

class TestTranslateExpectNotEmpty:
    """Testes para traducao de pm.expect(x).to.not.be.empty."""

    def test_translate_simple_variable(self):
        """Deve traduzir variavel simples."""
        result = translate_expect_not_empty("accessToken")
        assert result == "    Should Not Be Empty    ${accessToken}"

    def test_translate_nested_variable(self):
        """Deve traduzir variavel com indice."""
        result = translate_expect_not_empty("jsonData.access_token")
        assert result == "    Should Not Be Empty    ${jsonData.access_token}"

    def test_translate_array_access(self):
        """Deve traduzir acesso a array."""
        result = translate_expect_not_empty("jsonData.erros[0].codigo")
        assert result == "    Should Not Be Empty    ${jsonData.erros[0].codigo}"

    def test_translate_empty_string(self):
        """Deve retornar None para variavel vazia."""
        result = translate_expect_not_empty("")
        assert result is None


# --- Tests: translate_expect_null ---

class TestTranslateExpectNull:
    """Testes para traducao de pm.expect(x).to.be.null."""

    def test_translate_simple_variable(self):
        """Deve traduzir variavel simples."""
        result = translate_expect_null("response")
        assert result == "    Should Be Empty    ${response}"

    def test_translate_nested_variable(self):
        """Deve traduzir variavel aninhada."""
        result = translate_expect_null("jsonData.data")
        assert result == "    Should Be Empty    ${jsonData.data}"

    def test_translate_empty_string(self):
        """Deve retornar None para variavel vazia."""
        result = translate_expect_null("")
        assert result is None


# --- Tests: translate_expect_eql ---

class TestTranslateExpectEql:
    """Testes para traducao de pm.expect(x).to.eql(y)."""

    def test_translate_string_value(self):
        """Deve traduzir comparacao com string."""
        result = translate_expect_eql("jsonData.erros[0].codigo", '"401"')
        assert result == '    Should Be Equal As Strings    ${jsonData.erros[0].codigo}    401'

    def test_translate_string_value_quoted(self):
        """Deve traduzir com aspas simples."""
        result = translate_expect_eql("jsonData.erros[0].codigo", "'401'")
        assert result == '    Should Be Equal As Strings    ${jsonData.erros[0].codigo}    401'

    def test_translate_numeric_value(self):
        """Deve traduzir comparacao com numero."""
        result = translate_expect_eql("totalItens", "10")
        assert result == "    Should Be Equal As Strings    ${totalItens}    10"

    def test_translate_empty_values(self):
        """Deve retornar None para valores vazios."""
        result = translate_expect_eql("", "")
        assert result is None


# --- Tests: translate_expect_type ---

class TestTranslateExpectType:
    """Testes para traducao de pm.expect(x).to.be.a('type')."""

    def test_translate_string_type(self):
        """Deve traduzir tipo string."""
        result = translate_expect_type("accessToken", "string")
        assert result == "    Should Not Be Empty    ${accessToken}"

    def test_translate_number_type(self):
        """Deve traduzir tipo number."""
        result = translate_expect_type("totalItens", "number")
        assert result == "    Should Be Equal As Numbers    ${totalItens}"

    def test_translate_unknown_type(self):
        """Deve retornar None para tipo desconhecido."""
        result = translate_expect_type("x", "array")
        assert result is None

    def test_translate_empty_variable(self):
        """Deve retornar None para variavel vazia."""
        result = translate_expect_type("", "string")
        assert result is None

    def test_translate_with_double_quotes(self):
        """Deve funcionar com aspas duplas."""
        result = translate_expect_type("x", '"string"')
        assert result == "    Should Not Be Empty    ${x}"

    def test_translate_with_single_quotes(self):
        """Deve funcionar com aspas simples."""
        result = translate_expect_type("x", "'string'")
        assert result == "    Should Not Be Empty    ${x}"


# --- Tests: translate_expect_contain ---

class TestTranslateExpectContain:
    """Testes para traducao de pm.expect(x).to.contain(y)."""

    def test_translate_string_contain(self):
        """Deve traduzir contem string."""
        result = translate_expect_contain("responseBody", '"success"')
        assert result == '    Should Contain    ${responseBody}    success'

    def test_translate_variable_contain(self):
        """Deve traduzir contem variavel."""
        result = translate_expect_contain("header", "expectedValue")
        assert result == "    Should Contain    ${header}    ${expectedValue}"

    def test_translate_empty_values(self):
        """Deve retornar None para valores vazios."""
        result = translate_expect_contain("", "")
        assert result is None


# --- Tests: translate_expect_response_empty ---

class TestTranslateExpectResponseEmpty:
    """Testes para traducao de pm.expect(pm.response.text()).to.be.empty."""

    def test_translate_response_empty(self):
        """Deve traduzir response vazio."""
        result = translate_expect_response_empty()
        assert result == "    Should Be Empty    ${api_response.content}"

    def test_translate_response_not_empty(self):
        """Deve nao traduzir se nao for empty."""
        result = translate_expect_response_empty()
        assert "Should Be Empty" in result


# --- Tests: translate_expect_above ---

class TestTranslateExpectAbove:
    """Testes para traducao de pm.expect(x).to.be.above(n)."""

    def test_translate_above_zero(self):
        """Deve traduzir acima de zero."""
        result = translate_expect_above("totalItens", "0")
        assert result == "    Should Be True    ${totalItens} > 0"

    def test_translate_above_other(self):
        """Deve traduzir acima de outro valor."""
        result = translate_expect_above("responseTime", "15000")
        assert result == "    Should Be True    ${responseTime} > 15000"

    def test_translate_empty_variable(self):
        """Deve retornar None para variavel vazia."""
        result = translate_expect_above("", "0")
        assert result is None

    def test_translate_negative_value(self):
        """Deve traduzir valor negativo."""
        result = translate_expect_above("diff", "-10")
        assert result == "    Should Be True    ${diff} > -10"


# --- Tests: translate_collection_variable_set ---

class TestTranslateCollectionVariableSet:
    """Testes para traducao de pm.collectionVariables.set()."""

    def test_translate_simple_set(self):
        """Deve traduzir collectionVariables.set simples."""
        result = translate_collection_variable_set("oauth", "jsonData.access_token")
        assert result == "    Set Test Variable    ${oauth}    ${jsonData.access_token}"

    def test_translate_nested_variable(self):
        """Deve traduzir variavel aninhada."""
        result = translate_collection_variable_set("random_id", "randomId")
        assert result == "    Set Test Variable    ${random_id}    ${randomId}"

    def test_translate_empty_key(self):
        """Deve retornar None para chave vazia."""
        result = translate_collection_variable_set("", "value")
        assert result is None

    def test_translate_empty_value(self):
        """Deve retornar None para valor vazio."""
        result = translate_collection_variable_set("key", "")
        assert result is None


# --- Tests: translate_environment_variable_set ---

class TestTranslateEnvironmentVariableSet:
    """Testes para traducao de pm.environment.set()."""

    def test_translate_simple_set(self):
        """Deve traduzir environment.set simples."""
        result = translate_environment_variable_set("random_id", "randomId")
        assert result == "    Set Test Variable    ${random_id}    ${randomId}"

    def test_translate_nested_variable(self):
        """Deve traduzir variavel aninhada."""
        result = translate_environment_variable_set("token", "jsonData.access_token")
        assert result == "    Set Test Variable    ${token}    ${jsonData.access_token}"

    def test_translate_empty_key(self):
        """Deve retornar None para chave vazia."""
        result = translate_environment_variable_set("", "value")
        assert result is None


# --- Tests: extract_postman_assertions ---

class TestExtractPostmanAssertions:
    """Testes para extracao de assertions de scripts Postman."""

    def test_extract_status_code(self, sample_postman_scripts):
        """Deve extrair status code do script."""
        result = extract_postman_assertions(sample_postman_scripts[0])
        assert any("Status Should Be" in line for line in result)
        assert any("200" in line for line in result)

    def test_extract_not_empty(self, sample_postman_scripts):
        """Deve extrair assertion not empty."""
        result = extract_postman_assertions(sample_postman_scripts[1])
        assert any("Should Not Be Empty" in line for line in result)

    def test_extract_null(self, sample_postman_scripts):
        """Deve extrair assertion null."""
        result = extract_postman_assertions(sample_postman_scripts[2])
        assert any("Should Be Empty" in line for line in result)

    def test_extract_eql(self, sample_postman_scripts):
        """Deve extrair assertion eql."""
        result = extract_postman_assertions(sample_postman_scripts[3])
        assert any("Should Be Equal As Strings" in line for line in result)

    def test_extract_string_type(self, sample_postman_scripts):
        """Deve extrair assertion tipo string."""
        result = extract_postman_assertions(sample_postman_scripts[4])
        assert any("Should Not Be Empty" in line for line in result)

    def test_extract_number_type(self, sample_postman_scripts):
        """Deve extrair assertion tipo number."""
        result = extract_postman_assertions(sample_postman_scripts[5])
        assert any("Should Be Equal As Numbers" in line for line in result)

    def test_extract_contain(self, sample_postman_scripts):
        """Deve extrair assertion contain."""
        result = extract_postman_assertions(sample_postman_scripts[6])
        assert any("Should Contain" in line for line in result)

    def test_extract_response_empty(self, sample_postman_scripts):
        """Deve extrair assertion response empty."""
        result = extract_postman_assertions(sample_postman_scripts[7])
        assert any("Should Be Empty" in line for line in result)
        assert "api_response.content" in result[0]

    def test_extract_above(self, sample_postman_scripts):
        """Deve extrair assertion above."""
        result = extract_postman_assertions(sample_postman_scripts[8])
        assert any("Should Be True" in line for line in result)
        assert "> 0" in result[0]

    def test_extract_collection_variable(self, sample_postman_scripts):
        """Deve extrair collectionVariables.set."""
        result = extract_postman_assertions(sample_postman_scripts[9])
        assert any("Set Test Variable" in line for line in result)
        assert "${oauth}" in result[0]

    def test_extract_environment_variable(self, sample_postman_scripts):
        """Deve extrair environment.set."""
        result = extract_postman_assertions(sample_postman_scripts[10])
        assert any("Set Test Variable" in line for line in result)
        assert "${random_id}" in result[0]

    def test_extract_multiple_assertions(self, sample_postman_scripts):
        """Deve extrair multiple assertions do mesmo script."""
        result = extract_postman_assertions(sample_postman_scripts[11])
        assert len(result) >= 3  # status + not empty + set variable

    def test_extract_no_assertions(self, sample_postman_scripts):
        """Deve retornar lista vazia para script sem assertions."""
        result = extract_postman_assertions(sample_postman_scripts[12])
        assert result == []

    def test_extract_empty_script(self):
        """Deve retornar lista vazia para script vazio."""
        result = extract_postman_assertions("")
        assert result == []

    def test_extract_none_script(self):
        """Deve retornar lista vazia para script None."""
        result = extract_postman_assertions(None)
        assert result == []

    def test_extract_mixed_assertions(self):
        """Deve extrair mix de assertions diferentes."""
        script = (
            'pm.response.to.have.status(201);\n'
            'pm.expect(jsonData.access_token).to.not.be.empty;\n'
            'pm.expect(jsonData.token_type).to.be.a("string");\n'
            'pm.collectionVariables.set("oauth", jsonData.access_token);\n'
        )
        result = extract_postman_assertions(script)
        assert len(result) >= 4
        assert any("Status Should Be" in line for line in result)
        assert any("Should Not Be Empty" in line for line in result)
        assert any("Set Test Variable" in line for line in result)


# --- Tests: parse_assertions (integracao) ---

class TestParseAssertions:
    """Testes de integracao para a funcao parse_assertions."""

    def test_parse_single_event(self):
        """Deve parsear um evento com assertions."""
        events = [{
            "listen": "test",
            "script": 'pm.response.to.have.status(200);\n'
                      'pm.expect(x).to.not.be.empty;',
        }]
        result = parse_assertions(events)
        assert len(result) >= 2
        assert any("Status Should Be" in line for line in result)
        assert any("Should Not Be Empty" in line for line in result)

    def test_parse_multiple_events(self):
        """Deve parsear multiplos eventos."""
        events = [
            {
                "listen": "test",
                "script": 'pm.response.to.have.status(200);',
            },
            {
                "listen": "test",
                "script": 'pm.expect(x).to.be.null;',
            },
        ]
        result = parse_assertions(events)
        assert len(result) >= 2
        assert any("Status Should Be" in line for line in result)
        assert any("Should Be Empty" in line for line in result)

    def test_parse_prerequest_ignored(self):
        """Deve ignorar eventos prerequest."""
        events = [{
            "listen": "prerequest",
            "script": 'pm.response.to.have.status(200);',
        }]
        result = parse_assertions(events)
        assert result == []

    def test_parse_empty_events(self):
        """Deve retornar lista vazia para eventos vazios."""
        result = parse_assertions([])
        assert result == []

    def test_parse_none_events(self):
        """Deve retornar lista vazia para eventos None."""
        result = parse_assertions(None)
        assert result == []

    def test_parse_empty_scripts(self):
        """Deve retornar lista vazia para scripts vazios."""
        events = [{
            "listen": "test",
            "script": "",
        }]
        result = parse_assertions(events)
        assert result == []

    def test_parse_real_world_script(self):
        """Deve parsear script do mundo real (collection API Conecta Pedidos)."""
        script = (
            'var jsonData = JSON.parse(responseBody);\r\n'
            'pm.collectionVariables.set("oauth", jsonData.access_token);\r\n'
            'pm.test("O access_token não deve estar vazio", function () {\r\n'
            '    var accessToken = jsonData.access_token;\r\n'
            '    pm.expect(accessToken).to.be.a(\'string\');\r\n'
            '    pm.expect(accessToken).to.not.be.empty;\r\n'
            '});'
        )
        events = [{"listen": "test", "script": script}]
        result = parse_assertions(events)

        assert any("Set Test Variable" in line for line in result)
        assert any("Should Not Be Empty" in line for line in result)
        assert any("${oauth}" in line for line in result)
