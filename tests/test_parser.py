"""Testes unitários para o parser de Postman Collection."""

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
)


# --- Fixtures ---

@pytest.fixture
def sample_collection():
    """Retorna uma collection Postman de exemplo."""
    return {
        "info": {"name": "Test Collection", "schema": "v2.1"},
        "variable": [
            {"key": "baseUrl", "value": "https://api.example.com"},
            {"key": "env", "value": "dev"},
            {"key": "api", "value": "test-api"},
            {"key": "version", "value": "v1"},
        ],
        "item": [
            {
                "name": "Grupo 1",
                "item": [
                    {
                        "name": "Teste GET",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{token}}"},
                            ],
                            "url": {
                                "raw": "{{baseUrl}}/{{env}}/{{api}}/{{version}}/users",
                                "protocol": "https",
                                "host": ["{{baseUrl}}"],
                                "path": ["{{env}}", "{{api}}", "{{version}}", "users"],
                            },
                        },
                        "event": [
                            {
                                "listen": "test",
                                "script": {"exec": ['pm.test("status", function() {});']},
                            }
                        ],
                    }
                ],
            },
            {
                "name": "Grupo 2",
                "item": [
                    {
                        "name": "Teste POST",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/{{env}}/{{api}}/{{version}}/users",
                                "protocol": "https",
                                "host": ["{{baseUrl}}"],
                                "path": ["{{env}}", "{{api}}", "{{version}}", "users"],
                            },
                            "body": {"raw": '{"name": "Joao"}'},
                        },
                    }
                ],
            },
        ],
    }


@pytest.fixture
def collection_with_disabled():
    """Collection com requests desabilitados."""
    return {
        "info": {"name": "Test", "schema": "v2.1"},
        "variable": [],
        "item": [
            {
                "name": "Grupo",
                "item": [
                    {
                        "name": "Request Normal",
                        "request": {
                            "method": "GET",
                            "url": {"raw": "https://api.example.com/normal"},
                        },
                    },
                    {
                        "name": "Request Desabilitado",
                        "disabled": True,
                        "request": {
                            "method": "GET",
                            "url": {"raw": "https://api.example.com/disabled"},
                        },
                    },
                    {
                        "name": "Request com Param Desabilitado",
                        "request": {
                            "method": "GET",
                            "url": {
                                "raw": "https://api.example.com/test?param1=value1&param2=value2",
                                "query": [
                                    {"key": "param1", "value": "value1"},
                                    {"key": "param2", "value": "value2", "disabled": True},
                                ],
                            },
                        },
                    },
                ],
            }
        ],
    }


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
        assert result["baseUrl"] == "https://api.example.com"
        assert result["env"] == "dev"
        assert result["api"] == "test-api"
        assert result["version"] == "v1"

    def test_extract_variables_empty(self):
        """Deve retornar dicionario vazio sem variaveis."""
        result = extract_variables({"variable": []})
        assert result == {}

    def test_extract_variables_missing_value(self):
        """Deve usar string vazia quando value esta faltando."""
        collection = {"variable": [{"key": "myVar"}]}
        result = extract_variables(collection)
        assert result["myVar"] == ""


# --- Tests: resolve_variables ---

class TestResolveVariables:
    """Testes para a funcao resolve_variables."""

    def test_resolve_variables_success(self):
        """Deve substituir variaveis pelo valor correto."""
        variables = {"name": "Joao", "city": "Sao Paulo"}
        result = resolve_variables("Olá {{name}}, de {{city}}", variables)
        assert result == "Olá Joao, de Sao Paulo"

    def test_resolve_variables_no_variables(self):
        """Deve retornar texto original sem variaveis."""
        result = resolve_variables("Texto sem variaveis", {})
        assert result == "Texto sem variaveis"

    def test_resolve_variables_empty_text(self):
        """Deve retornar vazio para texto vazio."""
        result = resolve_variables("", {"key": "value"})
        assert result == ""

    def test_resolve_variables_none_text(self):
        """Deve retornar None para texto None."""
        result = resolve_variables(None, {"key": "value"})
        assert result is None

    def test_resolve_variables_multiple_same(self):
        """Deve substituir todas as ocorrencias da mesma variavel."""
        variables = {"x": "10"}
        result = resolve_variables("{{x}} + {{x}} = {{x}}", variables)
        assert result == "10 + 10 = 10"

    def test_resolve_variables_nonexistent(self):
        """Deve manter variavel nao encontrada inalterada."""
        variables = {"name": "Joao"}
        result = resolve_variables("Olá {{name}}, {{missing}}", variables)
        assert result == "Olá Joao, {{missing}}"


