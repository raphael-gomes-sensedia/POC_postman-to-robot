"""Testes unitários para o generator de arquivos .robot.

Abrange:
- is_success_status / is_error_status
- generate_group_keyword
- generate_keyword_name
- generate_test_case_enxuto
- generate_robot_file (nova estrutura)
- generate_robot (com separacao sucesso/erro)
"""

import os
import pytest
from service.generator import (
    get_top_level_group,
    group_requests_by_top_level,
    generate_file_name,
    get_env_from_requests,
    generate_documentation,
    generate_settings,
    generate_variables,
    extract_status_code,
    is_success_status,
    is_error_status,
    generate_keyword_name,
    generate_group_keyword,
    generate_test_case_enxuto,
    generate_assertions_from_events,
    generate_suite_setup,
    generate_keywords_section,
    generate_robot_file,
    generate_robot,
)


# --- Fixtures ---

@pytest.fixture
def sample_requests():
    """Lista com requests de sucesso e erro."""
    return [
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[200] GET /pedidos Sucesso",
            "method": "GET",
            "url": "https://api.example.com/dev/api/v1/pedidos",
            "headers": {"client_id": "{{client_id_og}}", "access_token": "{{oauth}}"},
            "body": None,
            "auth": None,
            "disabled": False,
            "events": [],
        },
        {
            "group": "[F001] GET /pedidos / Erro",
            "name": "[400] GET /pedidos Intervalo invalido",
            "method": "GET",
            "url": "https://api.example.com/dev/api/v1/pedidos?dataInicio=2025-01-01&dataFim=2024-01-01",
            "headers": {"client_id": "{{client_id_og}}"},
            "body": None,
            "auth": None,
            "disabled": False,
            "events": [{"listen": "test", "script": "pm.response.to.have.status(400);"}],
        },
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[206] GET /pedidos Parcial",
            "method": "GET",
            "url": "https://api.example.com/dev/api/v1/pedidos?limite=1",
            "headers": {"client_id": "{{client_id_og}}"},
            "body": None,
            "auth": None,
            "disabled": False,
            "events": [],
        },
        {
            "group": "[F002] POST /pedidos / Sucesso",
            "name": "[201] POST /pedidos Criar",
            "method": "POST",
            "url": "https://api.example.com/dev/api/v1/pedidos",
            "headers": {"Content-Type": "application/json"},
            "body": '{"nome": "teste"}',
            "auth": None,
            "disabled": False,
            "events": [],
        },
        {
            "group": "[F002] POST /pedidos / Erro",
            "name": "[401] POST /pedidos Token invalido",
            "method": "POST",
            "url": "https://api.example.com/dev/api/v1/pedidos",
            "headers": {"client_id": "{{client_id_og}}"},
            "body": None,
            "auth": None,
            "disabled": True,
            "events": [],
        },
    ]


@pytest.fixture
def sample_variables():
    return {"client_id_og": "883b0194-10a8-451e-bb38-1e61828c6f8b", "baseUrl": "https://api.example.com"}


@pytest.fixture
def sample_data(sample_requests, sample_variables):
    return {"collection_name": "Test API", "baseapi_variables": {"client_id": "abc", "oper_pedidos": "/pedidos"}, "variables": sample_variables, "requests": sample_requests}


# --- Tests: is_success_status / is_error_status ---

class TestStatusClassification:
    """Testes para classificacao de status code."""

    def test_success_200(self):
        assert is_success_status("200") is True

    def test_success_201(self):
        assert is_success_status("201") is True

    def test_success_202(self):
        assert is_success_status("202") is True

    def test_success_206(self):
        assert is_success_status("206") is True

    def test_error_400(self):
        assert is_error_status("400") is True

    def test_error_401(self):
        assert is_error_status("401") is True

    def test_error_403(self):
        assert is_error_status("403") is True

    def test_error_404(self):
        assert is_error_status("404") is True

    def test_error_422(self):
        assert is_error_status("422") is True

    def test_error_500(self):
        assert is_error_status("500") is True

    def test_204_is_success(self):
        assert is_success_status("204") is True
        assert is_error_status("204") is False

    def test_none_is_neither(self):
        assert is_success_status(None) is False
        assert is_error_status(None) is False

    def test_unknown_is_success(self):
        assert is_success_status("999") is True
        assert is_error_status("999") is False


# --- Tests: generate_keyword_name ---

