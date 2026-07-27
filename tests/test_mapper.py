"""
Testes do modulo mapper.

Este modulo valida o matching fuzzy entre:
- O slug da API (gerado a partir do nome da collection) e as listas @{api_*} do base-api.robot
- O path da URL das requests e as variaveis ${oper_*} do base-api.robot

Em Java, este arquivo equivaleria a:
    class MapperTest {
        @Test void deveParsearListasApiDoBaseApi() { ... }
        @Test void deveEncontrarMatchExato() { ... }
        @Test void deveEncontrarMatchParcial() { ... }
    }
"""

import os
import pytest
from service.mapper import (
    parse_base_api,
    match_api_slug,
    match_path,
    normalize,
    token_overlap,
)


# --- Fixtures ---

@pytest.fixture
def base_api_content():
    """Conteudo simulado do base-api.robot para testes sem depender do arquivo real."""
    return (
        "*** Variables ***\n"
        "${oper_token}       /token\n"
        "${oper_pedidos}     /pedidos\n"
        "${oper_orcamentos}  /orcamentos\n"
        "${oper_health}      /health\n"
        "\n"
        "###                        |api                            |version dev|version hml|\n"
        "@{api_conecta_pedidos}      conecta-pedidos                 v1.4          v1.4\n"
        "@{api_pedidos_proxy}        gestao-pedidos-laboratorio                v1.107        v1.104\n"
        "@{api_produtos_proxy}       gestao-produtos-laboratorio               v1.31         v1.30\n"
        "                                                                       \n"
        "@{api_auth_jwt}             autenticacao-jwt                v1.58         v1.58\n"
    )


@pytest.fixture
def base_api_file(tmp_path, base_api_content):
    """Cria um arquivo base-api.robot temporario para testes."""
    file_path = tmp_path / "base-api.robot"
    file_path.write_text(base_api_content, encoding="utf-8")
    return str(file_path)


# --- Tests: normalize ---

class TestNormalize:
    """Testes para a funcao normalize (normaliza texto para matching)."""

    def test_deve_remover_acentos(self):
        """Deve remover acentos de caracteres."""
        assert normalize("gestão-pedidos") == "gestao-pedidos"

    def test_deve_converter_para_minusculas(self):
        """Deve converter para minusculas."""
        assert normalize("API-Conecta-Pedidos") == "api-conecta-pedidos"

    def test_deve_substituir_underscores_por_hifens(self):
        """Deve substituir underscores por hifens para uniformizar."""
        assert normalize("api_conecta_pedidos") == "api-conecta-pedidos"

    def test_deve_remover_espacos_extras(self):
        """Deve remover espacos no inicio e fim."""
        assert normalize("  conecta-pedidos  ") == "conecta-pedidos"


# --- Tests: token_overlap ---

class TestTokenOverlap:
    """Testes para a funcao token_overlap (calcula similaridade por tokens)."""

    def test_deve_retornar_1_para_strings_identicas(self):
        """Deve retornar 1.0 quando as strings sao identicas."""
        assert token_overlap("conecta-pedidos", "conecta-pedidos") == 1.0

    def test_deve_retornar_zero_para_sem_overlap(self):
        """Deve retornar 0.0 quando nao ha tokens em comum."""
        assert token_overlap("abc", "xyz") == 0.0

    def test_deve_calcular_overlap_parcial(self):
        """Deve calcular o ratio de tokens em comum."""
        # "conecta pedidos" tem 2 tokens, "pedidos" tem 1
        # overlap = 1 token em comum / max(2, 1) = 0.5
        result = token_overlap("conecta-pedidos", "pedidos")
        assert 0.0 < result <= 1.0

    def test_deve_normalizar_strings_antes_de_comparar(self):
        """Deve normalizar strings antes de comparar."""
        result = token_overlap("Gestão-Pedidos", "gestao_pedidos")
        assert result == 1.0


# --- Tests: parse_base_api ---

