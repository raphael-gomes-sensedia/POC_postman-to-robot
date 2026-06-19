"""Gerador de arquivos .robot a partir de dados parseados.

Responsável por:
- Agrupar requests por pasta de primeiro nivel
- Gerar secao Settings com Resource para base-api.robot
- Gerar secao Variables com variaveis resolvidas
- Gerar secao Test Cases com um caso por request
- Gerar 1 arquivo .robot por grupo de primeiro nivel
"""

import os
import re


def get_top_level_group(group_path):
    """Extrai o grupo de primeiro nivel do caminho completo.

    Ex: "[F001] GET /pedidos / Sucesso [200,206] / [200] GET ..."
    Retorna: "[F001] GET /pedidos"
    """
    parts = group_path.split(" / ")
    if parts and parts[0]:
        return parts[0]
    return "Sem grupo"


def group_requests_by_top_level(requests):
    """Agrupa requests pelo grupo de primeiro nivel.

    Retorna um dicionario: {grupo_top: [requests]}
    """
    groups = {}
    for req in requests:
        top_group = get_top_level_group(req["group"])
        if top_group not in groups:
            groups[top_group] = []
        groups[top_group].append(req)
    return groups


def generate_file_name(group_name):
    """Gera o nome do arquivo .robot a partir do nome do grupo.

    Ex: "[F001] GET /pedidos" -> "f001_get_pedidos.robot"
    """
    import unicodedata
    # Normaliza e remove acentos
    name = unicodedata.normalize("NFKD", group_name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    # Remove colchetes
    name = name.replace("[", "").replace("]", "")
    # Substitui caracteres nao alfanumericos por underscore
    name = "".join(c if c.isalnum() or c == " " else "_" for c in name)
    # Converte para lowercase e substitui espacos por underscore
    name = name.lower().replace(" ", "_")
    # Remove underscores extras
    while "__" in name:
        name = name.replace("__", "_")
    name = name.strip("_")
    return f"{name}.robot"


def get_env_from_requests(requests):
    """Extrai o ambiente dos requests (dev ou hml)."""
    for req in requests:
        url = req.get("url", "")
        if "/hml/" in url:
            return "hml"
    return "dev"


def generate_documentation(requests, collection_name):
    """Gera a secao Documentation multi-linha.

    Inclui nome da API, operacoes e comando de execucao.
    """
    lines = []
    lines.append(f"Documentation    {collection_name}")

    seen = set()
    for req in requests:
        test_name = req["name"]
        if test_name not in seen:
            seen.add(test_name)
            lines.append(f"...              {test_name}")

    file_name = generate_file_name(get_top_level_group(requests[0]["group"]))
    env = get_env_from_requests(requests)
    lines.append(f"...        command to run tests:")
    lines.append(f"...        robot -d results\\unit_test_{env}\\{file_name} {file_name}")

    return "\n".join(lines)


def generate_settings(requests, collection_name, base_resource):
    """Gera a secao *** Settings *** do arquivo .robot."""
    lines = []
    lines.append("*** Settings ***")
    lines.append(generate_documentation(requests, collection_name))
    lines.append("")
    lines.append(f"Resource        {base_resource}")
    lines.append("")
    return "\n".join(lines)


def generate_variables(variables):
    """Gera a secao *** Variables *** com variaveis da collection."""
    lines = []
    lines.append("*** Variables ***")

    for key, value in variables.items():
        if value:
            lines.append(f"${{{key}}}    {value}")

    lines.append("")
    return "\n".join(lines)


def extract_status_code(name):
    """Extrai o status code do nome do teste.

    Ex: "[200] GET /pedidos" -> "200"
    Ex: "[400] GET /pedidos Erro" -> "400"
    """
    match = re.search(r"\[(\d{3})\]", name)
    if match:
        return match.group(1)
    return None


def generate_create_session(request):
    """Gera a keyword Create Session baseada no metodo e auth."""
    auth = request.get("auth")

    if auth and auth == "basic":
        return "    Create Session API Oauth"

    return "    Create Session API Proxy"


def generate_http_call(request):
    """Gera a chamada HTTP baseada no metodo."""
    method = request["method"].upper()
    url = request["url"]

    method_map = {
        "GET": "GET On Session",
        "POST": "POST On Session",
        "PUT": "PUT On Session",
        "DELETE": "DELETE On Session",
        "PATCH": "PATCH On Session",
    }

    keyword = method_map.get(method, "GET On Session")
    line = "    ${api_response}=    " + keyword + "    api-in-test    " + url + "    expected_status=any"

    if request.get("body"):
        body = request["body"]
        if isinstance(body, str):
            line += "    json=${body}    "
        else:
            line += "    data="

    return line


def generate_save_response():
    """Gera a keyword para salvar a resposta em variavel."""
    return ""


def generate_status_validation(status_code):
    """Gera a validacao de status code."""
    return "    Status Should Be    " + status_code + "    ${api_response}"


def generate_assertions_from_events(events):
    """Gera assertions a partir dos eventos (test scripts) do Postman.

    Usa o modulo assertions para traduzir as assertions do Postman JS
    para Robot Framework.
    """
    from service.assertions import parse_assertions
    return parse_assertions(events)


def generate_test_case(request):
    """Gera um Test Case Robot a partir de um request parseado."""
    lines = []

    name = request["name"]
    method = request["method"]

    if request["disabled"]:
        lines.append(f"{name}    Skip    Request desabilitado na collection Postman")
        lines.append("")
        return "\n".join(lines)

    test_name = f"{method} {name}"
    lines.append(test_name)

    lines.append(generate_create_session(request))
    lines.append(generate_http_call(request))
    lines.append(generate_save_response())

    status_code = extract_status_code(name)
    if status_code:
        lines.append(generate_status_validation(status_code))

    lines.extend(generate_assertions_from_events(request["events"]))

    lines.append("")
    return "\n".join(lines)


def generate_keywords_section():
    """Gera a secao *** Keywords *** (vazia por enquanto)."""
    return "*** Keywords ***"


def generate_robot_file(requests, collection_name, variables, base_resource):
    """Gera o conteudo completo de um arquivo .robot.

    Retorna a string com todo o conteudo do arquivo.
    """
    sections = []

    sections.append(generate_settings(requests, collection_name, base_resource))
    sections.append(generate_variables(variables))
    sections.append("*** Test Cases ***")

    for req in requests:
        sections.append(generate_test_case(req))

    sections.append(generate_keywords_section())

    return "\n".join(sections) + "\n"


def generate_robot(data, output_dir, base_resource, environment):
    """Gera os arquivos .robot a partir dos dados parseados.

    Cria um arquivo .robot por grupo de primeiro nivel.

    Args:
        data: dicionario retornado por parse_collection com:
              - collection_name: nome da collection
              - variables: dicionario de variaveis
              - requests: lista de requests parseados
        output_dir: diretorio de saida
        base_resource: caminho para o base-api.robot
        environment: ambiente (dev, hml)

    Returns:
        Lista de caminhos dos arquivos gerados.
    """
    os.makedirs(output_dir, exist_ok=True)

    collection_name = data.get("collection_name", "Sem nome")
    variables = data.get("variables", {})
    requests = data.get("requests", [])

    groups = group_requests_by_top_level(requests)

    files_created = []
    for group_name, group_requests in groups.items():
        file_name = generate_file_name(group_name)
        file_path = os.path.join(output_dir, file_name)

        content = generate_robot_file(
            group_requests,
            collection_name,
            variables,
            base_resource,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        files_created.append(file_path)
        print(f"Gerado: {file_path} ({len(group_requests)} testes)")

    return files_created
