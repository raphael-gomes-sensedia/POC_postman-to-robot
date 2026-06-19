"""Testes unitários para o generator de arquivos .robot."""

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
    generate_create_session,
    generate_http_call,
    generate_status_validation,
    generate_assertions_from_events,
    generate_test_case,
    generate_keywords_section,
    generate_robot_file,
    generate_robot,
)


# --- Fixtures ---

@pytest.fixture
def sample_requests():
    """Retorna uma lista de requests de exemplo."""
    return [
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[200] GET /pedidos Sucesso",
            "method": "GET",
            "url": "https://api.example.com/dev/api/v1/pedidos",
            "headers": {"client_id": "abc", "access_token": "xyz"},
            "body": None,
            "auth": None,
            "disabled": False,
            "events": [],
        },
        {
            "group": "[F001] GET /pedidos / Erros",
            "name": "[400] GET /pedidos Erro",
            "method": "GET",
            "url": "https://api.example.com/dev/api/v1/pedidos",
            "headers": {"client_id": "abc"},
            "body": None,
            "auth": None,
            "disabled": False,
            "events": [],
        },
        {
            "group": "[F002] POST /pedidos",
            "name": "POST /pedidos Criar",
            "method": "POST",
            "url": "https://api.example.com/dev/api/v1/pedidos",
            "headers": {"Content-Type": "application/json"},
            "body": '{"nome": "teste"}',
            "auth": None,
            "disabled": False,
            "events": [],
        },
        {
            "group": "[F000] Autenticacao",
            "name": "Gerar Token",
            "method": "POST",
            "url": "https://api.example.com/oauth/access-token",
            "headers": {},
            "body": None,
            "auth": "basic",
            "disabled": False,
            "events": [],
        },
        {
            "group": "[F001] GET /pedidos",
            "name": "[200] GET /pedidos Desabilitado",
            "method": "GET",
            "url": "https://api.example.com/dev/api/v1/pedidos",
            "headers": {},
            "body": None,
            "auth": None,
            "disabled": True,
            "events": [],
        },
    ]


@pytest.fixture
def sample_variables():
    """Retorna um dicionario de variaveis de exemplo."""
    return {
        "baseUrl": "https://api.example.com",
        "env": "dev",
        "api": "test-api",
        "version": "v1",
        "empty_var": "",
    }


@pytest.fixture
def sample_data(sample_requests, sample_variables):
    """Retorna o dicionario de dados completo."""
    return {
        "collection_name": "Test Collection",
        "variables": sample_variables,
        "requests": sample_requests,
    }


# --- Tests: get_top_level_group ---

class TestGetTopLevelGroup:
    """Testes para a funcao get_top_level_group."""

    def test_simple_group(self):
        """Deve extrair o grupo de primeiro nivel."""
        result = get_top_level_group("[F001] GET /pedidos / Sucesso")
        assert result == "[F001] GET /pedidos"

    def test_single_level_group(self):
        """Deve retornar o grupo quando so ha um nivel."""
        result = get_top_level_group("Autenticacao")
        assert result == "Autenticacao"

    def test_deeply_nested_group(self):
        """Deve extrair o primeiro nivel de grupo profundo."""
        result = get_top_level_group("A / B / C / D / E")
        assert result == "A"

    def test_empty_group(self):
        """Deve retornar 'Sem grupo' para caminho vazio."""
        result = get_top_level_group("")
        assert result == "Sem grupo"


# --- Tests: group_requests_by_top_level ---

class TestGroupRequestsByTopLevel:
    """Testes para a funcao group_requests_by_top_level."""

    def test_groups_by_top_level(self, sample_requests):
        """Deve agrupar requests pelo grupo de primeiro nivel."""
        groups = group_requests_by_top_level(sample_requests)

        assert len(groups) == 3
        assert "[F001] GET /pedidos" in groups
        assert "[F002] POST /pedidos" in groups
        assert "[F000] Autenticacao" in groups
        assert len(groups["[F001] GET /pedidos"]) == 3
        assert len(groups["[F002] POST /pedidos"]) == 1
        assert len(groups["[F000] Autenticacao"]) == 1

    def test_groups_empty(self):
        """Deve retornar dicionario vazio para lista vazia."""
        groups = group_requests_by_top_level([])
        assert groups == {}


