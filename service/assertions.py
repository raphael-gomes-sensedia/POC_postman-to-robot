"""Traducao de assertions Postman JS para Robot Framework.

Cobre todas as assertions basicas da secao 8.1 do documento POC:
- pm.response.to.have.status()
- pm.expect().to.not.be.empty
- pm.expect().to.be.null
- pm.expect().to.eql()
- pm.expect().to.be.a('string')
- pm.expect().to.be.a('number')
- pm.expect().to.contain()
- pm.expect(pm.response.text()).to.be.empty
- pm.expect().to.be.above(0)
- pm.collectionVariables.set()
- pm.environment.set()
"""

import re


def translate_status_code(status):
    """Traduz pm.response.to.have.status() para Robot.

    Args:
        status: codigo de status como string (ex: "200", "404")

    Returns:
        Linha Robot ou None se invalido.
    """
    if not status:
        return None

    try:
        code = int(status)
    except ValueError:
        return None

    # Status code valido deve estar entre 100 e 599
    if code < 100 or code > 599:
        return None

    return "    Status Should Be    " + status + "    ${api_response}"


def translate_expect_not_empty(variable):
    """Traduz pm.expect(x).to.not.be.empty para Robot.

    Args:
        variable: nome da variavel a verificar

    Returns:
        Linha Robot ou None se variavel vazia.
    """
    if not variable:
        return None

    return "    Should Not Be Empty    ${" + variable + "}"


def translate_expect_null(variable):
    """Traduz pm.expect(x).to.be.null para Robot.

    Args:
        variable: nome da variavel a verificar

    Returns:
        Linha Robot ou None se variavel vazia.
    """
    if not variable:
        return None

    return "    Should Be Empty    ${" + variable + "}"


def translate_expect_eql(variable, value):
    """Traduz pm.expect(x).to.eql(y) para Robot.

    Args:
        variable: nome da variavel
        value: valor esperado

    Returns:
        Linha Robot ou None se valores vazios.
    """
    if not variable or not value:
        return None

    # Remove aspas do valor esperado
    clean_value = value.strip('"').strip("'")

    return "    Should Be Equal As Strings    ${" + variable + "}    " + clean_value


def translate_expect_type(variable, type_name):
    """Traduz pm.expect(x).to.be.a('type') para Robot.

    Args:
        variable: nome da variavel
        type_name: tipo esperado (string, number, etc)

    Returns:
        Linha Robot ou None se tipo desconhecido.
    """
    if not variable or not type_name:
        return None

    # Remove aspas do tipo
    clean_type = type_name.strip('"').strip("'")

    if clean_type == "string":
        return "    Should Not Be Empty    ${" + variable + "}"
    if clean_type == "number":
        return "    Should Be Equal As Numbers    ${" + variable + "}"

    return None


def translate_expect_contain(variable, value):
    """Traduz pm.expect(x).to.contain(y) para Robot.

    Args:
        variable: nome da variavel
        value: valor a procurar

    Returns:
        Linha Robot ou None se valores vazios.
    """
    if not variable or not value:
        return None

    # Se o valor estiver entre aspas, é uma string literal
    is_quoted = (value.startswith('"') and value.endswith('"')) or \
                (value.startswith("'") and value.endswith("'"))

    if is_quoted:
        clean_value = value.strip('"').strip("'")
        return "    Should Contain    ${" + variable + "}    " + clean_value
    else:
        # Valor é uma variavel
        return "    Should Contain    ${" + variable + "}    ${" + value + "}"


def translate_expect_response_empty():
    """Traduz pm.expect(pm.response.text()).to.be.empty para Robot.

    Returns:
        Linha Robot para verificar se o conteudo da resposta esta vazio.
    """
    return "    Should Be Empty    ${api_response.content}"


def translate_expect_above(variable, value):
    """Traduz pm.expect(x).to.be.above(n) para Robot.

    Args:
        variable: nome da variavel
        value: valor limite

    Returns:
        Linha Robot ou None se variavel vazia.
    """
    if not variable:
        return None

    return "    Should Be True    ${" + variable + "} > " + value


def translate_collection_variable_set(key, value):
    """Traduz pm.collectionVariables.set(key, value) para Robot.

    Args:
        key: nome da variavel da collection
        value: valor a atribuir

    Returns:
        Linha Robot ou None se valores vazios.
    """
    if not key or not value:
        return None

    return "    Set Test Variable    ${" + key + "}    ${" + value + "}"


