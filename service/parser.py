"""Parser de Postman Collection v2.1 JSON.

Responsável por:
- Ler o arquivo JSON da collection
- Navegar recursivamente pela estrutura aninhada (pastas e subpastas)
- Extrair: nome do grupo, nome do teste, método, URL, headers, body, auth
- Resolver {{variaveis}} com valores do array variable[]
- Marcar requests com disabled: true para skip
"""

import json


def load_collection(input_file):
    """Lê e retorna o conteúdo do arquivo JSON da collection."""
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_variables(collection):
    """Extrai as variáveis da collection e retorna como dicionário."""
    variables = {}
    for var in collection.get("variable", []):
        variables[var["key"]] = var.get("value", "")
    return variables


def resolve_variables(text, variables):
    """Substitui {{variavel}} pelo valor real usando o dicionário de variáveis."""
    if not text:
        return text
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def build_url(url_obj, variables):
    """Monta a URL completa a partir do objeto url do Postman.

    Usa o campo 'raw' que ja contem a URL completa com variaveis,
    depois resolve as variaveis e remove params desabilitados.
    """
    raw = url_obj.get("raw", "")
    if not raw:
        return ""

    # Resolve variaveis na URL raw
    url = resolve_variables(raw, variables)

    # Remove query params desabilitados da URL
    query_params = url_obj.get("query", [])
    disabled_keys = [p["key"] for p in query_params if p.get("disabled", False)]

    if disabled_keys:
        # Encontra o inicio da query string
        query_start = url.find("?")
        if query_start != -1:
            base_url = url[:query_start]
            query_string = url[query_start + 1:]
            # Filtra params desabilitados
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
    if mode == "formdata":
        return body_obj
    if mode == "urlencoded":
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
    # Verifica se algum param de query esta desabilitado
    url_obj = item.get("request", {}).get("url", {})
    for param in url_obj.get("query", []):
        if param.get("disabled", False):
            return True
    return False


def parse_request(item, group_path, variables):
    """Parseia um request (item folha) e retorna um dicionario com todos os dados."""
    request = item.get("request", {})
    name = item.get("name", "Sem nome")

    url = build_url(request.get("url", {}), variables)
    method = request.get("method", "GET")
    headers = extract_headers(request.get("header", []), variables)
    body = extract_body(request)
    auth = extract_auth(request)
    disabled = is_request_disabled(item)

    # Extrai os eventos (test scripts)
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

    Se o item tem 'item' filho -> é uma pasta, entra recursivamente.
    Se o item tem 'request' -> é um request, parseia e salva.
    """
    for item in items:
        item_name = item.get("name", "Sem nome")
        current_path = f"{group_path} / {item_name}" if group_path else item_name

        # Se tem filhos, é uma pasta -> entra recursivamente
        if "item" in item and item["item"]:
            parse_collection_items(item["item"], current_path, variables, results)
        # Se tem request, é um teste
        elif "request" in item:
            # Usa o grupo atual (sem repetir o nome do item)
            request_data = parse_request(item, current_path, variables)
            results.append(request_data)


def parse_collection(input_file):
    """Funcao principal: lê o JSON e retorna lista de requests parseados.

    Cada request retornado tem:
      - group: caminho da pasta (ex: "[F001] GET /pedidos / Sucesso [200,206]")
      - name: nome do teste
      - method: metodo HTTP (GET, POST, etc)
      - url: URL completa com variaveis resolvidas
      - headers: dicionario de headers
      - body: body da request (se existir)
      - auth: tipo de autenticacao (se existir)
      - disabled: True se o request deve ser pulado
      - events: lista de scripts de teste (test scripts)
    """
    collection = load_collection(input_file)
    variables = extract_variables(collection)

    results = []
    top_level_items = collection.get("item", [])
    parse_collection_items(top_level_items, "", variables, results)

    return results
