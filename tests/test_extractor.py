"""
Testes do modulo extractor.

Validam a extracao deterministica de:
- Payloads: body raw JSON das requests, salvos em resources/payload_<nome>.json
- Schemas: objetos JSON inline nos test scripts do Postman, salvos em schemas/<endpoint>_schema.json

Em Java, este arquivo equivaleria a:
    class ExtractorTest {
        @Test void deveExtrairPayloadJsonValido() { ... }
        @Test void deveIgnorarBodyNaoJson() { ... }
        @Test void deveExtrairSchemaDeTestScript() { ... }
        @Test void deveRetornarRelatorioDeExtracao() { ... }
    }
"""

import json
import os
import pytest
from service.extractor import (
    extract_payloads,
    extract_schemas,
    extract_all,
    _extract_json_from_script,
)
from service.generator import generate_api_slug


# --- Fixtures ---

@pytest.fixture
def sample_requests_com_body():
    """Requests com e sem body para testar extracao de payloads."""
    return [
        {
            "group": "[F001] POST /pedidos / Sucesso",
            "name": "[201] POST /pedidos Criar",
            "method": "POST",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos",
            "headers": {"Content-Type": "application/json"},
            "body": '{"nome": "teste", "valor": 100, "itens": ["a", "b"]}',
            "auth": None,
            "events": [],
        },
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[200] GET /pedidos Listar",
            "method": "GET",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos",
            "headers": {},
            "body": None,
            "auth": None,
            "events": [],
        },
        {
            "group": "[F002] POST /pedidos / Sucesso",
            "name": "[201] POST /pedidos Criar Simplificado",
            "method": "POST",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos",
            "headers": {"Content-Type": "application/json"},
            "body": "texto nao json",
            "auth": None,
            "events": [],
        },
    ]


@pytest.fixture
def sample_requests_com_schema():
    """Requests com schemas JSON inline nos test scripts do Postman."""
    return [
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[200] GET /pedidos Sucesso",
            "method": "GET",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos",
            "headers": {},
            "body": None,
            "auth": None,
            "events": [
                {
                    "listen": "test",
                    "script": (
                        'var schema = {\n'
                        '  "type": "object",\n'
                        '  "properties": {\n'
                        '    "id": {"type": "number"},\n'
                        '    "nome": {"type": "string"}\n'
                        '  },\n'
                        '  "required": ["id", "nome"]\n'
                        '};\n'
                        'pm.expect(jsonData).to.have.jsonSchema(schema);\n'
                    ),
                }
            ],
        },
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[200] GET /pedidos Sem Schema",
            "method": "GET",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos",
            "headers": {},
            "body": None,
            "auth": None,
            "events": [
                {
                    "listen": "test",
                    "script": "pm.response.to.have.status(200);",
                }
            ],
        },
    ]


@pytest.fixture
def sample_data(sample_requests_com_body):
    """Dados completos no formato retornado por parse_collection."""
    return {
        "collection_name": "API Conecta Pedidos v1.4",
        "variables": {"client_id": "abc123"},
        "requests": sample_requests_com_body,
    }


# --- Tests: extract_payloads ---