# --- Tests: build_url ---

class TestBuildUrl:
    """Testes para a funcao build_url."""

    def test_build_url_simple(self):
        """Deve montar URL simples corretamente."""
        url_obj = {
            "raw": "https://api.example.com/users",
            "protocol": "https",
            "host": ["api", "example", "com"],
            "path": ["users"],
        }
        result = build_url(url_obj, {})
        assert result == "https://api.example.com/users"

    def test_build_url_with_variables(self):
        """Deve resolver variaveis na URL."""
        url_obj = {
            "raw": "{{baseUrl}}/{{env}}/users",
            "protocol": "https",
            "host": ["{{baseUrl}}"],
            "path": ["{{env}}", "users"],
        }
        variables = {"baseUrl": "https://api.example.com", "env": "dev"}
        result = build_url(url_obj, variables)
        assert result == "https://api.example.com/dev/users"

    def test_build_url_with_query_params(self):
        """Deve incluir query params na URL."""
        url_obj = {
            "raw": "https://api.example.com/users?id=123&name=joao",
            "protocol": "https",
            "host": ["api", "example", "com"],
            "path": ["users"],
            "query": [
                {"key": "id", "value": "123"},
                {"key": "name", "value": "joao"},
            ],
        }
        result = build_url(url_obj, {})
        assert "id=123" in result
        assert "name=joao" in result

    def test_build_url_removes_disabled_params(self):
        """Deve remover params desabilitados da URL."""
        url_obj = {
            "raw": "https://api.example.com/users?id=123&name=joao",
            "protocol": "https",
            "host": ["api", "example", "com"],
            "path": ["users"],
            "query": [
                {"key": "id", "value": "123"},
                {"key": "name", "value": "joao", "disabled": True},
            ],
        }
        result = build_url(url_obj, {})
        assert "id=123" in result
        assert "name=joao" not in result

    def test_build_url_all_params_disabled(self):
        """Deve remover toda query string se todos params estiverem desabilitados."""
        url_obj = {
            "raw": "https://api.example.com/users?id=123",
            "protocol": "https",
            "host": ["api", "example", "com"],
            "path": ["users"],
            "query": [
                {"key": "id", "value": "123", "disabled": True},
            ],
        }
        result = build_url(url_obj, {})
        assert result == "https://api.example.com/users"

    def test_build_url_empty_raw(self):
        """Deve retornar string vazia para raw vazio."""
        result = build_url({}, {})
        assert result == ""

    def test_build_url_with_disabled_param_in_url_string(self):
        """Deve filtrar params desabilitados mesmo quando estao na URL raw."""
        url_obj = {
            "raw": "https://api.example.com/test?param1=value1&param2=value2",
            "protocol": "https",
            "host": ["api", "example", "com"],
            "path": ["test"],
            "query": [
                {"key": "param1", "value": "value1"},
                {"key": "param2", "value": "value2", "disabled": True},
            ],
        }
        result = build_url(url_obj, {})
        assert "param1=value1" in result
        assert "param2=value2" not in result


# --- Tests: extract_headers ---