# --- Tests: generate_file_name ---

class TestGenerateFileName:
    """Testes para a funcao generate_file_name."""

    def test_simple_name(self):
        """Deve gerar nome de arquivo a partir do grupo."""
        result = generate_file_name("[F001] GET /pedidos")
        assert result == "f001_get_pedidos.robot"

    def test_name_with_special_chars(self):
        """Deve remover caracteres especiais do nome."""
        result = generate_file_name("[F000] Autenticacao")
        assert result == "f000_autenticacao.robot"

    def test_name_with_spaces(self):
        """Deve substituir espacos por underscore."""
        result = generate_file_name("Meu Grupo de Teste")
        assert result == "meu_grupo_de_teste.robot"

    def test_name_with_numbers(self):
        """Deve manter numeros no nome."""
        result = generate_file_name("Teste 123")
        assert result == "teste_123.robot"

    def test_name_extension(self):
        """Deve sempre ter extensao .robot."""
        result = generate_file_name("Teste")
        assert result.endswith(".robot")


# --- Tests: get_env_from_requests ---

class TestGetEnvFromRequests:
    """Testes para a funcao get_env_from_requests."""

    def test_dev_env(self):
        """Deve retornar 'dev' para requests em ambiente dev."""
        requests = [{"url": "https://api.example.com/dev/api/v1/pedidos"}]
        assert get_env_from_requests(requests) == "dev"

    def test_hml_env(self):
        """Deve retornar 'hml' para requests em ambiente hml."""
        requests = [{"url": "https://api.example.com/hml/api/v1/pedidos"}]
        assert get_env_from_requests(requests) == "hml"

    def test_multiple_requests_dev(self):
        """Deve retornar 'dev' mesmo com varios requests."""
        requests = [
            {"url": "https://api.example.com/dev/api/v1/a"},
            {"url": "https://api.example.com/dev/api/v1/b"},
        ]
        assert get_env_from_requests(requests) == "dev"


# --- Tests: extract_status_code ---

class TestExtractStatusCode:
    """Testes para a funcao extract_status_code."""

    def test_extract_200(self):
        """Deve extrair status code 200."""
        assert extract_status_code("[200] GET /pedidos") == "200"

    def test_extract_400(self):
        """Deve extrair status code 400."""
        assert extract_status_code("[400] GET /pedidos Erro") == "400"

    def test_extract_401(self):
        """Deve extrair status code 401."""
        assert extract_status_code("[401] GET /pedidos Token invalido") == "401"

    def test_extract_404(self):
        """Deve extrair status code 404."""
        assert extract_status_code("[404] GET /pedidos Nao encontrado") == "404"

    def test_extract_202(self):
        """Deve extrair status code 202."""
        assert extract_status_code("[202] POST /pedidos Criado") == "202"

    def test_no_status_code(self):
        """Deve retornar None sem status code."""
        assert extract_status_code("GET /pedidos Sucesso") is None

    def test_no_brackets(self):
        """Deve retornar None sem colchetes."""
        assert extract_status_code("200 GET /pedidos") is None


# --- Tests: generate_create_session ---

class TestGenerateCreateSession:
    """Testes para a funcao generate_create_session."""

    def test_no_auth(self):
        """Deve usar API Proxy sem autenticacao."""
        request = {"auth": None}
        result = generate_create_session(request)
        assert result == "    Create Session API Proxy"

    def test_basic_auth(self):
        """Deve usar API Oauth para autenticacao basic."""
        request = {"auth": "basic"}
        result = generate_create_session(request)
        assert result == "    Create Session API Oauth"

    def test_bearer_auth(self):
        """Deve usar API Proxy para bearer (fallback)."""
        request = {"auth": "bearer"}
        result = generate_create_session(request)
        assert result == "    Create Session API Proxy"


# --- Tests: generate_http_call ---

