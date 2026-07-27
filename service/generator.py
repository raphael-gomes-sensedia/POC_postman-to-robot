"""Gerador de esqueleto de arquivos .robot a partir de dados parseados.

Responsavel por (parte deterministica):
- Separar requests por grupo de primeiro nivel
- Separar requests de sucesso e erro por status code
- Gerar as secoes Settings, Variables e nomes de Test Cases
- Gerar esqueleto vazio de Keywords (preenchido posteriormente pela LLM)
"""

import os
import re
import unicodedata

from service.manifest import generate_manifest_file


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

    name = re.sub(r'\s*v\d+(\.\d+)*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^API\s+', '', name, flags=re.IGNORECASE)

    name = name.strip().lower().replace(" ", "-")
    name = re.sub(r'[^a-z0-9-]', '', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip("-")

    return name


def extract_status_code(name):
    """Extrai o status code do nome do teste."""
    match = re.search(r"\[(\d{3})\]", name)
    if match:
        return match.group(1)
    return None


def is_error_status(status_code):
    """Verifica se o status code indica erro (4xx ou 5xx)."""
    if not status_code:
        return False
    try:
        code = int(status_code)
        return 400 <= code < 600
    except ValueError:
        return False


def generate_documentation(requests, collection_name, tipo, file_name, api_slug):
    """Gera a secao Documentation multi-linha."""
    lines = []
    lines.append(f"Documentation    {collection_name} - {tipo}")

    seen = set()
    for req in requests:
        test_name = req["name"]
        if test_name not in seen:
            seen.add(test_name)
            lines.append(f"...              - {test_name}")

    lines.append(f"...")
    lines.append(f"...        command to run tests:")
    lines.append(f"...        robot -d results\\{api_slug}\\{file_name} {file_name}")

    return "\n".join(lines)


def generate_settings(requests, collection_name, tipo, file_name, api_slug):
    """Gera a secao *** Settings *** do arquivo .robot."""
    lines = []
    lines.append("*** Settings ***")
    lines.append(generate_documentation(requests, collection_name, tipo, file_name, api_slug))
    lines.append("")
    lines.append("Resource        ../api-tests/base-api.robot")
    lines.append("")
    return "\n".join(lines)


def generate_variables(collection_variables):
    """Gera secao *** Variables *** com as variaveis da collection."""
    lines = []
    lines.append("*** Variables ***")

    for key, value in collection_variables.items():
        if not value:
            continue
        lines.append(f"${{{key}}}    {value}")

    lines.append("")
    return "\n".join(lines)


def generate_robot_file(requests, collection_name, variables, tipo, file_name, api_slug):
    """Gera o esqueleto de um arquivo .robot.
    
    """
    sections = []

    sections.append(generate_settings(requests, collection_name, tipo, file_name, api_slug))

    sections.append(generate_variables(variables))

    sections.append("*** Test Cases ***")
    for i, req in enumerate(requests, 1):
        seq_str = f"T{i:02d}"
        test_name = f"{seq_str} - {collection_name} - {req['name']}"
        sections.append(test_name)
        sections.append(f"    # Keyword sera inserida pelo agente LLM")
        sections.append("")

    sections.append("*** Keywords ***")
    sections.append("# Keywords serao inseridas pelo agente LLM com base no contexto")
    sections.append("# do base-api.robot e nos padroes do time")
    sections.append("")

    return "\n".join(sections) + "\n"


def generate_robot(data, output_dir, base_api_path=None):
    """Gera os arquivos .robot (esqueleto) a partir dos dados parseados.

    Cria uma subpasta com o nome da API dentro de output_dir.
    Dentro dela, dois arquivos por grupo:
      - {grupo}.robot (apenas testes de sucesso)
      - neg-{grupo}.robot (apenas testes de erro)

    Para cada arquivo .robot gerado, tambem gera um arquivo .manifest.json
    sidecar com os dados estruturados das requests, assertions traduzidas e
    mapeamentos sugeridos de @{api_*} e ${oper_*}.

    """
    collection_name = data.get("collection_name", "Sem nome")
    variables = data.get("variables", {})
    requests = data.get("requests", [])

    if not requests:
        return []

    # Caminho padrao do base-api.robot se nao fornecido
    if base_api_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_api_path = os.path.join(
            project_root, ".opencode", "context", "resource", "base-api.robot"
        )

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
                "sucesso", file_name, api_slug
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            files_created.append(file_path)
            print(f"Esqueleto gerado: {file_path} ({len(success_reqs)} testes de sucesso)")

            # Gera o manifest JSON sidecar
            manifest_path = generate_manifest_file(
                requests=success_reqs,
                collection_name=collection_name,
                variables=variables,
                tipo="sucesso",
                file_name=file_name,
                api_slug=api_slug,
                base_api_path=base_api_path,
                output_dir=output_dir,
            )
            files_created.append(manifest_path)

        if error_reqs:
            file_name = generate_file_name(group_name, prefix="neg-")
            file_path = os.path.join(output_dir, file_name)

            content = generate_robot_file(
                error_reqs, collection_name, variables,
                "erro", file_name, api_slug
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            files_created.append(file_path)
            print(f"Esqueleto gerado: {file_path} ({len(error_reqs)} testes de erro)")

            # Gera o manifest JSON sidecar
            manifest_path = generate_manifest_file(
                requests=error_reqs,
                collection_name=collection_name,
                variables=variables,
                tipo="erro",
                file_name=file_name,
                api_slug=api_slug,
                base_api_path=base_api_path,
                output_dir=output_dir,
            )
            files_created.append(manifest_path)

    return files_created
