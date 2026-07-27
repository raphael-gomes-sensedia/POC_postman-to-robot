"""
Testes do modulo checksum.

Validam a geracao e verificacao de checksum (hash) do manifest JSON para
garantir idempotencia:
- Se o manifest nao mudou, o orquestrador pode pular a regeneracao
- O checksum e incluido no proprio manifest como campo "checksum"
- A verificacao compara o hash atual dos dados vs o checksum registrado

"""

import json
import os
import pytest
from service.checksum import (
    calculate_checksum,
    verify_checksum,
    add_checksum_to_manifest,
    has_manifest_changed,
)


@pytest.fixture
def sample_manifest_data():
    """Dados de manifest sem checksum para testar."""
    return {
        "file_name": "f001_get_pedidos.robot",
        "tipo": "sucesso",
        "collection_name": "API Conecta Pedidos v1.4",
        "api_slug": "conecta-pedidos",
        "group": "F001 - GET /pedidos",
        "api_mapping": {
            "best_match": {"array": "@{api_conecta_pedidos}", "slug": "conecta-pedidos", "confidence": 1.0},
            "alternatives": [],
        },
        "test_cases": [
            {
                "seq": "T01",
                "name": "[200] GET /pedidos Sucesso",
                "request": {
                    "method": "GET",
                    "url": "https://api.example.com/pedidos",
                    "headers": {"Content-Type": "application/json"},
                    "body": None,
                    "auth": "bearer",
                },
                "assertions": {
                    "raw_script": "pm.response.to.have.status(200);",
                    "translated": ["    Status Should Be    200    ${api_response}"],
                },
                "path_mapping": {
                    "best_match": {"var": "${oper_pedidos}", "path": "/pedidos", "confidence": 0.5},
                    "alternatives": [],
                },
                "status_code_expected": "200",
            }
        ],
    }


# --- Tests: calculate_checksum ---

class TestCalculateChecksum:
    """Testes para a funcao calculate_checksum."""

    def test_deve_retornar_string_hexadecimal(self, sample_manifest_data):
        """Deve retornar um hash hexadecimal valido."""
        result = calculate_checksum(sample_manifest_data)

        assert isinstance(result, str)
        assert len(result) > 0
        # Hash SHA-256 em hex tem 64 caracteres
        assert all(c in "0123456789abcdef" for c in result)

    def test_deve_ser_deterministico(self, sample_manifest_data):
        """Deve gerar o mesmo hash para os mesmos dados."""
        hash1 = calculate_checksum(sample_manifest_data)
        hash2 = calculate_checksum(sample_manifest_data)

        assert hash1 == hash2

    def test_deve_diferir_para_dados_diferentes(self, sample_manifest_data):
        """Deve gerar hashes diferentes para dados diferentes."""
        dados_modificados = dict(sample_manifest_data)
        dados_modificados["collection_name"] = "API Diferente v2.0"

        hash1 = calculate_checksum(sample_manifest_data)
        hash2 = calculate_checksum(dados_modificados)

        assert hash1 != hash2

    def test_deve_ignorar_checksum_existente_no_calculo(self, sample_manifest_data):
        """Deve ignorar o campo 'checksum' ao calcular o hash (evita recursao)."""
        dados_com_checksum = dict(sample_manifest_data)
        dados_com_checksum["checksum"] = "hash_anterior"

        dados_sem_checksum = dict(sample_manifest_data)

        hash1 = calculate_checksum(dados_com_checksum)
        hash2 = calculate_checksum(dados_sem_checksum)

        assert hash1 == hash2

    def test_deve_diferir_para_test_cases_diferentes(self, sample_manifest_data):
        """Deve gerar hashes diferentes se test_cases muda."""
        dados_modificados = json.loads(json.dumps(sample_manifest_data))
        dados_modificados["test_cases"].append({"seq": "T02", "name": "novo"})

        hash1 = calculate_checksum(sample_manifest_data)
        hash2 = calculate_checksum(dados_modificados)

        assert hash1 != hash2


