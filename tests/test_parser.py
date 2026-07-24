"""Testes unitarios para o parser de Postman Collection.

Abrange:
- parse_collection com filtro F000 (autenticacao)
- is_auth_group / should_skip_group
- Funcoes de extracao e resolucao de dados
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
    parse_request,
    parse_collection_items,
    parse_collection,
    is_auth_group,
    should_skip_group,
)


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
        assert should_skip_group("API Autenticacao JWT v1") is True

    def test_keep_gestao_pedidos(self):
        assert should_skip_group("API Gestao de Pedidos Proxy v1") is False


# --- Tests: parse_collection_items (com skip auth) ---

class TestParseCollectionItemsComSkip:
    """Testes para parse_collection_items com skip de grupos de auth."""

    def test_skips_f000_group(self, sample_collection):
        variables = extract_variables(sample_collection)
        results = []
        parse_collection_items(sample_collection["item"], "", variables, results)
        assert len(results) == 1
        assert results[0]["name"] == "[200] GET /pedidos Sucesso"

    def test_skips_auth_inside_utils(self, collection_with_auth_pastas):
        variables = extract_variables(collection_with_auth_pastas)
        results = []
        parse_collection_items(collection_with_auth_pastas["item"], "", variables, results)
        assert len(results) == 1
        assert "[200] GET /pedidos" in results[0]["name"]


# --- Tests: parse_collection (com F000 filter) ---

class TestParseCollectionWithFilter:
    """Testes para parse_collection com filtro F000 e extracao de variaveis."""

    def test_f000_removed(self, sample_collection, tmp_path):
        f = tmp_path / "col.json"
        f.write_text(json.dumps(sample_collection))
        result = parse_collection(str(f))
        groups = [r["group"] for r in result["requests"]]
        assert all("[F000]" not in g for g in groups)
        assert len(result["requests"]) == 1

    def test_variables_preserved(self, sample_collection, tmp_path):
        f = tmp_path / "col.json"
        f.write_text(json.dumps(sample_collection))
        result = parse_collection(str(f))
        assert result["variables"]["client_id_og"] == "883b0194-10a8-451e-bb38-1e61828c6f8b"


# --- Tests: load_collection ---

class TestLoadCollection:
    """Testes para a funcao load_collection."""

    def test_load_collection_success(self):
        mock_data = '{"info": {"name": "Test"}, "item": []}'
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = load_collection("fake_file.json")
            assert result["info"]["name"] == "Test"

    def test_load_collection_invalid_json(self):
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                load_collection("fake_file.json")


# --- Tests: extract_variables ---

class TestExtractVariables:
    """Testes para a funcao extract_variables."""

    def test_extract_variables_success(self, sample_collection):
        result = extract_variables(sample_collection)
        assert result["client_id_og"] == "883b0194-10a8-451e-bb38-1e61828c6f8b"

    def test_extract_variables_empty(self):
        result = extract_variables({"variable": []})
        assert result == {}

    def test_extract_variables_missing_value(self):
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
