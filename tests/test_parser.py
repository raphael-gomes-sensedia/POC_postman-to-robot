"""Testes unitários para o parser de Postman Collection.

Abrange:
- parse_collection com filtro F000 (autenticacao)
- extract_baseapi_catalog
- is_auth_group / should_skip_group
"""

import json
import pytest
from unittest.mock import patch, mock_open
from service.parser import (
    load_collection,
    extract_variables,
    resolve_variables,
    build_url,
    extract_headers,
    extract_body,
    extract_auth,
    is_request_disabled,
    parse_request,
    parse_collection_items,
    parse_collection,
    is_auth_group,
    should_skip_group,
)


# --- Fixtures ---

BASEAPI_ROBOT_CONTENT = """*** Variables ***
${client_id}        3b98e212-cc00-3deb-b2d9-2c7dfb7d2ca5
${client_secret}    5876deaa-e1f4-3951-a1bd-f0737e934c23
${oper_token}       /token
${oper_oauth}       /access-token?grant_type=client_credentials
@{api_pedidos_proxy}        gestao-pedidos-laboratorio                v1.107        v1.104
@{api_produtos_proxy}       gestao-produtos-laboratorio               v1.31         v1.30
@{api_conecta_pedidos}      conecta-pedidos                 v1.4          v1.4
@{user_adm_essilor}            administrador_essilor@teste.com       Essilor@2019
@{user_lab_og}                 user_alliance@teste.com               Essilor@2019

*** Keywords ***
Create Session API Proxy
    [Arguments]         ${api}
    Create Session      api-in-test     https://api.essilor.com.br/${env}/${api}/v1

POST Autenticacao JWT
    [Arguments]         ${usuario}     ${senha}
    Create Session API Proxy      ${api_auth_jwt}[0]
"""


@pytest.fixture
def sample_collection():
    """Retorna uma collection com grupo de autenticacao e grupos de teste."""
    return {
        "info": {"name": "Test Collection", "schema": "v2.1"},
        "variable": [
            {"key": "client_id_og", "value": "883b0194-10a8-451e-bb38-1e61828c6f8b"},
        ],
        "item": [
            {
                "name": "[F000] Autenticacao",
                "item": [
                    {
                        "name": "Gerar Token",
                        "request": {
                            "method": "POST",
                            "url": {"raw": "https://api.example.com/oauth/token"},
                        },
                    },
                ],
            },
            {
                "name": "[F001] GET /pedidos",
                "item": [
                    {
                        "name": "[200] GET /pedidos Sucesso",
                        "request": {
                            "method": "GET",
                            "url": {"raw": "https://api.example.com/pedidos"},
                        },
                    },
                ],
            },
        ],
    }


