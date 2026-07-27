"""
Modulo de geracao de manifest JSON intermediario (ponte deterministica).

Responsavel por gerar um arquivo <file_name>.manifest.json sidecar para cada
arquivo .robot, contendo os dados estruturados das requests parseadas da
collection Postman, as assertions traduzidas para Robot Framework e as
sugestoes de mapeamento @{api_*} e ${oper_*}.

Este manifest serve como contrato explicito entre a camada deterministica
(Python) e o subagente LLM (robot-test-writer), eliminando a necessidade de
re-derivar dados da collection original.

"""

import json
import os
import re
import unicodedata
from typing import Optional

from service.assertions import parse_assertions
from service.mapper import parse_base_api, match_api_slug, match_path
from service.checksum import add_checksum_to_manifest


def normalize_for_group(group_name: str) -> str:
    """
    Extrai o codigo de grupo (F001, F002, etc) do nome do grupo.

    Remove acentos, colchetes e extras, mantendo apenas o identificador
    principal do grupo para uso no campo "group" do manifest.

    """
    if not group_name:
        return "Sem grupo"

    name = unicodedata.normalize("NFKD", group_name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.replace("[", "").replace("]", "")
    return name.strip()


def get_top_level_group(group_path: str) -> str:
    """
    Extrai o grupo de primeiro nivel do caminho completo.

    O caminho do grupo usa " / " como separador entre niveis.
    Ex: "[F001] GET /pedidos / Sucesso" -> "[F001] GET /pedidos"

    """
    parts = group_path.split(" / ")
    if parts and parts[0]:
        return parts[0]
    return "Sem grupo"


def build_test_case(req: dict, seq_num: int, oper_vars: list) -> dict:
    """
    Constrói o dicionario de um test case para o manifest a partir de uma request parseada.

    Extrai todos os dados estruturados da request, traduz as assertions do Postman
    JS para Robot Framework (usando o modulo assertions.py) e faz o mapeamento
    fuzzy do path da URL contra as variaveis ${oper_*} do base-api.robot.

    """
    # Extrai o status code do nome do teste (ex: "[200] GET /pedidos" -> "200")
    status_code: Optional[str] = None
    match = re.search(r"\[(\d{3})\]", req.get("name", ""))
    if match:
        status_code = match.group(1)

    # Traduz assertions do Postman JS para Robot Framework
    events = req.get("events", [])
    translated_lines = parse_assertions(events)

    # Extrai o script bruto do evento test para referencia
    raw_script = ""
    for event in events:
        if event.get("listen") == "test":
            raw_script = event.get("script", "")
            break

    # Faz o mapeamento fuzzy do path da URL contra ${oper_*}
    path_mapping = match_path(req.get("url", ""), oper_vars)

    return {
        "seq": f"T{seq_num:02d}",
        "name": req.get("name", ""),
        "request": {
            "method": req.get("method", ""),
            "url": req.get("url", ""),
            "headers": req.get("headers", {}),
            "body": req.get("body"),
            "auth": req.get("auth"),
        },
        "assertions": {
            "raw_script": raw_script,
            "translated": translated_lines,
        },
        "path_mapping": path_mapping,
        "status_code_expected": status_code,
    }


def generate_manifest_file(
    requests: list,
    collection_name: str,
    variables: dict,
    tipo: str,
    file_name: str,
    api_slug: str,
    base_api_path: str,
    output_dir: str,
) -> str:
    """
    Gera o arquivo .manifest.json sidecar para um arquivo .robot.

    Cria um arquivo JSON ao lado do .robot contendo todos os dados estruturados
    das requests, assertions traduzidas e mapeamentos sugeridos. Este arquivo
    serve como contrato explicito para o subagente LLM.

    """
    # 1. Parse do base-api.robot para obter listas @{api_*} e ${oper_*}
    base_api_data = parse_base_api(base_api_path)
    api_arrays = base_api_data.get("api_arrays", [])
    oper_vars = base_api_data.get("oper_vars", [])

    # 2. Match do api_slug contra as listas @{api_*}
    api_mapping = match_api_slug(api_slug, api_arrays)

    # 3. Determinar o grupo de primeiro nivel (a partir do primeiro request)
    group = "Sem grupo"
    if requests:
        raw_group = get_top_level_group(requests[0].get("group", ""))
        group = normalize_for_group(raw_group)

    # 4. Construir cada test case
    test_cases = []
    for i, req in enumerate(requests, 1):
        tc = build_test_case(req, i, oper_vars)
        test_cases.append(tc)

    # 5. Montar o manifest completo
    manifest = {
        "file_name": file_name,
        "tipo": tipo,
        "collection_name": collection_name,
        "api_slug": api_slug,
        "group": group,
        "api_mapping": api_mapping,
        "test_cases": test_cases,
    }

    # 6. Adicionar checksum ao manifest (idempotencia)
    manifest_com_checksum = add_checksum_to_manifest(manifest)

    # 7. Serializar e escrever o arquivo .manifest.json
    manifest_file_name = file_name.replace(".robot", ".manifest.json")
    manifest_path = os.path.join(output_dir, manifest_file_name)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_com_checksum, f, ensure_ascii=False, indent=2)

    return manifest_path