"""
Testes do modulo manifest.

Validam a geracao do arquivo .manifest.json sidecar para cada arquivo .robot,
incluindo:
- Dados estruturados de cada request (method, url, headers, body, auth)
- Assertions traduzidas do Postman JS para Robot Framework (integracao com assertions.py)
- Sugestoes de mapeamento @{api_*} e ${oper_*} (integracao com mapper.py)
- Status code esperado extraido do nome do teste
- Estrutura do manifest seguindo o modelo do documento de arquitetura

Em Java, este arquivo equivaleria a:
    class ManifestTest {
        @Test void deveGerarManifestComDadosEstruturados() { ... }
        @Test void deveIncluirAssertionsTraduzidas() { ... }
        @Test void deveIncluirMapeamentosSugeridos() { ... }
    }
"""

import json
import os
import pytest
from service.manifest import generate_manifest_file
from service.generator import generate_api_slug, generate_file_name, get_top_level_group


# --- Fixtures ---

@pytest.fixture
def base_api_path():
    """Caminho fixo para o base-api.robot real do projeto."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".opencode", "context", "resource", "base-api.robot"
    )


@pytest.fixture
def sample_requests():
    """Lista com requests de sucesso e erro para testar o manifest."""
    return [
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[200] GET /pedidos Sucesso",
            "method": "GET",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos?pagina=1",
            "headers": {"Content-Type": "application/json", "client_id": "abc123"},
            "body": None,
            "auth": "bearer",
            "events": [
                {
                    "listen": "test",
                    "script": "pm.response.to.have.status(200);\npm.expect(jsonData.access_token).to.not.be.empty;",
                }
            ],
        },
        {
            "group": "[F001] GET /pedidos / Sucesso",
            "name": "[201] POST /pedidos Criar",
            "method": "POST",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos",
            "headers": {"Content-Type": "application/json"},
            "body": '{"nome": "teste", "valor": 100}',
            "auth": None,
            "events": [
                {
                    "listen": "test",
                    "script": "pm.response.to.have.status(201);",
                }
            ],
        },
        {
            "group": "[F001] GET /pedidos / Erro",
            "name": "[400] GET /pedidos Intervalo invalido",
            "method": "GET",
            "url": "https://api.example.com/dev/conecta-pedidos/v1/pedidos?dataInicio=2025-01-01",
            "headers": {"client_id": "abc123"},
            "body": None,
            "auth": None,
            "events": [],
        },
    ]


@pytest.fixture
def sample_variables():
    """Variaveis da collection para teste."""
    return {"client_id_og": "883b0194-10a8", "baseUrl": "https://api.example.com"}


@pytest.fixture
def sample_collection_name():
    """Nome da collection para teste."""
    return "API Conecta Pedidos v1.4"


# --- Tests: generate_manifest_file (estrutura basica) ---

class TestGenerateManifestFileEstrutura:
    """Testes para a estrutura basica do manifest gerado."""

    def test_deve_criar_arquivo_manifest_json(self, sample_requests, sample_variables,
                                              sample_collection_name, base_api_path, tmp_path):
        """Deve criar um arquivo .manifest.json no diretorio de saida."""
        api_slug = generate_api_slug(sample_collection_name)
        group_name = get_top_level_group(sample_requests[0]["group"])
        file_name = generate_file_name(group_name)

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        assert os.path.exists(manifest_path)
        assert manifest_path.endswith(".manifest.json")

    def test_deve_conter_file_name_no_manifest(self, sample_requests, sample_variables,
                                               sample_collection_name, base_api_path, tmp_path):
        """Deve incluir file_name no manifest."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["file_name"] == file_name

    def test_deve_conter_tipo_no_manifest(self, sample_requests, sample_variables,
                                          sample_collection_name, base_api_path, tmp_path):
        """Deve incluir tipo (sucesso/erro) no manifest."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["tipo"] == "sucesso"

    def test_deve_conter_collection_name_no_manifest(self, sample_requests, sample_variables,
                                                      sample_collection_name, base_api_path, tmp_path):
        """Deve incluir collection_name no manifest."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["collection_name"] == sample_collection_name

    def test_deve_conter_api_slug_no_manifest(self, sample_requests, sample_variables,
                                               sample_collection_name, base_api_path, tmp_path):
        """Deve incluir api_slug no manifest."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["api_slug"] == api_slug


# --- Tests: test_cases no manifest ---

class TestManifestTestCases:
    """Testes para a secao test_cases do manifest."""

    def test_deve_conter_lista_test_cases(self, sample_requests, sample_variables,
                                           sample_collection_name, base_api_path, tmp_path):
        """Deve incluir lista test_cases com um item por request."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert "test_cases" in manifest
        assert len(manifest["test_cases"]) == 2

    def test_deve_incluir_seq_numerado(self, sample_requests, sample_variables,
                                        sample_collection_name, base_api_path, tmp_path):
        """Deve incluir seq numerado (T01, T02, etc) para cada test case."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["test_cases"][0]["seq"] == "T01"
        assert manifest["test_cases"][1]["seq"] == "T02"

    def test_deve_incluir_nome_do_teste(self, sample_requests, sample_variables,
                                         sample_collection_name, base_api_path, tmp_path):
        """Deve incluir o name do teste em cada test case."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["test_cases"][0]["name"] == "[200] GET /pedidos Sucesso"

    def test_deve_incluir_dados_da_request(self, sample_requests, sample_variables,
                                             sample_collection_name, base_api_path, tmp_path):
        """Deve incluir request com method, url, headers, body e auth em cada test case."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        req = manifest["test_cases"][0]["request"]
        assert req["method"] == "GET"
        assert "pedidos" in req["url"]
        assert req["headers"]["Content-Type"] == "application/json"
        assert req["body"] is None
        assert req["auth"] == "bearer"

    def test_deve_incluir_status_code_expected(self, sample_requests, sample_variables,
                                                sample_collection_name, base_api_path, tmp_path):
        """Deve incluir status_code_expected extraido do nome do teste."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["test_cases"][0]["status_code_expected"] == "200"
        assert manifest["test_cases"][1]["status_code_expected"] == "201"

    def test_deve_incluir_status_code_none_se_nao_houver(self, sample_requests, sample_variables,
                                                          sample_collection_name, base_api_path, tmp_path):
        """Deve incluir status_code_expected como None se o nome nao tem status code."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        requests_sem_status = [{
            "group": "[F001] GET /pedidos",
            "name": "GET /pedidos sem status",
            "method": "GET",
            "url": "https://api.example.com/pedidos",
            "headers": {},
            "body": None,
            "auth": None,
            "events": [],
        }]

        manifest_path = generate_manifest_file(
            requests=requests_sem_status,
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["test_cases"][0]["status_code_expected"] is None


# --- Tests: assertions integradas (T02) ---

class TestManifestAssertions:
    """Testes para a integracao de assertions traduzidas no manifest (T02)."""

    def test_deve_incluir_assertions_com_raw_script(self, sample_requests, sample_variables,
                                                     sample_collection_name, base_api_path, tmp_path):
        """Deve incluir assertions.raw_script com o script original do Postman."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:1],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert "assertions" in manifest["test_cases"][0]
        assert "raw_script" in manifest["test_cases"][0]["assertions"]
        assert "pm.response.to.have.status(200)" in manifest["test_cases"][0]["assertions"]["raw_script"]

    def test_deve_incluir_assertions_translated(self, sample_requests, sample_variables,
                                                 sample_collection_name, base_api_path, tmp_path):
        """Deve incluir assertions.translated com as linhas Robot Framework traduzidas."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:1],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        translated = manifest["test_cases"][0]["assertions"]["translated"]
        assert isinstance(translated, list)
        assert len(translated) >= 2  # status + not empty
        assert any("Status Should Be" in line for line in translated)

    def test_deve_incluir_assertions_vazias_se_sem_events(self, sample_requests, sample_variables,
                                                           sample_collection_name, base_api_path, tmp_path):
        """Deve incluir assertions.translated vazia e raw_script vazio se nao ha events."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        # sample_requests[2] nao tem events
        manifest_path = generate_manifest_file(
            requests=[sample_requests[2]],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="erro",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["test_cases"][0]["assertions"]["translated"] == []
        assert manifest["test_cases"][0]["assertions"]["raw_script"] == ""


# --- Tests: mapeamentos integrados (T03) ---

class TestManifestMapeamentos:
    """Testes para a integracao de mapeamentos @{api_*} e ${oper_*} no manifest."""

    def test_deve_incluir_api_mapping(self, sample_requests, sample_variables,
                                       sample_collection_name, base_api_path, tmp_path):
        """Deve incluir api_mapping com sugestao de @{api_*}."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:1],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert "api_mapping" in manifest
        assert manifest["api_mapping"]["best_match"] is not None
        assert "array" in manifest["api_mapping"]["best_match"]
        assert "confidence" in manifest["api_mapping"]["best_match"]

    def test_deve_incluir_path_mapping_em_cada_test_case(self, sample_requests, sample_variables,
                                                          sample_collection_name, base_api_path, tmp_path):
        """Deve incluir path_mapping com sugestao de ${oper_*} em cada test case."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:2],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        for tc in manifest["test_cases"]:
            assert "path_mapping" in tc
            assert tc["path_mapping"]["best_match"] is not None
            assert "var" in tc["path_mapping"]["best_match"]

    def test_deve_sugerir_oper_pedidos_para_url_com_pedidos(self, sample_requests, sample_variables,
                                                              sample_collection_name, base_api_path, tmp_path):
        """Deve sugerir ${oper_pedidos} para URL que contem /pedidos."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        manifest_path = generate_manifest_file(
            requests=sample_requests[:1],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        # O slug gerado a partir de "API Conecta Pedidos v1.4" e "conecta-pedidos"
        # E deve fazer match com @{api_conecta_pedidos}
        assert manifest["api_mapping"]["best_match"]["array"] == "@{api_conecta_pedidos}"

    def test_deve_incluir_path_mapping_none_se_sem_match(self, sample_requests, sample_variables,
                                                          sample_collection_name, base_api_path, tmp_path):
        """Deve incluir path_mapping.best_match como None se nao ha match."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_get_pedidos.robot"

        requests_sem_match = [{
            "group": "[F001] GET /pedidos",
            "name": "[200] GET /pedidos",
            "method": "GET",
            "url": "https://api.example.com/rota-completamente-nova",
            "headers": {},
            "body": None,
            "auth": None,
            "events": [],
        }]

        manifest_path = generate_manifest_file(
            requests=requests_sem_match,
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["test_cases"][0]["path_mapping"]["best_match"] is None


# --- Tests: manifest com requests vazios ---

class TestManifestVazio:
    """Testes para casos de borda com manifest vazio."""

    def test_deve_gerar_manifest_com_test_cases_vazio(self, sample_variables,
                                                       sample_collection_name, base_api_path, tmp_path):
        """Deve gerar manifest com test_cases vazio se nao ha requests."""
        api_slug = generate_api_slug(sample_collection_name)
        file_name = "f001_sem_requests.robot"

        manifest_path = generate_manifest_file(
            requests=[],
            collection_name=sample_collection_name,
            variables=sample_variables,
            tipo="sucesso",
            file_name=file_name,
            api_slug=api_slug,
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["test_cases"] == []