class TestExtractHeaders:
    """Testes para a funcao extract_headers."""

    def test_extract_headers_success(self):
        """Deve extrair headers corretamente."""
        headers = [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Authorization", "value": "Bearer token123"},
        ]
        result = extract_headers(headers, {})
        assert result["Content-Type"] == "application/json"
        assert result["Authorization"] == "Bearer token123"

    def test_extract_headers_resolves_variables(self):
        """Deve resolver variaveis nos headers."""
        headers = [{"key": "Authorization", "value": "Bearer {{token}}"}]
        variables = {"token": "abc123"}
        result = extract_headers(headers, variables)
        assert result["Authorization"] == "Bearer abc123"

    def test_extract_headers_skips_disabled(self):
        """Deve ignorar headers desabilitados."""
        headers = [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "X-Disabled", "value": "no", "disabled": True},
        ]
        result = extract_headers(headers, {})
        assert "Content-Type" in result
        assert "X-Disabled" not in result

    def test_extract_headers_empty(self):
        """Deve retornar dicionario vazio para headers vazios."""
        result = extract_headers([], {})
        assert result == {}

    def test_extract_headers_none(self):
        """Deve retornar dicionario vazio para headers None."""
        result = extract_headers(None, {})
        assert result == {}


# --- Tests: extract_body ---

class TestExtractBody:
    """Testes para a funcao extract_body."""

    def test_extract_body_raw(self):
        """Deve extrair body raw."""
        request = {"body": {"raw": '{"name": "Joao"}'}}
        result = extract_body(request)
        assert result == '{"name": "Joao"}'

    def test_extract_body_formdata(self):
        """Deve retornar body obj para formdata."""
        request = {"body": {"mode": "formdata", "formdata": []}}
        result = extract_body(request)
        assert result == {"mode": "formdata", "formdata": []}

    def test_extract_body_urlencoded(self):
        """Deve retornar body obj para urlencoded."""
        request = {"body": {"mode": "urlencoded", "urlencoded": []}}
        result = extract_body(request)
        assert result == {"mode": "urlencoded", "urlencoded": []}

    def test_extract_body_empty(self):
        """Deve retornar None para body vazio."""
        request = {}
        result = extract_body(request)
        assert result is None

    def test_extract_body_no_raw(self):
        """Deve retornar None quando nao ha body."""
        request = {"body": {}}
        result = extract_body(request)
        assert result is None


# --- Tests: extract_auth ---

class TestExtractAuth:
    """Testes para a funcao extract_auth."""

    def test_extract_auth_basic(self):
        """Deve extrair tipo de autenticacao basic."""
        request = {"auth": {"type": "basic"}}
        result = extract_auth(request)
        assert result == "basic"

    def test_extract_auth_bearer(self):
        """Deve extrair tipo de autenticacao bearer."""
        request = {"auth": {"type": "bearer"}}
        result = extract_auth(request)
        assert result == "bearer"

    def test_extract_auth_none(self):
        """Deve retornar None sem autenticacao."""
        request = {}
        result = extract_auth(request)
        assert result is None

    def test_extract_auth_empty(self):
        """Deve retornar None com auth vazio."""
        request = {"auth": {}}
        result = extract_auth(request)
        assert result is None


# --- Tests: is_request_disabled ---

class TestIsRequestDisabled:
    """Testes para a funcao is_request_disabled."""

    def test_request_disabled_flag(self):
        """Deve retornar True quando item tem disabled: true."""
        item = {"disabled": True, "request": {"method": "GET"}}
        assert is_request_disabled(item) is True

    def test_request_not_disabled(self):
        """Deve retornar False quando request esta habilitado."""
        item = {"request": {"method": "GET"}}
        assert is_request_disabled(item) is False

    def test_request_with_disabled_param(self):
        """Deve retornar True quando algum param de query esta desabilitado."""
        item = {
            "request": {
                "url": {
                    "query": [
                        {"key": "param1", "value": "value1"},
                        {"key": "param2", "value": "value2", "disabled": True},
                    ]
                }
            }
        }
        assert is_request_disabled(item) is True

    def test_request_with_all_params_enabled(self):
        """Deve retornar False quando todos params estao habilitados."""
        item = {
            "request": {
                "url": {
                    "query": [
                        {"key": "param1", "value": "value1"},
                        {"key": "param2", "value": "value2"},
                    ]
                }
            }
        }
        assert is_request_disabled(item) is False