# --- Tests: verify_checksum ---

class TestVerifyChecksum:
    """Testes para a funcao verify_checksum."""

    def test_deve_retornar_true_se_checksum_coincide(self, sample_manifest_data):
        """Deve retornar True se o checksum no manifest coincide com o calculado."""
        manifest_com_checksum = add_checksum_to_manifest(sample_manifest_data)

        result = verify_checksum(manifest_com_checksum)

        assert result is True

    def test_deve_retornar_false_se_checksum_diverge(self, sample_manifest_data):
        """Deve retornar False se o checksum no manifest nao coincide."""
        manifest_modificado = dict(sample_manifest_data)
        manifest_modificado["checksum"] = "hash_completamente_errado"

        result = verify_checksum(manifest_modificado)

        assert result is False

    def test_deve_retornar_false_se_sem_checksum(self, sample_manifest_data):
        """Deve retornar False se o manifest nao tem campo checksum."""
        result = verify_checksum(sample_manifest_data)

        assert result is False


# --- Tests: add_checksum_to_manifest ---

class TestAddChecksumToManifest:
    """Testes para a funcao add_checksum_to_manifest."""

    def test_deve_adicionar_campo_checksum(self, sample_manifest_data):
        """Deve adicionar o campo 'checksum' no manifest."""
        result = add_checksum_to_manifest(sample_manifest_data)

        assert "checksum" in result
        assert isinstance(result["checksum"], str)
        assert len(result["checksum"]) > 0

    def test_deve_nao_alterar_dados_originais_exceto_checksum(self, sample_manifest_data):
        """Deve preservar todos os dados originais exceto o checksum."""
        result = add_checksum_to_manifest(sample_manifest_data)

        assert result["file_name"] == sample_manifest_data["file_name"]
        assert result["tipo"] == sample_manifest_data["tipo"]
        assert result["collection_name"] == sample_manifest_data["collection_name"]
        assert result["test_cases"] == sample_manifest_data["test_cases"]

    def test_deve_gerar_checksum_verificavel(self, sample_manifest_data):
        """Deve gerar um checksum que passa na verificacao."""
        manifest_com_checksum = add_checksum_to_manifest(sample_manifest_data)

        assert verify_checksum(manifest_com_checksum) is True


# --- Tests: has_manifest_changed ---

class TestHasManifestChanged:
    """Testes para a funcao has_manifest_changed."""

    def test_deve_retornar_true_se_arquivo_nao_existe(self, tmp_path):
        """Deve retornar True se o arquivo manifest nao existe (primeira geracao)."""
        manifest_inexistente = str(tmp_path / "nao_existe.manifest.json")

        result = has_manifest_changed(sample_manifest_data := {
            "file_name": "test.robot",
            "tipo": "sucesso",
            "collection_name": "Test",
            "test_cases": [],
        }, manifest_inexistente)

        assert result is True

    def test_deve_retornar_true_se_dados_mudaram(self, sample_manifest_data, tmp_path):
        """Deve retornar True se os dados do manifest mudaram."""
        # Salva manifest original com checksum
        manifest_com_checksum = add_checksum_to_manifest(sample_manifest_data)
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(json.dumps(manifest_com_checksum), encoding="utf-8")

        # Modifica os dados
        dados_modificados = dict(sample_manifest_data)
        dados_modificados["collection_name"] = "API Modificada v2.0"

        result = has_manifest_changed(dados_modificados, str(manifest_path))

        assert result is True

    def test_deve_retornar_false_se_dados_nao_mudaram(self, sample_manifest_data, tmp_path):
        """Deve retornar False se os dados do manifest nao mudaram."""
        # Salva manifest original com checksum
        manifest_com_checksum = add_checksum_to_manifest(sample_manifest_data)
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(json.dumps(manifest_com_checksum), encoding="utf-8")

        # Mesmos dados (sem checksum no dict — o checksum no arquivo deve ser ignorado na comparacao)
        result = has_manifest_changed(sample_manifest_data, str(manifest_path))

        assert result is False