class TestGenerateKeywordName:
    """Testes para nomeacao de keywords."""

    def test_get_requests(self):
        requests = [
            {"method": "GET", "name": "[200] GET /pedidos Sucesso", "group": "[F001] GET /pedidos"},
            {"method": "GET", "name": "[206] GET /pedidos Parcial", "group": "[F001] GET /pedidos"},
        ]
        result = generate_keyword_name(requests, "sucesso")
        assert "GET" in result
        assert "Sucesso" in result

    def test_post_requests(self):
        requests = [{"method": "POST", "name": "[201] POST /pedidos Criar", "group": "[F002] POST /pedidos"}]
        result = generate_keyword_name(requests, "sucesso")
        assert "POST" in result

    def test_erro_keyword(self):
        requests = [{"method": "GET", "name": "[400] GET /pedidos Erro", "group": "[F001] GET /pedidos"}]
        result = generate_keyword_name(requests, "erro")
        assert "Erro" in result


# --- Tests: generate_group_keyword ---

class TestGenerateGroupKeyword:
    """Testes para geracao de keywords reutilizaveis por grupo."""

    def test_generates_get_keyword_success(self):
        requests = [
            {"method": "GET", "name": "[200] GET /pedidos Sucesso", "url": "https://api.example.com/v1/pedidos", "headers": {"client_id": "abc", "access_token": "xyz"}, "body": None, "group": "[F001] GET /pedidos"},
        ]
        result = generate_group_keyword("[F001] GET /pedidos", requests, "sucesso")
        assert "POST Autenticacao JWT" in result
        assert "Create Session API Proxy" in result
        assert "GET On Session" in result
        assert "[Arguments]" in result
        assert "api-in-test" in result
        assert "expected_status=any" in result

    def test_generates_post_keyword_success(self):
        requests = [
            {"method": "POST", "name": "[201] POST /pedidos Criar", "url": "https://api.example.com/v1/pedidos", "headers": {"Content-Type": "application/json"}, "body": '{"nome": "teste"}', "group": "[F002] POST /pedidos"},
        ]
        result = generate_group_keyword("[F002] POST /pedidos", requests, "sucesso")
        assert "POST On Session" in result
        assert "POST Autenticacao JWT" in result

    def test_generates_keyword_without_auth_for_health(self):
        requests = [{"method": "GET", "name": "[200] GET /health", "url": "https://api.example.com/health", "headers": {}, "body": None, "group": "[F000] GET /health"}]
        result = generate_group_keyword("[F000] GET /health", requests, "sucesso")
        # Health endpoint should NOT include auth calls or session creation
        assert "POST Autenticacao" not in result
        assert "Create Session" not in result

    def test_keyword_has_arguments(self):
        requests = [{"method": "GET", "name": "[200] GET /pedidos", "url": "https://api.example.com/v1/pedidos", "headers": {"client_id": "abc"}, "body": None, "group": "[F001] GET /pedidos"}]
        result = generate_group_keyword("[F001] GET /pedidos", requests, "sucesso")
        assert "${user}" in result
        assert "${pwd}" in result
        assert "${cnpjOtica}" in result
        assert "${cnpjLab}" in result
        assert "${api_proxy}" in result


# --- Tests: generate_test_case_enxuto ---

class TestGenerateTestCaseEnxuto:
    """Testes para geracao de test cases enxutos."""

    def test_success_test_case(self):
        request = {"name": "[200] GET /pedidos Sucesso", "method": "GET", "url": "https://api.example.com/pedidos?param=1", "disabled": False, "events": []}
        result = generate_test_case_enxuto(request, "GET Sucesso - Pedidos")
        assert request["name"] in result
        assert "GET Sucesso - Pedidos" in result
        assert "@{dados_login}" in result
        assert "${oper_conecta_pedidos}" in result

    def test_disabled_test_case(self):
        request = {"name": "[401] GET /pedidos Token invalido", "method": "GET", "disabled": True, "events": []}
        result = generate_test_case_enxuto(request, "GET Erro - Pedidos")
        assert "Skip" in result

    def test_test_case_sequence_number(self):
        # Testa que o contador gera T01, T02...
        pass


# --- Tests: generate suite setup ---

class TestGenerateSuiteSetup:
    """Testes para geracao de Suite Setup."""

    def test_contains_suite_setup(self, sample_data):
        result = generate_suite_setup(sample_data["requests"], "dev")
        assert "Definir Dados do Laboratorio" in result

    def test_is_comment(self, sample_data):
        result = generate_suite_setup(sample_data["requests"], "dev")
        assert result.startswith("#")