class TestGenerateHttpCall:
    """Testes para a funcao generate_http_call."""

    def test_get_request(self):
        """Deve gerar chamada GET correta."""
        request = {"method": "GET", "url": "https://api.example.com/users", "body": None}
        result = generate_http_call(request)
        assert "GET On Session" in result
        assert "https://api.example.com/users" in result
        assert "expected_status=any" in result

    def test_post_request_with_body(self):
        """Deve gerar chamada POST com body."""
        request = {
            "method": "POST",
            "url": "https://api.example.com/users",
            "body": '{"name": "Joao"}',
        }
        result = generate_http_call(request)
        assert "POST On Session" in result
        assert "json=${body}" in result

    def test_put_request(self):
        """Deve gerar chamada PUT correta."""
        request = {"method": "PUT", "url": "https://api.example.com/users/1", "body": None}
        result = generate_http_call(request)
        assert "PUT On Session" in result

    def test_delete_request(self):
        """Deve gerar chamada DELETE correta."""
        request = {"method": "DELETE", "url": "https://api.example.com/users/1", "body": None}
        result = generate_http_call(request)
        assert "DELETE On Session" in result

    def test_patch_request(self):
        """Deve gerar chamada PATCH correta."""
        request = {"method": "PATCH", "url": "https://api.example.com/users/1", "body": None}
        result = generate_http_call(request)
        assert "PATCH On Session" in result

    def test_unknown_method_fallback_to_get(self):
        """Deve usar GET como fallback para metodo desconhecido."""
        request = {"method": "OPTIONS", "url": "https://api.example.com", "body": None}
        result = generate_http_call(request)
        assert "GET On Session" in result


# --- Tests: generate_status_validation ---

class TestGenerateStatusValidation:
    """Testes para a funcao generate_status_validation."""

    def test_status_200(self):
        """Deve gerar validacao para status 200."""
        result = generate_status_validation("200")
        assert "Status Should Be" in result
        assert "200" in result
        assert "${api_response}" in result

    def test_status_404(self):
        """Deve gerar validacao para status 404."""
        result = generate_status_validation("404")
        assert "404" in result


# --- Tests: generate_assertions_from_events ---

class TestGenerateAssertionsFromEvents:
    """Testes para a funcao generate_assertions_from_events."""

    def test_no_events(self):
        """Deve retornar lista vazia sem eventos."""
        result = generate_assertions_from_events([])
        assert result == []

    def test_detect_status_code(self):
        """Deve detectar status code no script."""
        events = [{
            "listen": "test",
            "script": 'pm.response.to.have.status(201);',
        }]
        result = generate_assertions_from_events(events)
        assert any("Status 201" in line for line in result)

    def test_detect_json_schema(self):
        """Deve detectar jsonSchema no script."""
        events = [{
            "listen": "test",
            "script": 'pm.response.to.have.jsonSchema(schema);',
        }]
        result = generate_assertions_from_events(events)
        assert any("TODO: Validar JSON Schema" in line for line in result)

    def test_detect_collection_variables_set(self):
        """Deve detectar collectionVariables.set no script."""
        events = [{
            "listen": "test",
            "script": 'pm.collectionVariables.set("oauth", jsonData.access_token);',
        }]
        result = generate_assertions_from_events(events)
        assert any("Set Test Variable ${oauth}" in line for line in result)

    def test_detect_empty_validation(self):
        """Deve detectar validacao de response vazio."""
        events = [{
            "listen": "test",
            "script": 'pm.expect(data.pedidos).to.be.empty;',
        }]
        result = generate_assertions_from_events(events)
        assert any("TODO: Validar response vazio" in line for line in result)

    def test_detect_string_type(self):
        """Deve detectar validacao de tipo string."""
        events = [{
            "listen": "test",
            "script": "pm.expect(accessToken).to.be.a('string');",
        }]
        result = generate_assertions_from_events(events)
        assert any("TODO: Validar tipo string" in line for line in result)

    def test_detect_above_zero(self):
        """Deve detectar validacao de valor > 0."""
        events = [{
            "listen": "test",
            "script": "pm.expect(totalItens).to.be.above(0);",
        }]
        result = generate_assertions_from_events(events)
        assert any("TODO: Validar valor > 0" in line for line in result)

    def test_detect_exact_equality(self):
        """Deve detectar validacao de valor exato."""
        events = [{
            "listen": "test",
            "script": 'pm.expect(jsonData.erros[0].codigo).to.eql("401");',
        }]
        result = generate_assertions_from_events(events)
        assert any("TODO: Validar valor exato" in line for line in result)

    def test_detect_not_null(self):
        """Deve detectar validacao de nao null."""
        events = [{
            "listen": "test",
            "script": "pm.expect(randomId).to.not.be.null;",
        }]
        result = generate_assertions_from_events(events)
        assert any("TODO: Validar nao null" in line for line in result)

    def test_prerequest_event_ignored(self):
        """Deve ignorar eventos prerequest."""
        events = [{
            "listen": "prerequest",
            "script": 'pm.test("test", function() {});',
        }]
        result = generate_assertions_from_events(events)
        assert result == []


