"""
Testes do modulo validator_service.

Validam as funcoes de validacao pos-geracao que verificam:
- Sintaxe Robot (secoes *** ***, indentacao, keywords)
- Mapeamentos @{api_*} e ${oper_*} contra o base-api.robot
- Arquivos JSON (schemas e payloads) sao validos
- Completude: cada test case tem keyword associada
- Divergencia: numero de test cases no .robot vs manifest

Em Java, este arquivo equivaleria a:
    class ValidatorServiceTest {
        @Test void deveValidarSintaxeRobotValido() { ... }
        @Test void deveDetectarSintaxeRobotInvalido() { ... }
        @Test void deveValidarMapeamentosExistentes() { ... }
        @Test void deveDetectarMapeamentoInexistente() { ... }
        @Test void deveValidarJsonsValidos() { ... }
        @Test void deveDetectarJsonInvalido() { ... }
        @Test void deveValidarCompletude() { ... }
        @Test void deveDetectarTestCaseSemKeyword() { ... }
    }
"""

import json
import os
import pytest
from service.validator_service import (
    validate_robot_syntax,
    validate_mappings,
    validate_json_files,
    validate_completeness,
    validate_all,
)
from service.manifest import generate_manifest_file
from service.generator import generate_api_slug, generate_file_name


# --- Fixtures ---

