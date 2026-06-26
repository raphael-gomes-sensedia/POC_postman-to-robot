"""Gerador de arquivos .robot a partir de dados parseados.

Responsavel por:
- Gerar keywords reutilizaveis por grupo (com auth + session + HTTP)
- Gerar test cases enxutos
- Separar arquivos de sucesso e erro
- Extrair catalogo de variaveis do base-api.robot para nao duplicar
- Injetar Suite Setup comentado
"""

import os
import re
import unicodedata


def get_top_level_group(group_path):
    """Extrai o grupo de primeiro nivel do caminho completo."""
    parts = group_path.split(" / ")
    if parts and parts[0]:
        return parts[0]
    return "Sem grupo"


def group_requests_by_top_level(requests):
    """Agrupa requests pelo grupo de primeiro nivel."""
    groups = {}
    for req in requests:
        top_group = get_top_level_group(req["group"])
        if top_group not in groups:
            groups[top_group] = []
        groups[top_group].append(req)
    return groups


def generate_file_name(group_name, prefix=""):
    """Gera o nome do arquivo .robot a partir do nome do grupo.

    Se prefix for "neg-", gera "neg-f001_get_pedidos.robot"
    """
    name = unicodedata.normalize("NFKD", group_name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.replace("[", "").replace("]", "")
    name = "".join(c if c.isalnum() or c == " " else "_" for c in name)
    name = name.lower().replace(" ", "_")
    while "__" in name:
        name = name.replace("__", "_")
    name = name.strip("_")
    return f"{prefix}{name}.robot"


def generate_api_slug(collection_name):
    """Gera um slug curto para a API a partir do nome da collection.

    Ex: "API Conecta Pedidos v1.6" -> "conecta-pedidos"
        "Essilor AppSheet v1.223" -> "essilor-appsheet"
    """
    name = unicodedata.normalize("NFKD", collection_name)
    name = "".join(c for c in name if not unicodedata.combining(c))

    # Remove prefixo "API " e sufixo de versao
    name = re.sub(r'\s*v\d+(\.\d+)*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^API\s+', '', name, flags=re.IGNORECASE)

    # Converte para slug
    name = name.strip().lower().replace(" ", "-")
    name = re.sub(r'[^a-z0-9-]', '', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip("-")

    return name


def get_env_from_requests(requests):
    """Extrai o ambiente dos requests (dev ou hml)."""
    for req in requests:
        url = req.get("url", "")
        if "/hml/" in url:
            return "hml"
    return "dev"


def extract_status_code(name):
    """Extrai o status code do nome do teste."""
    match = re.search(r"\[(\d{3})\]", name)
    if match:
        return match.group(1)
    return None


def is_success_status(status_code):
    """Verifica se o status code indica sucesso (2xx).

    Status codes fora do padrao 4xx/5xx sao tratados como sucesso.
    """
    if not status_code:
        return False
    try:
        code = int(status_code)
        if 400 <= code < 600:
            return False
        return True
    except ValueError:
        return False


def is_error_status(status_code):
    """Verifica se o status code indica erro (4xx ou 5xx)."""
    if not status_code:
        return False
    try:
        code = int(status_code)
        return 400 <= code < 600
    except ValueError:
        return False


def get_group_method(requests):
    """Extrai o metodo HTTP principal do grupo."""
    methods = set(r["method"].upper() for r in requests)
    if "POST" in methods:
        return "POST"
    if "GET" in methods:
        return "GET"
    if methods:
        return list(methods)[0]
    return "GET"


def get_group_oper_var(group_name, requests):
    """Extrai o nome da variavel de operacao para o grupo.

    Ex: "[F001] GET /pedidos" -> "oper_pedidos"
    """
    # Tenta extrair o path da URL
    for req in requests:
        url = req.get("url", "")
        # Extrai o path apos o ultimo /v1/ (ou /v2/) ate a query string
        match = re.search(r'/v\d+/([^?\s]+)', url)
        if match:
            path = match.group(1)
            # Pega o segmento principal
            segments = path.split("/")
            main_seg = segments[0]
            # Remove caracteres especiais
            clean = re.sub(r'[^a-zA-Z0-9]', '_', main_seg).lower()
            return "oper_" + clean

    # Fallback: usa o nome do grupo
    name = group_name.replace("[", "").replace("]", "")
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    parts = name.split()
    if len(parts) >= 2:
        last_part = parts[-1].lower().replace("/", "_")
        return "oper_" + last_part
    return "oper_api"


def should_use_oauth(requests):
    """Verifica se o grupo usa autenticacao OAuth ou JWT.

    Retorna True se algum request tem auth basic.
    """
    for req in requests:
        if req.get("auth") == "basic":
            return True
    return False


def is_endpoint_health(requests):
    """Verifica se o grupo eh de health check (nao precisa de auth)."""
    for req in requests:
        name = req.get("name", "").lower()
        url = req.get("url", "").lower()
        if "health" in name or "/health" in url:
            return True
    return False


def generate_keyword_name(requests, tipo):
    """Gera um nome descritivo para a keyword do grupo.

    Args:
        requests: lista de requests do grupo
        tipo: "sucesso" ou "erro"

    Ex: "GET Sucesso - Pedidos", "GET Erro - Pedidos"
    """
    method = get_group_method(requests)

    # Extrai assunto do grupo (com fallback seguro)
    group = ""
    if requests and len(requests) > 0:
        group = requests[0].get("group", "")

    parts = group.split(" / ")
    top = parts[0] if parts else ""
    # Remove [FXXX] e GET/POST prefixos
    top_clean = re.sub(r'\[F\d+\]\s*', '', top)
    top_clean = top_clean.replace("GET /", "").replace("POST /", "").strip()

    if top_clean:
        segs = top_clean.split("/")
        subject = segs[-1].strip() if segs else top_clean
        subject = subject.replace("-", " ").title()
    else:
        subject = "API"

    if tipo == "sucesso":
        return f"{method} Sucesso - {subject}"
    else:
        return f"{method} Erro - {subject}"


def generate_group_keyword(group_name, requests, tipo):
    """Gera uma keyword reutilizavel para o grupo.

    A keyword encapsula:
    1. POST Autenticacao JWT/Oauth
    2. Create Session API Proxy/Adapter
    3. Chamada HTTP
    4. Validacoes basicas (response time, headers)

    Args:
        group_name: nome do grupo
        requests: requests do grupo
        tipo: "sucesso" ou "erro"

    Returns:
        String com o codigo Robot da keyword.
    """
    kw_name = generate_keyword_name(requests, tipo)
    method = get_group_method(requests)
    auth_keyword = "POST Autenticacao JWT"
    session_keyword = "Create Session API Proxy"

    if should_use_oauth(requests):
        auth_keyword = "POST Autenticacao Oauth"

    if is_endpoint_health(requests):
        session_keyword = "Create Session API Adapter"

    oper_var = get_group_oper_var(group_name, requests)

    lines = []
    lines.append(kw_name)
    lines.append(f"    [Arguments]    ${{user}}    ${{pwd}}    ${{cnpjOtica}}    ${{cnpjLab}}    ${{api_proxy}}    ${{api_version_dev}}    ${{api_version_hml}}    ${{{oper_var}}}")

    if not is_endpoint_health(requests):
        lines.append("")
        lines.append(f"    POST Autenticacao JWT        ${{user}}    ${{pwd}}")
        lines.append(f"    {session_keyword}     ${{api_proxy}}")

    lines.append("")
    lines.append(f"    &{{headers}}=     Create Dictionary      Content-Type=application/json    client_id=${{client_id}}      access_token=${{jwt}}      laboratorio=${{cnpjLab}}")
    lines.append(f"    ${{response}}=    {method} On Session         api-in-test      ${{{oper_var}}}       headers=${{headers}}    expected_status=any")
    lines.append("")
    lines.append("    Set Global Variable    ${api_response}    ${response}")
    lines.append("")
    lines.append("    ${status_code}=    Convert To String    ${api_response.status_code}")

    if tipo == "sucesso":
        lines.append("    Should Contain Any        ${status_code}    200     206")
    lines.append("")
    lines.append("    Validate ResponseTime")
    lines.append("    Validate Header API Version      ${api_version_dev}      ${api_version_hml}     proxy")
    lines.append("    Validate Header Content Type     application/json")
    lines.append("")

    return "\n".join(lines)


def generate_test_case_enxuto(request, keyword_name, sequence=1):
    """Gera um test case enxuto que chama a keyword do grupo.

    Args:
        request: request parseado
        keyword_name: nome da keyword a ser chamada
        sequence: numero sequencial do teste (T01, T02...)

    Returns:
        String com o codigo Robot do test case.
    """
    lines = []

    name = request["name"]
    method = request["method"]

    if request["disabled"]:
        lines.append(f"{name}    Skip    Request desabilitado na collection Postman")
        lines.append("")
        return "\n".join(lines)

    # Nome do test case
    seq_str = f"T{sequence:02d}"
    test_name = f"{seq_str} - Perfil LabOG - {keyword_name} - {name}"
    lines.append(test_name)

    oper_var = f"${{oper_conecta_pedidos}}"

    lines.append(f"    {keyword_name}        @{{dados_login}}    @{{api_pedidos_proxy}}     {oper_var}")
    lines.append("")

    return "\n".join(lines)


def generate_documentation(requests, collection_name, tipo, keyword_name):
    """Gera a secao Documentation multi-linha."""
    lines = []
    lines.append(f"Documentation    {collection_name} - {tipo}")

    seen = set()
    for req in requests:
        test_name = req["name"]
        if test_name not in seen:
            seen.add(test_name)
            lines.append(f"...              - {test_name}")

    file_name = generate_file_name(get_top_level_group(requests[0]["group"]), "neg-" if tipo == "erro" else "")
    env = get_env_from_requests(requests)
    api_slug = generate_api_slug(collection_name)
    lines.append(f"...")
    lines.append(f"...        command to run tests:")
    lines.append(f"...        robot -d results\\{api_slug}\\{file_name} {file_name}")

    return "\n".join(lines)


def generate_settings(requests, collection_name, base_resource, tipo, keyword_name):
    """Gera a secao *** Settings *** do arquivo .robot."""
    lines = []
    lines.append("*** Settings ***")
    lines.append(generate_documentation(requests, collection_name, tipo, keyword_name))
    lines.append("")
    lines.append(f"Resource        {base_resource}")
    lines.append("")
    return "\n".join(lines)


def generate_suite_setup(requests, environment):
    """Gera Suite Setup injetado como comentario."""
    return '# Suíte Setup     Definir Dados do Laboratorio     LabOG     LabOG     hml'


def generate_variables(baseapi_variables, collection_variables):
    """Gera secao *** Variables *** apenas com variaveis que nao existem no base-api."""
    lines = []
    lines.append("*** Variables ***")

    baseapi_set = baseapi_variables if isinstance(baseapi_variables, set) else set()

    for key, value in collection_variables.items():
        if not value:
            continue
        if key in baseapi_set:
            continue
        lines.append(f"${{{key}}}    {value}")

    lines.append("")
    return "\n".join(lines)


def generate_keywords_section():
    """Gera o inicio da secao *** Keywords ***."""
    return "*** Keywords ***"


def generate_assertions_from_events(events):
    """Gera assertions a partir dos eventos (test scripts) do Postman.

    Usa o modulo assertions para traduzir as assertions do Postman JS
    para Robot Framework.
    """
    from service.assertions import parse_assertions
    return parse_assertions(events)


def generate_robot_file(requests, collection_name, variables, base_resource, tipo, baseapi_variables):
    """Gera o conteudo completo de um arquivo .robot.

    Args:
        requests: requests do grupo
        collection_name: nome da collection
        variables: variaveis da collection
        base_resource: caminho do base-api.robot
        tipo: "sucesso" ou "erro"
        baseapi_variables: set de variaveis do base-api.robot

    Returns:
        String com o conteudo do arquivo.
    """
    group = get_top_level_group(requests[0]["group"])
    keyword_name = generate_keyword_name(requests, tipo)

    sections = []

    # Settings
    sections.append(generate_settings(requests, collection_name, base_resource, tipo, keyword_name))

    # Suite Setup (comentado)
    sections.append(generate_suite_setup(requests, ""))

    # Variables (apenas as que nao existem no base-api)
    sections.append(generate_variables(baseapi_variables, variables))

    # Test Cases
    sections.append("*** Test Cases ***")
    for i, req in enumerate(requests, 1):
        sections.append(generate_test_case_enxuto(req, keyword_name, sequence=i))

    # Keywords
    sections.append(generate_keywords_section())
    group_keyword = generate_group_keyword(group, requests, tipo)
    sections.append(group_keyword)

    return "\n".join(sections) + "\n"


def generate_robot(data, output_dir, base_resource, environment):
    """Gera os arquivos .robot a partir dos dados parseados.

    Cria uma subpasta com o nome da API dentro de output_dir.
    Dentro dela, dois arquivos por grupo:
      - {grupo}.robot (apenas testes de sucesso)
      - neg-{grupo}.robot (apenas testes de erro)

    Args:
        data: dicionario retornado por parse_collection
        output_dir: diretorio de saida
        base_resource: caminho para o base-api.robot
        environment: ambiente (dev, hml)

    Returns:
        Lista de caminhos dos arquivos gerados.
    """
    collection_name = data.get("collection_name", "Sem nome")
    variables = data.get("variables", {})
    baseapi_variables = data.get("baseapi_variables", set())
    requests = data.get("requests", [])

    if not requests:
        return []

    # Cria subpasta com o nome da API
    api_slug = generate_api_slug(collection_name)
    output_dir = os.path.join(output_dir, api_slug)
    os.makedirs(output_dir, exist_ok=True)

    groups = group_requests_by_top_level(requests)

    files_created = []
    for group_name, group_requests in groups.items():

        success_reqs = []
        error_reqs = []
        for req in group_requests:
            sc = extract_status_code(req["name"])
            if sc and is_error_status(sc):
                error_reqs.append(req)
            else:
                success_reqs.append(req)

        if success_reqs:
            file_name = generate_file_name(group_name)
            file_path = os.path.join(output_dir, file_name)

            content = generate_robot_file(
                success_reqs, collection_name, variables,
                base_resource, "sucesso", baseapi_variables
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            files_created.append(file_path)
            print(f"Gerado: {file_path} ({len(success_reqs)} testes de sucesso)")

        if error_reqs:
            file_name = generate_file_name(group_name, prefix="neg-")
            file_path = os.path.join(output_dir, file_name)

            content = generate_robot_file(
                error_reqs, collection_name, variables,
                base_resource, "erro", baseapi_variables
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            files_created.append(file_path)
            print(f"Gerado: {file_path} ({len(error_reqs)} testes de erro)")

    return files_created