class TestParseBaseApi:
    """Testes para a funcao parse_base_api (extrai listas e variaveis do base-api.robot)."""

    def test_deve_extrair_listas_api(self, base_api_file):
        """Deve extrair todas as listas @{api_*} do arquivo."""
        result = parse_base_api(base_api_file)

        assert "api_arrays" in result
        assert len(result["api_arrays"]) == 4

        api_names = [a["name"] for a in result["api_arrays"]]
        assert "api_conecta_pedidos" in api_names
        assert "api_pedidos_proxy" in api_names
        assert "api_produtos_proxy" in api_names
        assert "api_auth_jwt" in api_names

    def test_deve_extrair_slug_da_lista_api(self, base_api_file):
        """Deve extrair o slug (segunda coluna) de cada lista @{api_*}."""
        result = parse_base_api(base_api_file)

        conecta = [a for a in result["api_arrays"] if a["name"] == "api_conecta_pedidos"][0]
        assert conecta["slug"] == "conecta-pedidos"

    def test_deve_extrair_versao_dev_da_lista_api(self, base_api_file):
        """Deve extrair a versao dev (terceira coluna) de cada lista @{api_*}."""
        result = parse_base_api(base_api_file)

        conecta = [a for a in result["api_arrays"] if a["name"] == "api_conecta_pedidos"][0]
        assert conecta["version_dev"] == "v1.4"

    def test_deve_extrair_versao_hml_da_lista_api(self, base_api_file):
        """Deve extrair a versao hml (quarta coluna) de cada lista @{api_*}."""
        result = parse_base_api(base_api_file)

        conecta = [a for a in result["api_arrays"] if a["name"] == "api_conecta_pedidos"][0]
        assert conecta["version_hml"] == "v1.4"

    def test_deve_extrair_variaveis_oper(self, base_api_file):
        """Deve extrair todas as variaveis ${oper_*} do arquivo."""
        result = parse_base_api(base_api_file)

        assert "oper_vars" in result
        assert len(result["oper_vars"]) == 4

        oper_names = [o["name"] for o in result["oper_vars"]]
        assert "oper_token" in oper_names
        assert "oper_pedidos" in oper_names
        assert "oper_orcamentos" in oper_names
        assert "oper_health" in oper_names

    def test_deve_extrair_path_da_variavel_oper(self, base_api_file):
        """Deve extrair o path de cada variavel ${oper_*}."""
        result = parse_base_api(base_api_file)

        pedidos = [o for o in result["oper_vars"] if o["name"] == "oper_pedidos"][0]
        assert pedidos["path"] == "/pedidos"

    def test_deve_ignorar_linhas_vazias_e_comentarios(self, base_api_file):
        """Deve ignorar linhas vazias, comentarios e linhas de cabecalho."""
        result = parse_base_api(base_api_file)

        # Nao deve incluir linhas de cabecalho como ###...
        api_names = [a["name"] for a in result["api_arrays"]]
        assert all(not a.startswith("#") for a in api_names)

    def test_deve_lancar_erro_se_arquivo_nao_existe(self):
        """Deve lancar FileNotFoundError se o arquivo nao existe."""
        with pytest.raises(FileNotFoundError):
            parse_base_api("/caminho/inexistente/base-api.robot")


# --- Tests: match_api_slug ---

class TestMatchApiSlug:
    """Testes para a funcao match_api_slug (fuzzy matching do slug contra listas @{api_*})."""

    def test_deve_retornar_match_exato(self, base_api_file):
        """Deve retornar best_match com confidence 1.0 quando slug e identico."""
        api_data = parse_base_api(base_api_file)
        result = match_api_slug("conecta-pedidos", api_data["api_arrays"])

        assert result["best_match"]["array"] == "@{api_conecta_pedidos}"
        assert result["best_match"]["confidence"] == 1.0

    def test_deve_retornar_match_parcial_por_substring(self, base_api_file):
        """Deve retornar match por substring (slug contem o slug da lista ou vice-versa)."""
        api_data = parse_base_api(base_api_file)
        # "pedidos" e substring de "conecta-pedidos"
        result = match_api_slug("pedidos", api_data["api_arrays"])

        assert result["best_match"] is not None
        assert result["best_match"]["confidence"] > 0.0

    def test_deve_retornar_alternativas_ordenadas_por_confianca(self, base_api_file):
        """Deve retornar alternativas ordenadas por confidence decrescente."""
        api_data = parse_base_api(base_api_file)
        result = match_api_slug("pedidos-proxy", api_data["api_arrays"])

        if len(result["alternatives"]) > 1:
            confidences = [a["confidence"] for a in result["alternatives"]]
            assert confidences == sorted(confidences, reverse=True)

    def test_deve_retornar_none_se_nenhuma_correspondencia(self, base_api_file):
        """Deve retornar best_match None se nao ha correspondencia."""
        api_data = parse_base_api(base_api_file)
        result = match_api_slug("api-completamente-diferente", api_data["api_arrays"])

        assert result["best_match"] is None
        assert result["alternatives"] == []

    def test_deve_incluir_slug_e_array_no_resultado(self, base_api_file):
        """Deve incluir o slug e o nome do array no resultado do best_match."""
        api_data = parse_base_api(base_api_file)
        result = match_api_slug("conecta-pedidos", api_data["api_arrays"])

        assert "array" in result["best_match"]
        assert "slug" in result["best_match"]
        assert "confidence" in result["best_match"]
        assert result["best_match"]["slug"] == "conecta-pedidos"