class TestExtractPayloads:
    """Testes para a funcao extract_payloads."""

    def test_deve_extrair_payload_json_valido(self, sample_requests_com_body, tmp_path):
        """Deve extrair body JSON valido e salvar em resources/."""
        api_slug = "conecta-pedidos"
        result = extract_payloads(sample_requests_com_body, str(tmp_path), api_slug)

        assert len(result) == 1  # apenas 1 request tem body JSON valido

        payload_path = os.path.join(str(tmp_path), "resources", result[0]["file_name"])
        assert os.path.exists(payload_path)

        with open(payload_path, encoding="utf-8") as f:
            payload = json.load(f)
        assert payload["nome"] == "teste"
        assert payload["valor"] == 100

    def test_deve_ignorar_body_none(self, sample_requests_com_body, tmp_path):
        """Deve ignorar requests sem body (body None)."""
        api_slug = "conecta-pedidos"
        result = extract_payloads(sample_requests_com_body, str(tmp_path), api_slug)

        # Apenas o request[0] tem body JSON valido; request[1] tem body None,
        # request[2] tem body nao-JSON
        assert len(result) == 1

    def test_deve_ignorar_body_nao_json(self, sample_requests_com_body, tmp_path):
        """Deve ignorar requests cujo body nao e JSON valido."""
        api_slug = "conecta-pedidos"
        result = extract_payloads(sample_requests_com_body, str(tmp_path), api_slug)

        # request[2] tem body "texto nao json" — nao deve ser extraido
        nomes_arquivos = [r["file_name"] for r in result]
        assert not any("simplificado" in n.lower() for n in nomes_arquivos)

    def test_deve_criar_diretorio_resources_se_nao_existe(self, sample_requests_com_body, tmp_path):
        """Deve criar o diretorio resources/ se nao existir."""
        api_slug = "conecta-pedidos"
        resources_dir = os.path.join(str(tmp_path), "resources")
        assert not os.path.exists(resources_dir)

        extract_payloads(sample_requests_com_body, str(tmp_path), api_slug)

        assert os.path.exists(resources_dir)

    def test_deve_incluir_metodo_e_nome_no_resultado(self, sample_requests_com_body, tmp_path):
        """Deve incluir metodo, nome do teste e caminho do arquivo no resultado."""
        api_slug = "conecta-pedidos"
        result = extract_payloads(sample_requests_com_body, str(tmp_path), api_slug)

        assert result[0]["method"] == "POST"
        assert result[0]["test_name"] == "[201] POST /pedidos Criar"
        assert "file_name" in result[0]

    def test_deve_retornar_lista_vazia_se_sem_bodies(self, tmp_path):
        """Deve retornar lista vazia se nenhuma request tem body."""
        requests_sem_body = [
            {"name": "[200] GET /pedidos", "method": "GET", "body": None, "events": []},
        ]
        result = extract_payloads(requests_sem_body, str(tmp_path), "slug")
        assert result == []

    def test_deve_retornar_lista_vazia_se_lista_vazia(self, tmp_path):
        """Deve retornar lista vazia se a lista de requests e vazia."""
        result = extract_payloads([], str(tmp_path), "slug")
        assert result == []


# --- Tests: _extract_json_from_script ---

class TestExtractJsonFromScript:
    """Testes para a funcao auxiliar _extract_json_from_script."""

    def test_deve_extrair_objeto_json_inline(self):
        """Deve extrair um objeto JSON inline de um script JS."""
        script = (
            'var schema = {\n'
            '  "type": "object",\n'
            '  "properties": {\n'
            '    "id": {"type": "number"}\n'
            '  }\n'
            '};\n'
        )
        result = _extract_json_from_script(script)

        assert result is not None
        assert result["type"] == "object"
        assert "properties" in result

    def test_deve_retornar_none_se_sem_objeto_json(self):
        """Deve retornar None se o script nao contem objeto JSON."""
        script = "pm.response.to.have.status(200);"
        result = _extract_json_from_script(script)
        assert result is None

    def test_deve_retornar_none_se_script_vazio(self):
        """Deve retornar None para script vazio."""
        result = _extract_json_from_script("")
        assert result is None

    def test_deve_retornar_none_se_script_none(self):
        """Deve retornar None para script None."""
        result = _extract_json_from_script(None)
        assert result is None

    def test_deve_extrair_schema_com_required(self):
        """Deve extrair schema JSON com campo required."""
        script = (
            'var schema = {\n'
            '  "type": "object",\n'
            '  "required": ["id", "nome"],\n'
            '  "properties": {\n'
            '    "id": {"type": "number"},\n'
            '    "nome": {"type": "string"}\n'
            '  }\n'
            '};\n'
        )
        result = _extract_json_from_script(script)

        assert result is not None
        assert result["type"] == "object"
        assert "id" in result["required"]
        assert "nome" in result["required"]


# --- Tests: extract_schemas ---

