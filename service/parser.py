"""Parser de Postman Collection v2.1 JSON.

Responsável por:
- Ler o arquivo JSON da collection
- Navegar recursivamente pela estrutura aninhada (pastas e subpastas)
- Extrair: nome do grupo, nome do teste, método, URL, headers, body, auth
- Resolver {{variaveis}} com valores do array variable[]
- Marcar requests com disabled: true para skip
- Ignorar grupos de autenticao (F000, Autenticacao)
- Extrair catalogo de variaveis e keywords do base-api.robot
"""

import json
import re


def load_collection(input_file):
    """Le e retorna o conteudo do arquivo JSON da collection."""
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_variables(collection):
    """Extrai as variaveis da collection e retorna como dicionario."""
    variables = {}
    for var in collection.get("variable", []):
        variables[var["key"]] = var.get("value", "")
    return variables


def resolve_variables(text, variables):
    """Substitui {{variavel}} pelo valor real usando o dicionario de variaveis."""
    if not text:
        return text
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def build_url(url_obj, variables):
    """Monta a URL completa a partir do objeto url do Postman."""
    raw = url_obj.get("raw", "")
    if not raw:
        return ""

    url = resolve_variables(raw, variables)

    query_params = url_obj.get("query", [])
    disabled_keys = [p["key"] for p in query_params if p.get("disabled", False)]

    if disabled_keys:
        query_start = url.find("?")
        if query_start != -1:
            base_url = url[:query_start]
            query_string = url[query_start + 1:]
            params = query_string.split("&")
            filtered = [p for p in params if not p.split("=")[0] in disabled_keys]
            if filtered:
                url = base_url + "?" + "&".join(filtered)
            else:
                url = base_url

    return url


def extract_headers(headers, variables):
    """Extrai headers e resolve variaveis. Ignora headers desabilitados."""
    result = {}
    for header in headers or []:
        if header.get("disabled", False):
            continue
        key = header["key"]
        value = resolve_variables(header.get("value", ""), variables)
        result[key] = value
    return result


def extract_body(request):
    """Extrai o body da request se existir."""
    body_obj = request.get("body", {})
    if not body_obj:
        return None

    raw = body_obj.get("raw", "")
    if raw:
        return raw

    mode = body_obj.get("mode")
    if mode in ("formdata", "urlencoded"):
        return body_obj

    return None


def extract_auth(request):
    """Extrai o tipo de autenticacao da request."""
    auth = request.get("auth", {})
    if not auth:
        return None
    return auth.get("type")


def is_request_disabled(item):
    """Verifica se o request esta desabilitado."""
    if item.get("disabled", False):
        return True
    url_obj = item.get("request", {}).get("url", {})
    for param in url_obj.get("query", []):
        if param.get("disabled", False):
            return True
    return False


def is_auth_group(group_name):
    """Verifica se o nome do grupo indica um grupo de autenticacao.

    Retorna True se o nome comeca com [F000] ou contem 'Autenticacao'.
    """
    if not group_name:
        return False
    name_lower = group_name.lower()
    if name_lower.startswith("[f000]"):
        return True
    if "autenticacao" in name_lower:
        return True
    return False


def should_skip_group(group_name):
    """Verifica se um grupo deve ser ignorado no parser.

    Grupos de autenticacao sao ignorados porque a autenticacao
    sera feita pelas keywords do base-api.robot.
    """
    return is_auth_group(group_name)