# --- Tests: parse_request ---

class TestParseRequest:
    """Testes para a funcao parse_request."""

    def test_parse_request_basic(self):
        """Deve parsear request basico corretamente."""
        item = {
            "name": "Teste GET",
            "request": {
                "method": "GET",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "url": {"raw": "https://api.example.com/users"},
            },
        }
        result = parse_request(item, "Grupo 1", {})

        assert result["group"] == "Grupo 1"
        assert result["name"] == "Teste GET"
        assert result["method"] == "GET"
        assert result["url"] == "https://api.example.com/users"
        assert result["headers"]["Content-Type"] == "application/json"
        assert result["body"] is None
        assert result["auth"] is None
        assert result["disabled"] is False
        assert result["events"] == []

    def test_parse_request_with_events(self):
        """Deve extrair eventos do request."""
        item = {
            "name": "Teste",
            "request": {"method": "GET", "url": {"raw": "https://api.example.com"}},
            "event": [
                {
                    "listen": "test",
                    "script": {"exec": ['pm.test("ok", function() {});']},
                }
            ],
        }
        result = parse_request(item, "", {})

        assert len(result["events"]) == 1
        assert result["events"][0]["listen"] == "test"
        assert 'pm.test("ok"' in result["events"][0]["script"]

    def test_parse_request_with_auth(self):
        """Deve extrair autenticacao do request."""
        item = {
            "name": "Teste",
            "request": {
                "method": "POST",
                "url": {"raw": "https://api.example.com"},
                "auth": {"type": "bearer"},
            },
        }
        result = parse_request(item, "", {})
        assert result["auth"] == "bearer"


# --- Tests: parse_collection_items ---

class TestParseCollectionItems:
    """Testes para a funcao parse_collection_items."""

    def test_parse_nested_groups(self, sample_collection):
        """Deve navegar em grupos aninhados."""
        variables = extract_variables(sample_collection)
        results = []
        parse_collection_items(sample_collection["item"], "", variables, results)

        assert len(results) == 2
        assert results[0]["group"] == "Grupo 1 / Teste GET"
        assert results[1]["group"] == "Grupo 2 / Teste POST"

    def test_parse_collection_with_disabled(self, collection_with_disabled):
        """Deve marcar requests desabilitados corretamente."""
        variables = extract_variables(collection_with_disabled)
        results = []
        parse_collection_items(
            collection_with_disabled["item"], "", variables, results
        )

        assert len(results) == 3
        assert results[0]["disabled"] is False
        assert results[1]["disabled"] is True
        assert results[2]["disabled"] is True


# --- Tests: parse_collection (integration) ---

class TestParseCollection:
    """Testes de integracao para a funcao parse_collection."""

    def test_parse_collection_integration(self, sample_collection, tmp_path):
        """Deve parsear collection completa e salvar em arquivo temporario."""
        collection_file = tmp_path / "collection.json"
        collection_file.write_text(json.dumps(sample_collection))

        results = parse_collection(str(collection_file))

        assert len(results) == 2
        assert results[0]["method"] == "GET"
        assert results[1]["method"] == "POST"
        assert "Joao" in results[1]["body"]

    def test_parse_collection_empty(self, tmp_path):
        """Deve retornar lista vazia para collection sem items."""
        collection_file = tmp_path / "empty.json"
        collection_file.write_text('{"info": {}, "item": []}')

        results = parse_collection(str(collection_file))
        assert results == []

    def test_parse_collection_with_variables_resolved(self, tmp_path):
        """Deve resolver variaveis na collection."""
        collection = {
            "info": {"name": "Test"},
            "variable": [{"key": "baseUrl", "value": "https://resolved.com"}],
            "item": [
                {
                    "name": "Test",
                    "request": {
                        "method": "GET",
                        "url": {"raw": "{{baseUrl}}/users"},
                    },
                }
            ],
        }
        collection_file = tmp_path / "resolved.json"
        collection_file.write_text(json.dumps(collection))

        results = parse_collection(str(collection_file))
        assert results[0]["url"] == "https://resolved.com/users"
