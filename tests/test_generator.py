"""Testes unitarios para o generator de arquivos .robot (esqueleto).

Abrange:
- is_error_status
- generate_robot (com separacao sucesso/erro)
- Utilitarios: file name, status code, group
- Integracao com manifest (geracao de .manifest.json sidecar)
"""

import os
import json
import pytest
from service.generator import (
    get_top_level_group,
    group_requests_by_top_level,
    generate_file_name,
    generate_documentation,
    generate_settings,
    generate_variables,
    extract_status_code,
    is_error_status,
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
            "events": [],
        },
    ]


@pytest.fixture
def sample_variables():
    return {"client_id_og": "883b0194-10a8-451e-bb38-1e61828c6f8b", "baseUrl": "https://api.example.com"}


@pytest.fixture
def sample_data(sample_requests, sample_variables):
    return {"collection_name": "Test API", "variables": sample_variables, "requests": sample_requests}


# --- Tests: is_error_status ---

class TestStatusClassification:
    """Testes para classificacao de status code."""

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

    def test_204_is_not_error(self):
        assert is_error_status("204") is False

    def test_none_is_not_error(self):
        assert is_error_status(None) is False

    def test_200_is_not_error(self):
        assert is_error_status("200") is False


# --- Tests: generate_variables ---

class TestGenerateVariables:
    """Testes para geracao de variaveis."""

    def test_generates_variables(self):
        collection_vars = {"client_id_og": "883b0194", "baseUrl": "https://api.example.com"}
        result = generate_variables(collection_vars)
        assert "${client_id_og}" in result
        assert "${baseUrl}" in result
        assert "*** Variables ***" in result

    def test_skips_empty_values(self):
        result = generate_variables({"vazia": ""})
        assert "${vazia}" not in result

    def test_empty_collection_vars(self):
        result = generate_variables({})
        assert "*** Variables ***" in result


# --- Tests: generate_robot (com separacao sucesso/erro) ---

class TestGenerateRobotComSeparacao:
    """Testes de integracao com separacao sucesso/erro em arquivos."""

    def test_creates_success_and_error_files(self, sample_data, tmp_path):
        files = generate_robot(sample_data, str(tmp_path))
        assert len(files) >= 2

    def test_error_file_has_neg_prefix(self, sample_data, tmp_path):
        files = generate_robot(sample_data, str(tmp_path))
        neg_files = [f for f in files if "neg-" in os.path.basename(f)]
        assert len(neg_files) >= 1

    def test_success_file_has_sections(self, sample_data, tmp_path):
        files = generate_robot(sample_data, str(tmp_path))
        for f in files:
            if not f.endswith(".robot"):
                continue
            if "neg-" not in os.path.basename(f):
                with open(f, encoding="utf-8") as fh:
                    content = fh.read()
                assert "*** Settings ***" in content
                assert "*** Variables ***" in content
                assert "*** Test Cases ***" in content
                assert "*** Keywords ***" in content
                assert "Resource" in content

    def test_creates_output_directory(self, sample_data, tmp_path):
        output_subdir = str(tmp_path / "subdir" / "output")
        files = generate_robot(sample_data, output_subdir)
        assert len(files) > 0
        assert os.path.isdir(output_subdir)

    def test_empty_requests(self, tmp_path):
        data = {"collection_name": "Test", "variables": {}, "requests": []}
        files = generate_robot(data, str(tmp_path))
        assert files == []


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


# --- Tests: integracao manifest ---

class TestManifestIntegracao:
    """Testes para a integracao do manifest JSON sidecar no generate_robot."""

    def test_deve_gerar_manifest_json_junto_com_robot(self, sample_data, tmp_path):
        """Deve gerar um arquivo .manifest.json ao lado de cada .robot."""
        files = generate_robot(sample_data, str(tmp_path))

        manifest_files = [f for f in files if f.endswith(".manifest.json")]
        assert len(manifest_files) > 0

    def test_deve_retornar_arquivos_robot_e_manifest(self, sample_data, tmp_path):
        """Deve retornar tanto arquivos .robot quanto .manifest.json na lista."""
        files = generate_robot(sample_data, str(tmp_path))

        robot_files = [f for f in files if f.endswith(".robot")]
        manifest_files = [f for f in files if f.endswith(".manifest.json")]
        assert len(robot_files) > 0
        assert len(manifest_files) > 0

    def test_manifest_deve_conter_file_name_correspondente(self, sample_data, tmp_path):
        """Deve conter file_name correspondente ao arquivo .robot no manifest."""
        files = generate_robot(sample_data, str(tmp_path))

        manifest_files = [f for f in files if f.endswith(".manifest.json")]
        robot_files = [f for f in files if f.endswith(".robot")]

        for robot_file in robot_files:
            robot_name = os.path.basename(robot_file)
            expected_manifest = robot_name.replace(".robot", ".manifest.json")
            manifest_match = [m for m in manifest_files if os.path.basename(m) == expected_manifest]
            assert len(manifest_match) == 1, f"Manifest nao encontrado para {robot_name}"

    def test_manifest_gerado_deve_ser_json_valido(self, sample_data, tmp_path):
        """Deve gerar um manifest JSON valido (parseavel)."""
        files = generate_robot(sample_data, str(tmp_path))

        manifest_files = [f for f in files if f.endswith(".manifest.json")]
        for mf in manifest_files:
            with open(mf, encoding="utf-8") as f:
                manifest = json.load(f)
            assert "file_name" in manifest
            assert "test_cases" in manifest