# --- Tests: generate_test_case ---

class TestGenerateTestCase:
    """Testes para a funcao generate_test_case."""

    def test_enabled_test(self):
        """Deve gerar teste habilitado com chamadas HTTP."""
        request = {
            "name": "[200] GET /pedidos",
            "method": "GET",
            "url": "https://api.example.com/users",
            "disabled": False,
            "events": [],
        }
        result = generate_test_case(request)

        assert "[200] GET /pedidos" in result
        assert "GET On Session" in result
        assert "Status Should Be" in result

    def test_disabled_test(self):
        """Deve gerar teste com Skip quando desabilitado."""
        request = {
            "name": "[200] GET /pedidos Desabilitado",
            "method": "GET",
            "url": "https://api.example.com/users",
            "disabled": True,
            "events": [],
        }
        result = generate_test_case(request)

        assert "Skip" in result
        assert "Request desabilitado" in result
        assert "GET On Session" not in result

    def test_test_with_assertions(self):
        """Deve incluir assertions dos eventos."""
        request = {
            "name": "[200] GET /pedidos",
            "method": "GET",
            "url": "https://api.example.com/users",
            "disabled": False,
            "events": [{
                "listen": "test",
                "script": 'pm.expect(x).to.eql(y);',
            }],
        }
        result = generate_test_case(request)

        assert "TODO: Validar valor exato" in result

    def test_post_test_with_body(self):
        """Deve gerar teste POST com body."""
        request = {
            "name": "POST /pedidos",
            "method": "POST",
            "url": "https://api.example.com/pedidos",
            "body": '{"nome": "teste"}',
            "disabled": False,
            "events": [],
        }
        result = generate_test_case(request)

        assert "POST On Session" in result
        assert "json=${body}" in result


# --- Tests: generate_settings ---

class TestGenerateSettings:
    """Testes para a funcao generate_settings."""

    def test_contains_settings_header(self, sample_requests):
        """Deve conter cabecalho Settings."""
        result = generate_settings(sample_requests, "Test API", "../test-base/base-api.robot")
        assert "*** Settings ***" in result

    def test_contains_documentation(self, sample_requests):
        """Deve conter secao Documentation."""
        result = generate_settings(sample_requests, "Test API", "../test-base/base-api.robot")
        assert "Documentation" in result
        assert "Test API" in result

    def test_contains_resource(self, sample_requests):
        """Deve conter Resource para base-api.robot."""
        result = generate_settings(sample_requests, "Test API", "../test-base/base-api.robot")
        assert "Resource" in result
        assert "../test-base/base-api.robot" in result

    def test_contains_command(self, sample_requests):
        """Deve conter comando de execucao sugerido."""
        result = generate_settings(sample_requests, "Test API", "../test-base/base-api.robot")
        assert "command to run tests" in result
        assert "robot -d" in result


# --- Tests: generate_variables ---

class TestGenerateVariables:
    """Testes para a funcao generate_variables."""

    def test_contains_variables_header(self, sample_variables):
        """Deve conter cabecalho Variables."""
        result = generate_variables(sample_variables)
        assert "*** Variables ***" in result

    def test_includes_variables(self, sample_variables):
        """Deve incluir variaveis no arquivo."""
        result = generate_variables(sample_variables)
        assert "${baseUrl}" in result
        assert "${env}" in result
        assert "https://api.example.com" in result

    def test_excludes_empty_variables(self, sample_variables):
        """Deve excluir variaveis com valor vazio."""
        result = generate_variables(sample_variables)
        assert "${empty_var}" not in result

    def test_empty_variables(self):
        """Deve gerar secao vazia sem variaveis."""
        result = generate_variables({})
        assert "*** Variables ***" in result