@pytest.fixture
def base_api_path():
    """Caminho fixo para o base-api.robot real do projeto."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".opencode", "context", "resource", "base-api.robot"
    )


@pytest.fixture
def valid_robot_content():
    """Conteudo de um arquivo .robot valido com secoes e keywords."""
    return (
        "*** Settings ***\n"
        "Documentation    Test API - sucesso\n"
        "Resource        ../api-tests/base-api.robot\n\n"
        "*** Variables ***\n\n"
        "*** Test Cases ***\n"
        "T01 - Test API - [200] GET /pedidos\n"
        "    Keyword De Teste\n\n"
        "*** Keywords ***\n"
        "Keyword De Teste\n"
        "    Log    teste\n"
    )


@pytest.fixture
def invalid_robot_content():
    """Conteudo de um arquivo .robot invalido (sem secao Test Cases)."""
    return (
        "*** Settings ***\n"
        "Documentation    Teste\n\n"
        "*** Variables ***\n"
    )


@pytest.fixture
def robot_with_test_case_no_keyword():
    """Conteudo .robot com test case sem keyword associada."""
    return (
        "*** Settings ***\n"
        "Documentation    Teste\n\n"
        "*** Variables ***\n\n"
        "*** Test Cases ***\n"
        "T01 - Teste Sem Keyword\n"
        "    # Apenas comentario, sem keyword\n\n"
        "*** Keywords ***\n"
    )


@pytest.fixture
def sample_manifest_data():
    """Dados para gerar um manifest de teste."""
    return {
        "requests": [
            {
                "group": "[F001] GET /pedidos / Sucesso",
                "name": "[200] GET /pedidos Sucesso",
                "method": "GET",
                "url": "https://api.example.com/pedidos",
                "headers": {},
                "body": None,
                "auth": None,
                "events": [],
            },
            {
                "group": "[F001] GET /pedidos / Sucesso",
                "name": "[201] POST /pedidos Criar",
                "method": "POST",
                "url": "https://api.example.com/pedidos",
                "headers": {},
                "body": None,
                "auth": None,
                "events": [],
            },
        ],
        "collection_name": "API Conecta Pedidos v1.4",
        "variables": {},
        "tipo": "sucesso",
        "file_name": "f001_get_pedidos.robot",
        "api_slug": "conecta-pedidos",
    }


# --- Tests: validate_robot_syntax ---

class TestValidateRobotSyntax:
    """Testes para a validacao de sintaxe Robot via regex fallback."""

    def test_deve_passar_arquivo_robot_valido(self, valid_robot_content, tmp_path):
        """Deve passar (sem erros) para arquivo .robot com secoes validas."""
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(valid_robot_content, encoding="utf-8")

        result = validate_robot_syntax(str(robot_file))

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_deve_falhar_sem_secao_test_cases(self, invalid_robot_content, tmp_path):
        """Deve falhar se nao ha secao *** Test Cases ***."""
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(invalid_robot_content, encoding="utf-8")

        result = validate_robot_syntax(str(robot_file))

        assert result["valid"] is False
        assert any("Test Cases" in e for e in result["errors"])

    def test_deve_falhar_sem_secao_keywords(self, tmp_path):
        """Deve falhar se nao ha secao *** Keywords ***."""
        content = (
            "*** Settings ***\n"
            "Documentation    Teste\n\n"
            "*** Test Cases ***\n"
            "T01 - Teste\n"
            "    Keyword\n"
        )
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(content, encoding="utf-8")

        result = validate_robot_syntax(str(robot_file))

        assert result["valid"] is False
        assert any("Keywords" in e for e in result["errors"])

    def test_deve_falhar_se_arquivo_nao_existe(self):
        """Deve falhar se o arquivo nao existe."""
        result = validate_robot_syntax("/caminho/inexistente.robot")

        assert result["valid"] is False
        assert len(result["errors"]) > 0


# --- Tests: validate_mappings ---

class TestValidateMappings:
    """Testes para a validacao de mapeamentos @{api_*} e ${oper_*}."""

    def test_deve_passar_com_mapeamentos_validos(self, base_api_path, tmp_path):
        """Deve passar se @{api_*} e ${oper_*} referenciados existem no base-api.robot."""
        content = (
            "*** Test Cases ***\n"
            "T01 - Teste\n"
            "    @{api_conecta_pedidos}\n"
            "    ${oper_pedidos}\n"
        )
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(content, encoding="utf-8")

        result = validate_mappings(str(robot_file), base_api_path)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_deve_falhar_com_api_inexistente(self, base_api_path, tmp_path):
        """Deve falhar se @{api_*} referenciada nao existe no base-api.robot."""
        content = (
            "*** Test Cases ***\n"
            "T01 - Teste\n"
            "    @{api_inexistente_xyz}\n"
        )
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(content, encoding="utf-8")

        result = validate_mappings(str(robot_file), base_api_path)

        assert result["valid"] is False
        assert any("api_inexistente_xyz" in e for e in result["errors"])

    def test_deve_falhar_com_oper_inexistente(self, base_api_path, tmp_path):
        """Deve falhar se ${oper_*} referenciado nao existe no base-api.robot."""
        content = (
            "*** Test Cases ***\n"
            "T01 - Teste\n"
            "    ${oper_inexistente_xyz}\n"
        )
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(content, encoding="utf-8")

        result = validate_mappings(str(robot_file), base_api_path)

        assert result["valid"] is False
        assert any("oper_inexistente_xyz" in e for e in result["errors"])

    def test_deve_passar_se_sem_mapeamentos(self, base_api_path, tmp_path):
        """Deve passar se o arquivo nao referencia nenhum @{api_*} ou ${oper_*}."""
        content = "*** Test Cases ***\nT01 - Teste\n    Log    teste\n"
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(content, encoding="utf-8")

        result = validate_mappings(str(robot_file), base_api_path)

        assert result["valid"] is True


# --- Tests: validate_json_files ---

class TestValidateJsonFiles:
    """Testes para a validacao de arquivos JSON (schemas e payloads)."""

    def test_deve_passar_com_jsons_validos(self, tmp_path):
        """Deve passar se todos os arquivos JSON no diretorio sao validos."""
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()
        (schemas_dir / "schema1.json").write_text('{"type": "object"}', encoding="utf-8")

        resources_dir = tmp_path / "resources"
        resources_dir.mkdir()
        (resources_dir / "payload1.json").write_text('{"nome": "teste"}', encoding="utf-8")

        result = validate_json_files(str(tmp_path))

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_deve_falhar_com_json_invalido(self, tmp_path):
        """Deve falhar se algum arquivo JSON e invalido."""
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()
        (schemas_dir / "bad.json").write_text("{invalid json}", encoding="utf-8")

        result = validate_json_files(str(tmp_path))

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_deve_passar_se_sem_diretorios(self, tmp_path):
        """Deve passar se nao existem diretorios schemas/ ou resources/."""
        result = validate_json_files(str(tmp_path))

        assert result["valid"] is True


# --- Tests: validate_completeness ---

class TestValidateCompleteness:
    """Testes para a validacao de completude (test cases vs manifest)."""

    def test_deve_passar_se_test_cases_tem_keywords(self, valid_robot_content, sample_manifest_data, base_api_path, tmp_path):
        """Deve passar se todos os test cases tem keyword associada."""
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(valid_robot_content, encoding="utf-8")

        manifest_path = generate_manifest_file(
            requests=sample_manifest_data["requests"],
            collection_name=sample_manifest_data["collection_name"],
            variables=sample_manifest_data["variables"],
            tipo=sample_manifest_data["tipo"],
            file_name=sample_manifest_data["file_name"],
            api_slug=sample_manifest_data["api_slug"],
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        result = validate_completeness(str(robot_file), manifest_path)

        # O robot tem 1 test case com keyword, o manifest tem 2.
        # Pode haver divergencia de contagem (warning), mas completude deve passar
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_deve_falhar_se_test_case_sem_keyword(self, robot_with_test_case_no_keyword, sample_manifest_data, base_api_path, tmp_path):
        """Deve falhar se algum test case nao tem keyword."""
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(robot_with_test_case_no_keyword, encoding="utf-8")

        manifest_path = generate_manifest_file(
            requests=sample_manifest_data["requests"],
            collection_name=sample_manifest_data["collection_name"],
            variables=sample_manifest_data["variables"],
            tipo=sample_manifest_data["tipo"],
            file_name=sample_manifest_data["file_name"],
            api_slug=sample_manifest_data["api_slug"],
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        result = validate_completeness(str(robot_file), manifest_path)

        assert len(result["errors"]) > 0
        assert any("sem keyword" in e.lower() for e in result["errors"])

    def test_deve_detectar_divergencia_de_contagem(self, sample_manifest_data, base_api_path, tmp_path):
        """Deve alertar se o numero de test cases no .robot difere do manifest."""
        # Robot com 1 test case, manifest com 2
        content = (
            "*** Settings ***\n\n"
            "*** Test Cases ***\n"
            "T01 - Teste\n"
            "    Keyword\n\n"
            "*** Keywords ***\n"
        )
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(content, encoding="utf-8")

        manifest_path = generate_manifest_file(
            requests=sample_manifest_data["requests"],
            collection_name=sample_manifest_data["collection_name"],
            variables=sample_manifest_data["variables"],
            tipo=sample_manifest_data["tipo"],
            file_name=sample_manifest_data["file_name"],
            api_slug=sample_manifest_data["api_slug"],
            base_api_path=base_api_path,
            output_dir=str(tmp_path),
        )

        result = validate_completeness(str(robot_file), manifest_path)

        # Deve haver warning de divergencia
        assert len(result["warnings"]) > 0
        assert any("diverg" in w.lower() for w in result["warnings"])


# --- Tests: validate_all ---

class TestValidateAll:
    """Testes para a funcao validate_all (orquestra todas as validacoes)."""

    def test_deve_retornar_estrutura_completa(self, base_api_path, tmp_path):
        """Deve retornar um relatorio com errors, warnings e passed."""
        # Criar estrutura minima
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(
            "*** Settings ***\n"
            "Resource    ../base-api.robot\n\n"
            "*** Test Cases ***\n"
            "T01 - Teste\n"
            "    Log    teste\n\n"
            "*** Keywords ***\n",
            encoding="utf-8"
        )

        result = validate_all(str(tmp_path), base_api_path)

        assert "errors" in result
        assert "warnings" in result
        assert "passed" in result
        assert "summary" in result

    def test_deve_validar_multiplos_arquivos_robot(self, base_api_path, tmp_path):
        """Deve validar todos os arquivos .robot no diretorio de saida."""
        # Criar dois arquivos .robot
        for i in range(2):
            robot_file = tmp_path / f"test{i}.robot"
            robot_file.write_text(
                "*** Settings ***\n\n"
                "*** Test Cases ***\n"
                f"T01 - Teste{i}\n"
                "    Log    teste\n\n"
                "*** Keywords ***\n",
                encoding="utf-8"
            )

        result = validate_all(str(tmp_path), base_api_path)

        assert "errors" in result
        assert "summary" in result

    def test_deve_incluir_estatisticas_no_summary(self, base_api_path, tmp_path):
        """Deve incluir contadores no summary (total, errors, warnings)."""
        robot_file = tmp_path / "test.robot"
        robot_file.write_text(
            "*** Settings ***\n\n"
            "*** Test Cases ***\n"
            "T01 - Teste\n"
            "    Log    teste\n\n"
            "*** Keywords ***\n",
            encoding="utf-8"
        )

        result = validate_all(str(tmp_path), base_api_path)

        assert "total_files" in result["summary"]
        assert "total_errors" in result["summary"]
        assert "total_warnings" in result["summary"]