class TestExtractSchemas:
    """Testes para a funcao extract_schemas."""

    def test_deve_extrair_schema_de_test_script(self, sample_requests_com_schema, tmp_path):
        """Deve extrair schema JSON do test script e salvar em schemas/."""
        api_slug = "conecta-pedidos"
        result = extract_schemas(sample_requests_com_schema, str(tmp_path), api_slug)

        assert len(result) == 1  # apenas 1 request tem schema

        schema_path = os.path.join(str(tmp_path), "schemas", result[0]["file_name"])
        assert os.path.exists(schema_path)

        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["type"] == "object"

    def test_deve_ignorar_request_sem_schema(self, sample_requests_com_schema, tmp_path):
        """Deve ignorar requests cujo test script nao tem schema JSON."""
        api_slug = "conecta-pedidos"
        result = extract_schemas(sample_requests_com_schema, str(tmp_path), api_slug)

        # Apenas request[0] tem schema; request[1] so tem status check
        assert len(result) == 1

    def test_deve_criar_diretorio_schemas_se_nao_existe(self, sample_requests_com_schema, tmp_path):
        """Deve criar o diretorio schemas/ se nao existir."""
        api_slug = "conecta-pedidos"
        schemas_dir = os.path.join(str(tmp_path), "schemas")
        assert not os.path.exists(schemas_dir)

        extract_schemas(sample_requests_com_schema, str(tmp_path), api_slug)

        assert os.path.exists(schemas_dir)

    def test_deve_retornar_lista_vazia_se_sem_schemas(self, tmp_path):
        """Deve retornar lista vazia se nenhuma request tem schema."""
        requests_sem_schema = [
            {
                "name": "[200] GET /pedidos",
                "method": "GET",
                "events": [{"listen": "test", "script": "pm.response.to.have.status(200);"}],
            },
        ]
        result = extract_schemas(requests_sem_schema, str(tmp_path), "slug")
        assert result == []


# --- Tests: extract_all ---

class TestExtractAll:
    """Testes para a funcao extract_all (orquestra payloads e schemas)."""

    def test_deve_extrair_payloads_e_schemas(self, tmp_path):
        """Deve extrair payloads e schemas em uma unica chamada."""
        requests = [
            {
                "group": "[F001] POST /pedidos / Sucesso",
                "name": "[201] POST /pedidos Criar",
                "method": "POST",
                "url": "https://api.example.com/pedidos",
                "headers": {},
                "body": '{"nome": "teste"}',
                "auth": None,
                "events": [
                    {
                        "listen": "test",
                        "script": (
                            'var schema = {"type": "object", "properties": {"id": {"type": "number"}}};\n'
                            'pm.expect(jsonData).to.have.jsonSchema(schema);\n'
                        ),
                    }
                ],
            },
        ]
        data = {
            "collection_name": "API Teste v1.0",
            "variables": {},
            "requests": requests,
        }

        result = extract_all(data, str(tmp_path))

        assert "payloads" in result
        assert "schemas" in result
        assert len(result["payloads"]) == 1
        assert len(result["schemas"]) == 1

    def test_deve_criar_ambos_diretorios(self, tmp_path):
        """Deve criar os diretorios resources/ e schemas/ se nao existirem."""
        data = {
            "collection_name": "API Teste v1.0",
            "variables": {},
            "requests": [],
        }

        extract_all(data, str(tmp_path))

        assert os.path.exists(os.path.join(str(tmp_path), "resources"))
        assert os.path.exists(os.path.join(str(tmp_path), "schemas"))

    def test_deve_retornar_listas_vazias_se_sem_requests(self, tmp_path):
        """Deve retornar listas vazias se nao ha requests."""
        data = {
            "collection_name": "API Teste v1.0",
            "variables": {},
            "requests": [],
        }

        result = extract_all(data, str(tmp_path))

        assert result["payloads"] == []
        assert result["schemas"] == []

    def test_deve_usar_api_slug_gerado_da_collection(self, sample_data, tmp_path):
        """Deve gerar api_slug a partir do nome da collection automaticamente."""
        result = extract_all(sample_data, str(tmp_path))

        # O slug gerado de "API Conecta Pedidos v1.4" e "conecta-pedidos"
        # Verificar que os arquivos foram criados no diretorio correto
        assert len(result["payloads"]) >= 1