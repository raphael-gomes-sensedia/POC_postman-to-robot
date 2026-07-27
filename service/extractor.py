"""
Modulo extrator deterministico de schemas e payloads.

Responsavel por extrair de forma deterministica:
- Payloads: body raw JSON das requests, salvos em resources/payload_<nome>.json
- Schemas: objetos JSON inline nos test scripts do Postman, salvos em schemas/<endpoint>_schema.json

A extracao deterministica reduz a carga cognitiva do subagente LLM, que passa
apenas a referenciar os arquivos ja extraidos. Quando a extracao nao e possivel
(por exemplo, body nao-JSON ou schema em formato nao reconhecido), o subagente
pode complementar manualmente.

"""

import json
import os
import re
import unicodedata
from typing import Optional

from service.generator import generate_api_slug


def _slugify(text: str) -> str:
    """
    Converte texto em slug seguro para nome de arquivo.

    Remove acentos, caracteres especiais e espacos, substituindo-os por
    hifens e convertendo para minusculas.

    Ex: "POST /pedidos Criar" -> "post-pedidos-criar"

    Parametros:
        text (str): Texto a ser convertido.

    Retorna:
        str: Slug em minusculas com hifens.
    """
    name = unicodedata.normalize("NFKD", text)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.replace("[", "").replace("]", "")
    name = "".join(c if c.isalnum() or c == " " else "-" for c in name)
    name = name.lower().replace(" ", "-")
    while "--" in name:
        name = name.replace("--", "-")
    return name.strip("-")


def extract_payloads(requests: list, output_dir: str, api_slug: str) -> list:
    """
    Extrai payloads JSON do body das requests e salva em resources/.

    Para cada request que possui um body raw valido como JSON, tenta fazer
    json.loads e salva o resultado em <output_dir>/resources/payload_<slug>.json.
    Requests sem body, com body None ou com body nao-JSON sao ignoradas.

    """
    if not requests:
        return []

    resources_dir = os.path.join(output_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)

    extraidos = []

    for req in requests:
        body = req.get("body")

        if not body or not isinstance(body, str):
            continue

        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            continue

        slug = _slugify(req.get("name", "sem_nome"))
        file_name = f"payload_{slug}.json"
        file_path = os.path.join(resources_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        extraidos.append({
            "method": req.get("method", ""),
            "test_name": req.get("name", ""),
            "file_name": file_name,
        })

    return extraidos


def _extract_json_from_script(script: Optional[str]) -> Optional[dict]:
    """
    Extrai um objeto JSON inline de um script JavaScript do Postman.

    Procura por padroes de objetos JSON literais em scripts de teste do Postman,
    especificamente objetos assigned a variaveis que se assemelham a schemas
    (ex: var schema = { ... };). Usa regex para encontrar o bloco e tenta
    fazer json.loads do conteudo.

    A regex procura por padroes como:
        var <nome> = { ... };
    E tenta fazer parse do conteudo entre { e }.

    """
    if not script:
        return None

    # Padrao para encontrar "var <nome> = { ... };" ou "const <nome> = { ... };"
    # O grupo captura o conteudo entre { e }
    padrao_var = re.compile(
        r'(?:var|const|let)\s+\w+\s*=\s*(\{[^;]+\})\s*;',
        re.DOTALL
    )

    matches = padrao_var.findall(script)

    for match in matches:
        try:
            obj = json.loads(match)
            # Verifica se parece um schema (tem "type" ou "properties")
            if isinstance(obj, dict) and ("type" in obj or "properties" in obj):
                return obj
        except (json.JSONDecodeError, TypeError):
            continue

    # Tenta encontrar JSON.stringify({...})
    padrao_stringify = re.compile(
        r'JSON\.stringify\((\{[^)]+\})\)',
        re.DOTALL
    )

    matches_stringify = padrao_stringify.findall(script)

    for match in matches_stringify:
        try:
            obj = json.loads(match)
            if isinstance(obj, dict):
                return obj
        except (json.JSONDecodeError, TypeError):
            continue

    return None


def extract_schemas(requests: list, output_dir: str, api_slug: str) -> list:
    """
    Extrai schemas JSON dos test scripts do Postman e salva em schemas/.

    Para cada request, examina os eventos de teste (listen == "test") procurando
    por objetos JSON inline que representem schemas. Se encontrar, tenta fazer
    json.loads e salva em <output_dir>/schemas/<slug>_schema.json.

    """
    if not requests:
        return []

    schemas_dir = os.path.join(output_dir, "schemas")
    os.makedirs(schemas_dir, exist_ok=True)

    extraidos = []

    for req in requests:
        events = req.get("events", [])

        for event in events:
            if event.get("listen") != "test":
                continue

            script = event.get("script", "")
            schema = _extract_json_from_script(script)

            if schema is not None:
                slug = _slugify(req.get("name", "sem_nome"))
                file_name = f"{slug}_schema.json"
                file_path = os.path.join(schemas_dir, file_name)

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(schema, f, ensure_ascii=False, indent=2)

                extraidos.append({
                    "method": req.get("method", ""),
                    "test_name": req.get("name", ""),
                    "file_name": file_name,
                })
                break  # Apenas um schema por request

    return extraidos


def extract_all(data: dict, output_dir: str) -> dict:
    """
    Orquestra a extracao de payloads e schemas a partir dos dados da collection.

    Recebe o dicionario retornado por parse_collection() e executa ambas as
    extracoes (payloads e schemas), criando os diretorios resources/ e schemas/
    dentro do output_dir. Retorna um relatorio com as listas de arquivos extraidos.

    """
    collection_name = data.get("collection_name", "Sem nome")
    requests = data.get("requests", [])

    api_slug = generate_api_slug(collection_name)

    # Garante que os diretorios existam mesmo se nao houver requests para extrair
    os.makedirs(os.path.join(output_dir, "resources"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "schemas"), exist_ok=True)

    payloads = extract_payloads(requests, output_dir, api_slug)
    schemas = extract_schemas(requests, output_dir, api_slug)

    return {
        "payloads": payloads,
        "schemas": schemas,
    }