# --- Tests: match_path ---

class TestMatchPath:
    """Testes para a funcao match_path (fuzzy matching do path da URL contra ${oper_*})."""

    def test_deve_retornar_match_exato(self, base_api_file):
        """Deve retornar match exato quando o path e identico ao ${oper_*}."""
        api_data = parse_base_api(base_api_file)
        result = match_path("https://api.example.com/dev/conecta-pedidos/v1/pedidos", api_data["oper_vars"])

        assert result["best_match"]["var"] == "${oper_pedidos}"
        assert result["best_match"]["confidence"] > 0.0

    def test_deve_retornar_match_por_substring_do_path(self, base_api_file):
        """Deve retornar match quando o path da URL contem o path do ${oper_*}."""
        api_data = parse_base_api(base_api_file)
        result = match_path("https://api.example.com/orcamentos/123", api_data["oper_vars"])

        assert result["best_match"]["var"] == "${oper_orcamentos}"

    def test_deve_retornar_none_se_nenhuma_correspondencia(self, base_api_file):
        """Deve retornar best_match None se nao ha correspondencia."""
        api_data = parse_base_api(base_api_file)
        result = match_path("https://api.example.com/rota-desconhecida", api_data["oper_vars"])

        assert result["best_match"] is None
        assert result["alternatives"] == []

    def test_deve_extrair_apenas_o_path_da_url_completa(self, base_api_file):
        """Deve extrair apenas o path da URL, ignorando protocolo e dominio."""
        api_data = parse_base_api(base_api_file)
        result = match_path("https://api.example.com/dev/api/v1/pedidos?pagina=1", api_data["oper_vars"])

        # Deve encontrar /pedidos na URL
        assert result["best_match"]["var"] == "${oper_pedidos}"

    def test_deve_incluir_path_extraido_no_resultado(self, base_api_file):
        """Deve incluir o path extraido da URL no resultado."""
        api_data = parse_base_api(base_api_file)
        result = match_path("https://api.example.com/pedidos", api_data["oper_vars"])

        assert "path" in result["best_match"]
        assert "/pedidos" in result["best_match"]["path"]


# --- Tests: integracao com base-api.robot real ---

class TestIntegracaoBaseApiReal:
    """Testes de integracao usando o base-api.robot real do projeto."""

    @pytest.fixture
    def real_base_api_path(self):
        """Caminho fixo para o base-api.robot real."""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".opencode", "context", "resource", "base-api.robot"
        )

    def test_deve_parsear_base_api_real(self, real_base_api_path):
        """Deve parsear o base-api.robot real sem erros."""
        result = parse_base_api(real_base_api_path)

        assert len(result["api_arrays"]) > 0
        assert len(result["oper_vars"]) > 0

    def test_deve_encontrar_conecta_pedidos_no_real(self, real_base_api_path):
        """Deve encontrar api_conecta_pedidos no base-api.robot real."""
        result = parse_base_api(real_base_api_path)

        api_names = [a["name"] for a in result["api_arrays"]]
        assert "api_conecta_pedidos" in api_names

    def test_deve_fazer_match_conecta_pedidos_no_real(self, real_base_api_path):
        """Deve fazer match do slug 'conecta-pedidos' contra o base-api.robot real."""
        api_data = parse_base_api(real_base_api_path)
        result = match_api_slug("conecta-pedidos", api_data["api_arrays"])

        assert result["best_match"]["array"] == "@{api_conecta_pedidos}"

    def test_deve_fazer_match_oper_pedidos_no_real(self, real_base_api_path):
        """Deve fazer match do path /pedidos contra o base-api.robot real."""
        api_data = parse_base_api(real_base_api_path)
        result = match_path("https://api.example.com/conecta-pedidos/v1/pedidos", api_data["oper_vars"])

        assert result["best_match"]["var"] == "${oper_pedidos}"