def extract_baseapi_catalog(baseapi_file):
    """Extrai variaveis e keywords do arquivo base-api.robot.

    Retorna um dicionario com:
      - variables: set de nomes de variaveis definidas
      - keywords: set de nomes de keywords definidas
      - lists: set de nomes de listas (@{...})
    """
    catalog = {
        "variables": set(),
        "keywords": set(),
        "lists": set(),
    }

    if not baseapi_file or not os.path.exists(baseapi_file):
        return catalog

    with open(baseapi_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extrai variaveis: ${nome_var}
    for match in re.finditer(r'^\s*\$\{(\w+)\}\s+', content, re.MULTILINE):
        catalog["variables"].add(match.group(1))

    # Extrai listas: @{nome_lista}
    for match in re.finditer(r'^\s*@\{(\w+)\}\s+', content, re.MULTILINE):
        catalog["lists"].add(match.group(1))

    # Extrai keywords: nomes de keywords (sem indentacao, antes de *** ou [Arguments])
    in_keywords = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "*** Keywords ***":
            in_keywords = True
            continue
        if in_keywords and stripped.startswith("*** "):
            break
        if in_keywords and stripped and not stripped.startswith("#") and not stripped.startswith("[") and not stripped.startswith("    ") and not stripped.startswith("${") and not stripped.startswith("@{") and "    " not in stripped:
            catalog["keywords"].add(stripped)

    return catalog


def parse_request(item, group_path, variables):
    """Parseia um request (item folha) e retorna um dicionario com todos os dados."""
    request = item.get("request", {})
    name = item.get("name", "Sem nome")

    url = build_url(request.get("url", {}), variables)
    method = request.get("method", "GET")
    headers = extract_headers(request.get("header", []), variables)
    body = extract_body(request)
    auth = extract_auth(request)
    disabled = is_request_disabled(item) or is_request_disabled(item)

    events = []
    for event in item.get("event", []):
        script = event.get("script", {})
        exec_lines = script.get("exec", [])
        if exec_lines:
            events.append({
                "listen": event.get("listen", ""),
                "script": "\n".join(exec_lines),
            })

    return {
        "group": group_path,
        "name": name,
        "method": method,
        "url": url,
        "headers": headers,
        "body": body,
        "auth": auth,
        "disabled": disabled,
        "events": events,
    }


def parse_collection_items(items, group_path, variables, results):
    """Navega recursivamente pelos items da collection.

    Se o item tem 'item' filho -> eh uma pasta, entra recursivamente.
    Se o item tem 'request' -> eh um request, parseia e salva.
    Grupos de autenticacao (F000) sao ignorados.
    """
    for item in items:
        item_name = item.get("name", "Sem nome")
        current_path = f"{group_path} / {item_name}" if group_path else item_name

        # Se tem filhos, eh uma pasta
        if "item" in item and item["item"]:
            # Verifica se esta pasta ou alguma ancestral eh de auth
            # So entra recursivamente se nao for grupo de auth
            if not should_skip_group(item_name):
                parse_collection_items(item["item"], current_path, variables, results)
        # Se tem request, eh um teste
        elif "request" in item:
            # Nao adiciona se o grupo atual for de auth
            if not should_skip_group(item_name) and not any(should_skip_group(p) for p in current_path.split(" / ")):
                request_data = parse_request(item, current_path, variables)
                results.append(request_data)


def parse_collection(input_file, baseapi_file=None):
    """Funcao principal: le o JSON e retorna todos os dados da collection.

    Args:
        input_file: caminho para o arquivo da collection Postman
        baseapi_file: (opcional) caminho para base-api.robot

    Retorna um dicionario com:
      - collection_name: nome da collection
      - variables: dicionario de variaveis resolvidas
      - baseapi_variables: set de variaveis do base-api.robot
      - baseapi_keywords: set de keywords do base-api.robot
      - baseapi_lists: set de listas do base-api.robot
      - requests: lista de requests parseados
      - skip_groups: lista de grupos ignorados
    """
    collection = load_collection(input_file)
    variables = extract_variables(collection)

    collection_name = collection.get("info", {}).get("name", "Sem nome")

    # Extrai catalogo do base-api.robot
    catalog = extract_baseapi_catalog(baseapi_file)

    results = []
    top_level_items = collection.get("item", [])
    parse_collection_items(top_level_items, "", variables, results)

    return {
        "collection_name": collection_name,
        "variables": variables,
        "baseapi_variables": catalog["variables"],
        "baseapi_keywords": catalog["keywords"],
        "baseapi_lists": catalog["lists"],
        "requests": results,
    }


import os