# --- Tests: generate_keywords_section ---

class TestGenerateKeywordsSection:
    """Testes para a funcao generate_keywords_section."""

    def test_contains_keywords_header(self):
        """Deve conter cabecalho Keywords."""
        result = generate_keywords_section()
        assert "*** Keywords ***" in result


# --- Tests: generate_robot_file ---

class TestGenerateRobotFile:
    """Testes para a funcao generate_robot_file."""

    def test_contains_all_sections(self, sample_requests, sample_variables):
        """Deve conter todas as secoes do arquivo .robot."""
        content = generate_robot_file(
            sample_requests, "Test API", sample_variables, "../test-base/base-api.robot"
        )

        assert "*** Settings ***" in content
        assert "*** Variables ***" in content
        assert "*** Test Cases ***" in content
        assert "*** Keywords ***" in content

    def test_contains_documentation(self, sample_requests, sample_variables):
        """Deve conter documentation."""
        content = generate_robot_file(
            sample_requests, "Test API", sample_variables, "../test-base/base-api.robot"
        )
        assert "Test API" in content

    def test_contains_test_cases(self, sample_requests, sample_variables):
        """Deve conter todos os test cases."""
        content = generate_robot_file(
            sample_requests, "Test API", sample_variables, "../test-base/base-api.robot"
        )
        assert "[200] GET /pedidos Sucesso" in content
        assert "[400] GET /pedidos Erro" in content
        assert "POST /pedidos Criar" in content
        assert "Gerar Token" in content
        assert "[200] GET /pedidos Desabilitado" in content

    def test_contains_skip_for_disabled(self, sample_requests, sample_variables):
        """Deve marcar testes desabilitados com Skip."""
        content = generate_robot_file(
            sample_requests, "Test API", sample_variables, "../test-base/base-api.robot"
        )
        assert "Request desabilitado na collection Postman" in content

    def test_ends_with_newline(self, sample_requests, sample_variables):
        """Deve terminar com newline."""
        content = generate_robot_file(
            sample_requests, "Test API", sample_variables, "../test-base/base-api.robot"
        )
        assert content.endswith("\n")


# --- Tests: generate_robot (integration) ---

class TestGenerateRobot:
    """Testes de integracao para a funcao generate_robot."""

    def test_creates_files(self, sample_data, tmp_path):
        """Deve criar arquivos no diretorio de saida."""
        files = generate_robot(sample_data, str(tmp_path), "../test-base/base-api.robot", "dev")

        assert len(files) > 0
        for f in files:
            assert os.path.exists(f)

    def test_creates_one_file_per_group(self, sample_data, tmp_path):
        """Deve criar um arquivo por grupo de primeiro nivel."""
        files = generate_robot(sample_data, str(tmp_path), "../test-base/base-api.robot", "dev")

        groups = set()
        for req in sample_data["requests"]:
            groups.add(get_top_level_group(req["group"]))

        assert len(files) == len(groups)

    def test_file_content_valid(self, sample_data, tmp_path):
        """Deve gerar conteudo valido no arquivo."""
        files = generate_robot(sample_data, str(tmp_path), "../test-base/base-api.robot", "dev")

        for f in files:
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()

            assert "*** Settings ***" in content
            assert "*** Test Cases ***" in content
            assert "*** Variables ***" in content

    def test_creates_output_directory(self, sample_data, tmp_path):
        """Deve criar o diretorio de saida se nao existir."""
        output_subdir = str(tmp_path / "subdir" / "output")
        files = generate_robot(sample_data, output_subdir, "../test-base/base-api.robot", "dev")

        assert len(files) > 0
        assert os.path.isdir(output_subdir)

    def test_empty_requests(self, tmp_path):
        """Deve retornar lista vazia para requests vazios."""
        data = {"collection_name": "Test", "variables": {}, "requests": []}
        files = generate_robot(data, str(tmp_path), "../test-base/base-api.robot", "dev")

        assert files == []