@pytest.fixture
def collection_with_auth_pastas():
    """Collection com multiplas camadas e nomes de autenticacao."""
    return {
        "info": {"name": "Test", "schema": "v2.1"},
        "variable": [],
        "item": [
            {
                "name": "Utils",
                "item": [
                    {
                        "name": "API Autenticacao JWT v1",
                        "item": [
                            {
                                "name": "[F001] POST /token",
                                "item": [
                                    {
                                        "name": "[201] POST /token Sucesso",
                                        "request": {"method": "POST", "url": {"raw": "https://api.example.com/token"}},
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "API Gestao de Pedidos Proxy v1",
                        "item": [
                            {
                                "name": "Autenticacao",
                                "item": [
                                    {
                                        "name": "Gerar Token",
                                        "request": {"method": "POST", "url": {"raw": "https://api.example.com/auth"}},
                                    },
                                ],
                            },
                            {
                                "name": "[F001] GET /pedidos",
                                "item": [
                                    {
                                        "name": "[200] GET /pedidos",
                                        "request": {"method": "GET", "url": {"raw": "https://api.example.com/pedidos"}},
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }


# --- Tests: is_auth_group ---

class TestIsAuthGroup:
    """Testes para a funcao is_auth_group."""

    def test_f000_exact(self):
        assert is_auth_group("[F000] Autenticacao") is True

    def test_f000_variation(self):
        assert is_auth_group("[F000] Autenticacao JWT") is True

    def test_autenticacao_only(self):
        assert is_auth_group("Autenticacao") is True

    def test_normal_group(self):
        assert is_auth_group("[F001] GET /pedidos") is False

    def test_empty_group(self):
        assert is_auth_group("") is False

    def test_utils_with_auth_child(self):
        # Utils so deve ser ignorado se o nome da pasta for explicitamente de auth
        assert is_auth_group("Utils") is False

    def test_autenticacao_case_insensitive(self):
        assert is_auth_group("autenticacao") is True

    def test_basic_group_name(self):
        assert is_auth_group("API Gestao de Pedidos Proxy v1") is False


# --- Tests: should_skip_group ---

class TestShouldSkipGroup:
    """Testes para a funcao should_skip_group."""

    def test_skip_f000(self):
        assert should_skip_group("[F000] Autenticacao") is True

    def test_skip_autenticacao(self):
        assert should_skip_group("Autenticacao") is True

    def test_keep_normal(self):
        assert should_skip_group("[F001] GET /pedidos") is False

    def test_keep_utils(self):
        assert should_skip_group("Utils") is False

    def test_skip_api_autenticacao(self):
        # Nome que contem "Autenticacao"
        assert should_skip_group("API Autenticacao JWT v1") is True

    def test_keep_gestao_pedidos(self):
        assert should_skip_group("API Gestao de Pedidos Proxy v1") is False


# --- Tests: parse_collection_items (com skip auth) ---

class TestParseCollectionItemsComSkip:
    """Testes para parse_collection_items com skip de grupos de auth."""

    def test_skips_f000_group(self, sample_collection):
        """Deve pular requests dentro de [F000] Autenticacao."""
        variables = extract_variables(sample_collection)
        results = []
        parse_collection_items(sample_collection["item"], "", variables, results)
        # Apenas [F001] GET /pedidos deve ser incluido
        assert len(results) == 1
        assert results[0]["name"] == "[200] GET /pedidos Sucesso"

    def test_skips_auth_inside_utils(self, collection_with_auth_pastas):
        """Deve pular requests em pastas de autenticacao aninhadas."""
        variables = extract_variables(collection_with_auth_pastas)
        results = []
        parse_collection_items(collection_with_auth_pastas["item"], "", variables, results)
        # So deve ter o request de [F001] GET /pedidos
        assert len(results) == 1
        assert "[200] GET /pedidos" in results[0]["name"]


# --- Tests: parse_collection (com F000 filter) ---

class TestParseCollectionWithFilter:
    """Testes para parse_collection com filtro F000 e extracao de variaveis."""

    def test_f000_removed(self, sample_collection, tmp_path):
        """F000 nao deve aparecer na lista de requests."""
        f = tmp_path / "col.json"
        f.write_text(json.dumps(sample_collection))
        result = parse_collection(str(f))
        groups = [r["group"] for r in result["requests"]]
        assert all("[F000]" not in g for g in groups)
        assert len(result["requests"]) == 1

    def test_variables_preserved(self, sample_collection, tmp_path):
        """Variaveis da collection devem ser preservadas."""
        f = tmp_path / "col.json"
        f.write_text(json.dumps(sample_collection))
        result = parse_collection(str(f))
        assert result["variables"]["client_id_og"] == "883b0194-10a8-451e-bb38-1e61828c6f8b"


# --- Tests: load_collection ---

class TestLoadCollection:
    """Testes para a funcao load_collection."""

    def test_load_collection_success(self):
        """Deve carregar o arquivo JSON corretamente."""
        mock_data = '{"info": {"name": "Test"}, "item": []}'
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = load_collection("fake_file.json")
            assert result["info"]["name"] == "Test"

    def test_load_collection_invalid_json(self):
        """Deve levantar erro com JSON invalido."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                load_collection("fake_file.json")


# --- Tests: extract_variables ---

class TestExtractVariables:
    """Testes para a funcao extract_variables."""

    def test_extract_variables_success(self, sample_collection):
        """Deve extrair todas as variaveis da collection."""
        result = extract_variables(sample_collection)
        assert result["client_id_og"] == "883b0194-10a8-451e-bb38-1e61828c6f8b"

    def test_extract_variables_empty(self):
        """Deve retornar dicionario vazio sem variaveis."""
        result = extract_variables({"variable": []})
        assert result == {}

    def test_extract_variables_missing_value(self):
        """Deve usar string vazia quando value esta faltando."""
        c = {"variable": [{"key": "myVar"}]}
        result = extract_variables(c)
        assert result["myVar"] == ""


# --- Tests: resolve_variables ---

class TestResolveVariables:
    """Testes para a funcao resolve_variables."""

    def test_resolve_variables_success(self):
        variables = {"name": "Joao", "city": "Sao Paulo"}
        result = resolve_variables("Ola {{name}}, de {{city}}", variables)
        assert result == "Ola Joao, de Sao Paulo"

    def test_resolve_variables_no_variables(self):
        result = resolve_variables("Texto sem variaveis", {})
        assert result == "Texto sem variaveis"

    def test_resolve_variables_empty_text(self):
        result = resolve_variables("", {"key": "value"})
        assert result == ""

    def test_resolve_variables_none_text(self):
        result = resolve_variables(None, {"key": "value"})
        assert result is None

    def test_resolve_variables_multiple_same(self):
        variables = {"x": "10"}
        result = resolve_variables("{{x}} + {{x}} = {{x}}", variables)
        assert result == "10 + 10 = 10"

    def test_resolve_variables_nonexistent(self):
        variables = {"name": "Joao"}
        result = resolve_variables("Ola {{name}}, {{missing}}", variables)
        assert result == "Ola Joao, {{missing}}"


# --- Tests: build_url ---

class TestBuildUrl:
    """Testes para a funcao build_url."""

    def test_build_url_simple(self):
        url_obj = {"raw": "https://api.example.com/users", "protocol": "https", "host": ["api", "example", "com"], "path": ["users"]}
        result = build_url(url_obj, {})
        assert result == "https://api.example.com/users"

    def test_build_url_with_variables(self):
        url_obj = {"raw": "{{baseUrl}}/{{env}}/users", "protocol": "https", "host": ["{{baseUrl}}"], "path": ["{{env}}", "users"]}
        variables = {"baseUrl": "https://api.example.com", "env": "dev"}
        result = build_url(url_obj, variables)
        assert result == "https://api.example.com/dev/users"

    def test_build_url_with_query_params(self):
        url_obj = {"raw": "https://api.example.com/users?id=123", "protocol": "https", "host": ["api", "example", "com"], "path": ["users"], "query": [{"key": "id", "value": "123"}]}
        result = build_url(url_obj, {})
        assert "id=123" in result

    def test_build_url_removes_disabled_params(self):
        url_obj = {"raw": "https://api.example.com/users?id=123&name=joao", "protocol": "https", "host": ["api", "example", "com"], "path": ["users"], "query": [{"key": "id", "value": "123"}, {"key": "name", "value": "joao", "disabled": True}]}
        result = build_url(url_obj, {})
        assert "id=123" in result
        assert "name=joao" not in result

    def test_build_url_all_params_disabled(self):
        url_obj = {"raw": "https://api.example.com/users?id=123", "protocol": "https", "host": ["api", "example", "com"], "path": ["users"], "query": [{"key": "id", "value": "123", "disabled": True}]}
        result = build_url(url_obj, {})
        assert result == "https://api.example.com/users"

    def test_build_url_empty_raw(self):
        result = build_url({}, {})
        assert result == ""


# --- Tests: extract_headers ---

class TestExtractHeaders:
    """Testes para a funcao extract_headers."""

    def test_extract_headers_success(self):
        headers = [{"key": "Content-Type", "value": "application/json"}, {"key": "Authorization", "value": "Bearer token123"}]
        result = extract_headers(headers, {})
        assert result["Content-Type"] == "application/json"
        assert result["Authorization"] == "Bearer token123"

    def test_extract_headers_resolves_variables(self):
        headers = [{"key": "Authorization", "value": "Bearer {{token}}"}]
        variables = {"token": "abc123"}
        result = extract_headers(headers, variables)
        assert result["Authorization"] == "Bearer abc123"

    def test_extract_headers_skips_disabled(self):
        headers = [{"key": "Content-Type", "value": "application/json"}, {"key": "X-Disabled", "value": "no", "disabled": True}]
        result = extract_headers(headers, {})
        assert "Content-Type" in result
        assert "X-Disabled" not in result

    def test_extract_headers_empty(self):
        result = extract_headers([], {})
        assert result == {}

    def test_extract_headers_none(self):
        result = extract_headers(None, {})
        assert result == {}


# --- Tests: extract_body ---

class TestExtractBody:
    """Testes para a funcao extract_body."""

    def test_extract_body_raw(self):
        request = {"body": {"raw": '{"name": "Joao"}'}}
        result = extract_body(request)
        assert result == '{"name": "Joao"}'

    def test_extract_body_empty(self):
        request = {}
        result = extract_body(request)
        assert result is None


# --- Tests: extract_auth ---

class TestExtractAuth:
    """Testes para a funcao extract_auth."""

    def test_extract_auth_basic(self):
        request = {"auth": {"type": "basic"}}
        result = extract_auth(request)
        assert result == "basic"

    def test_extract_auth_none(self):
        request = {}
        result = extract_auth(request)
        assert result is None


# --- Tests: is_request_disabled ---

class TestIsRequestDisabled:
    """Testes para a funcao is_request_disabled."""

    def test_request_disabled_flag(self):
        item = {"disabled": True, "request": {"method": "GET"}}
        assert is_request_disabled(item) is True

    def test_request_not_disabled(self):
        item = {"request": {"method": "GET"}}
        assert is_request_disabled(item) is False

    def test_request_with_disabled_param(self):
        item = {"request": {"url": {"query": [{"key": "p1", "value": "v1"}, {"key": "p2", "value": "v2", "disabled": True}]}}}
        assert is_request_disabled(item) is True

    def test_request_with_all_params_enabled(self):
        item = {"request": {"url": {"query": [{"key": "p1", "value": "v1"}, {"key": "p2", "value": "v2"}]}}}
        assert is_request_disabled(item) is False


# --- Tests: parse_request ---

class TestParseRequest:
    """Testes para a funcao parse_request."""

    def test_parse_request_basic(self):
        item = {"name": "Teste GET", "request": {"method": "GET", "header": [{"key": "Content-Type", "value": "application/json"}], "url": {"raw": "https://api.example.com/users"}}}
        result = parse_request(item, "Grupo 1", {})
        assert result["name"] == "Teste GET"
        assert result["method"] == "GET"
        assert result["url"] == "https://api.example.com/users"

    def test_parse_request_with_events(self):
        item = {"name": "Teste", "request": {"method": "GET", "url": {"raw": "https://api.example.com"}}, "event": [{"listen": "test", "script": {"exec": ['pm.test("ok", function() {});']}}]}
        result = parse_request(item, "", {})
        assert len(result["events"]) == 1
        assert result["events"][0]["listen"] == "test"


# --- Tests: parse_collection (integration) ---

class TestParseCollection:
    """Testes de integracao para a funcao parse_collection."""

    def test_parse_collection_integration(self, sample_collection, tmp_path):
        f = tmp_path / "collection.json"
        f.write_text(json.dumps(sample_collection))
        result = parse_collection(str(f))
        assert len(result["requests"]) == 1
        assert result["requests"][0]["method"] == "GET"

    def test_parse_collection_empty(self, tmp_path):
        f = tmp_path / "empty.json"
        f.write_text('{"info": {}, "item": []}')
        result = parse_collection(str(f))
        assert result["requests"] == []

    def test_parse_collection_with_variables_resolved(self, tmp_path):
        collection = {"info": {"name": "Test"}, "variable": [{"key": "baseUrl", "value": "https://resolved.com"}], "item": [{"name": "Test", "request": {"method": "GET", "url": {"raw": "{{baseUrl}}/users"}}}]}
        f = tmp_path / "resolved.json"
        f.write_text(json.dumps(collection))
        result = parse_collection(str(f))
        assert result["requests"][0]["url"] == "https://resolved.com/users"