def translate_environment_variable_set(key, value):
    """Traduz pm.environment.set(key, value) para Robot.

    Args:
        key: nome da variavel de ambiente
        value: valor a atribuir

    Returns:
        Linha Robot ou None se valores vazios.
    """
    if not key or not value:
        return None

    return "    Set Test Variable    ${" + key + "}    ${" + value + "}"


def extract_postman_assertions(script):
    """Extrai e traduz todas as assertions de um script Postman.

    Analisa o script JavaScript do Postman e retorna uma lista
    de linhas Robot Framework equivalentes.

    Args:
        script: string com o codigo JavaScript do Postman

    Returns:
        Lista de linhas Robot Framework traduzidas.
    """
    if not script:
        return []

    lines = []

    # 1. pm.response.to.have.status(N)
    status_match = re.search(
        r'pm\.response\.to\.have\.status\((\d+)\)', script
    )
    if status_match:
        code = status_match.group(1)
        line = translate_status_code(code)
        if line:
            lines.append(line)

    # 2. pm.expect(x).to.not.be.empty
    not_empty_matches = re.findall(
        r'pm\.expect\((\w+(?:\.\w+|\[\d+\])*)\)\.to\.not\.be\.empty', script
    )
    for var in not_empty_matches:
        line = translate_expect_not_empty(var)
        if line:
            lines.append(line)

    # 3. pm.expect(x).to.be.null ou pm.expect(x).to.not.be.null
    null_matches = re.findall(
        r'pm\.expect\((\w+(?:\.\w+|\[\d+\])*)\)\.to(?:\.not)?\.be\.null', script
    )
    for var in null_matches:
        line = translate_expect_null(var)
        if line:
            lines.append(line)

    # 4. pm.expect(x).to.eql(y)
    eql_matches = re.findall(
        r'pm\.expect\((\w+(?:\.\w+|\[\d+\])*)\)\.to\.eql\((.+?)\)', script
    )
    for var, val in eql_matches:
        line = translate_expect_eql(var.strip(), val.strip())
        if line:
            lines.append(line)

    # 5. pm.expect(x).to.be.a('type')
    type_matches = re.findall(
        r'pm\.expect\((\w+(?:\.\w+|\[\d+\])*)\)\.to\.be\.a\(["\'](\w+)["\']\)', script
    )
    for var, typ in type_matches:
        line = translate_expect_type(var.strip(), typ.strip())
        if line:
            lines.append(line)

    # 6. pm.expect(x).to.contain(y)
    contain_matches = re.findall(
        r'pm\.expect\((\w+(?:\.\w+|\[\d+\])*)\)\.to\.contain\((.+?)\)', script
    )
    for var, val in contain_matches:
        line = translate_expect_contain(var.strip(), val.strip())
        if line:
            lines.append(line)

    # 7. pm.expect(pm.response.text()).to.be.empty
    response_empty = re.search(
        r'pm\.expect\(pm\.response\.text\(\)\)\.to\.be\.empty', script
    )
    if response_empty:
        lines.append(translate_expect_response_empty())

    # 8. pm.expect(x).to.be.above(n)
    above_matches = re.findall(
        r'pm\.expect\((\w+(?:\.\w+|\[\d+\])*)\)\.to\.be\.above\((.+?)\)', script
    )
    for var, val in above_matches:
        line = translate_expect_above(var.strip(), val.strip())
        if line:
            lines.append(line)

    # 9. pm.collectionVariables.set(key, value)
    collection_matches = re.findall(
        r'pm\.collectionVariables\.set\(["\'](\w+)["\'],\s*(.+?)\)', script
    )
    for key, val in collection_matches:
        line = translate_collection_variable_set(key.strip(), val.strip())
        if line:
            lines.append(line)

    # 10. pm.environment.set(key, value)
    env_matches = re.findall(
        r'pm\.environment\.set\(["\'](\w+)["\'],\s*(.+?)\)', script
    )
    for key, val in env_matches:
        line = translate_environment_variable_set(key.strip(), val.strip())
        if line:
            lines.append(line)

    return lines


def parse_assertions(events):
    """Extrai assertions de todos os eventos test de um request.

    Ignora eventos prerequest.

    Args:
        events: lista de eventos com 'listen' e 'script'

    Returns:
        Lista de todas as linhas Robot traduzidas.
    """
    if not events:
        return []

    all_lines = []
    for event in events:
        if event.get("listen") == "test":
            script = event.get("script", "")
            lines = extract_postman_assertions(script)
            all_lines.extend(lines)

    return all_lines