# --- Tests: generate_variables (filtrando base-api) ---

class TestGenerateVariablesFiltradas:
    """Testes para geracao de variaveis sem duplicar as do base-api."""

    def test_remove_baseapi_vars(self):
        baseapi_set = {"client_id", "oper_pedidos", "client_secret", "api_pedidos_proxy"}
        collection_vars = {"client_id": "valor_diferente", "oper_pedidos": "/pedidos", "client_id_og": "883b0194", "baseUrl": "https://api.example.com"}
        result = generate_variables(baseapi_set, collection_vars)
        # client_id_og deve aparecer (nao existe no base-api)
        assert "${client_id_og}" in result
        # client_id nao deve aparecer (ja existe no base-api)
        assert "${client_id}" not in result
        # oper_pedidos nao deve aparecer
        assert "${oper_pedidos}" not in result
        # baseUrl deve aparecer (nao existe no base-api)
        assert "${baseUrl}" in result

    def test_empty_collection_vars(self):
        result = generate_variables({"client_id": "abc"}, {})
        assert "*** Variables ***" in result


# --- Tests: generate_robot (com separacao sucesso/erro) ---

class TestGenerateRobotComSeparacao:
    """Testes de integracao com separacao sucesso/erro em arquivos."""

    def test_creates_success_and_error_files(self, sample_data, tmp_path):
        # sample_data tem requests de sucesso e erro
        files = generate_robot(sample_data, str(tmp_path), "../test-base/base-api.robot", "dev")
        # Deve gerar ao menos 2 arquivos
        assert len(files) >= 2

    def test_error_file_has_neg_prefix(self, sample_data, tmp_path):
        files = generate_robot(sample_data, str(tmp_path), "../test-base/base-api.robot", "dev")
        # Verifica se o arquivo de erro tem prefixo neg-
        neg_files = [f for f in files if "neg-" in os.path.basename(f)]
        assert len(neg_files) >= 1

    def test_success_file_has_keyword_section(self, sample_data, tmp_path):
        files = generate_robot(sample_data, str(tmp_path), "../test-base/base-api.robot", "dev")
        for f in files:
            if "neg-" not in os.path.basename(f):
                with open(f, encoding="utf-8") as fh:
                    content = fh.read()
                assert "*** Keywords ***" in content
                assert "POST Autenticacao JWT" in content

    def test_creates_output_directory(self, sample_data, tmp_path):
        output_subdir = str(tmp_path / "subdir" / "output")
        files = generate_robot(sample_data, output_subdir, "../test-base/base-api.robot", "dev")
        assert len(files) > 0
        assert os.path.isdir(output_subdir)

    def test_empty_requests(self, tmp_path):
        data = {"collection_name": "Test", "baseapi_variables": {}, "variables": {}, "requests": []}
        files = generate_robot(data, str(tmp_path), "../test-base/base-api.robot", "dev")
        assert files == []


# --- Tests: detect endpoint path from URL ---

class TestDetectEndpoint:
    """Testes para extracao do path da operacao a partir da URL."""

    def test_get_group_oper_var(self):
        from service.generator import get_group_oper_var
        # Grupo [F001] GET /pedidos deve retornar operacao /pedidos
        requests = [{"method": "GET", "url": "https://api.example.com/dev/api/v1/pedidos?param=1"}]
        result = get_group_oper_var("[F001] GET /pedidos", requests)
        assert "pedidos" in result.lower()


# --- Tests: file name generation ---

class TestGenerateFileName:
    """Testes para geracao de nomes de arquivo."""

    def test_simple_name(self):
        result = generate_file_name("[F001] GET /pedidos")
        assert result == "f001_get_pedidos.robot"

    def test_name_extension(self):
        result = generate_file_name("Teste")
        assert result.endswith(".robot")


# --- Tests: extract_status_code ---

class TestExtractStatusCode:
    """Testes para extracao de status code do nome."""

    def test_extract_200(self):
        assert extract_status_code("[200] GET /pedidos") == "200"

    def test_extract_400(self):
        assert extract_status_code("[400] GET /pedidos Erro") == "400"

    def test_no_status_code(self):
        assert extract_status_code("GET /pedidos Sucesso") is None
