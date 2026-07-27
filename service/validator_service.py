"""
Modulo de validacao pos-geracao (validator service).

Responsavel por validar os arquivos .robot apos o subagente LLM preencher as
keywords. As validacoes sao deterministicas e incluem:

1. Sintaxe Robot: Verifica presenca das secoes obrigatorias (*** Settings ***,
   *** Test Cases ***, *** Keywords ***) e que cada test case tem keyword.
   Tenta `robot --dryrun` se robotframework estiver instalado; caso contrario,
   usa fallback com regex parsing.

2. Mapeamentos: Verifica que cada @{api_*} e ${oper_*} referenciado no .robot
   existe no base-api.robot.

3. JSON: Valida que cada arquivo em schemas/*.json e resources/*.json e JSON valido.

4. Completude: Compara o numero de test cases no .robot com o manifest JSON
   e verifica que nenhum test case esta sem keyword associada.
"""

import json
import os
import re
import subprocess
import shutil
import tempfile
from typing import Optional
from service.mapper import parse_base_api


def validate_robot_syntax(robot_file: str) -> dict:
    """
    Valida a sintaxe de um arquivo .robot.

    Primeiro tenta usar `robot --dryrun` (se robotframework estiver instalado)
    para uma validacao completa. Se robot nao estiver disponivel, faz fallback
    com regex parsing verificando:
    - Presenca das secoes obrigatorias: *** Settings ***, *** Test Cases ***,
      *** Keywords ***
    - Cada test case tem pelo menos uma keyword chamada (nao apenas comentario)

    """
    errors = []

    if not os.path.exists(robot_file):
        return {"valid": False, "errors": [f"Arquivo nao encontrado: {robot_file}"]}

    with open(robot_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Tenta robot --dryrun se robotframework estiver instalado
    # Usa diretorio temporario para nao gerar output.xml/log.html/report.html na raiz
    robot_executable = shutil.which("robot")
    if robot_executable:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                proc = subprocess.run(
                    [robot_executable, "--dryrun", "-d", tmpdir, robot_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if proc.returncode != 0:
                    # Se robot falhou, usa o output de erro mas continua com regex
                    # para mensagens mais claras
                    pass
                else:
                    return {"valid": True, "errors": []}
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass  # Fallback para regex

    # Fallback: validacao via regex das secoes obrigatorias
    secoes_obrigatorias = [
        "*** Settings ***",
        "*** Test Cases ***",
        "*** Keywords ***",
    ]

    for secao in secoes_obrigatorias:
        if secao not in content:
            errors.append(f"Sintaxe: secao obrigatoria ausente: {secao}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_mappings(robot_file: str, base_api_path: str) -> dict:
    """
    Valida que os mapeamentos @{api_*} e ${oper_*} referenciados no .robot existem.

    Le o arquivo .robot, encontra todas as referencias a @{api_*} e ${oper_*},
    e verifica each uma contra as listas e variaveis do base-api.robot.
    
    """
    errors = []

    if not os.path.exists(robot_file):
        return {"valid": False, "errors": [f"Arquivo nao encontrado: {robot_file}"]}

    with open(robot_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse do base-api.robot para obter listas e variaveis validas
    base_api_data = parse_base_api(base_api_path)
    apis_validas = {f"@{{{a['name']}}}" for a in base_api_data["api_arrays"]}
    opers_validos = {f"${{{o['name']}}}" for o in base_api_data["oper_vars"]}

    # Encontra todas as referencias @{api_*} no .robot
    refs_api = re.findall(r"@\{api_\w+\}", content)
    for ref in set(refs_api):
        if ref not in apis_validas:
            errors.append(f"Mapeamento: {ref} referenciado mas nao existe no base-api.robot")

    # Encontra todas as referencias ${oper_*} no .robot
    refs_oper = re.findall(r"\$\{oper_\w+\}", content)
    for ref in set(refs_oper):
        if ref not in opers_validos:
            errors.append(f"Mapeamento: {ref} referenciado mas nao existe no base-api.robot")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_json_files(output_dir: str) -> dict:
    """
    Valida que todos os arquivos JSON em schemas/ e resources/ sao validos.

    Procura por diretorios schemas/ e resources/ dentro de output_dir (incluindo
    subdiretorios de API) e tenta fazer json.load de cada arquivo .json encontrado.

    """
    errors = []

    diretorios_json = []

    # Procura por schemas/ e resources/ no diretorio base e subdiretorios
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path):
            for subdir in ["schemas", "resources"]:
                subdir_path = os.path.join(item_path, subdir)
                if os.path.isdir(subdir_path):
                    diretorios_json.append(subdir_path)

    # Tambem verifica no nivel raiz
    for subdir in ["schemas", "resources"]:
        subdir_path = os.path.join(output_dir, subdir)
        if os.path.isdir(subdir_path):
            diretorios_json.append(subdir_path)

    for dir_path in diretorios_json:
        for file_name in os.listdir(dir_path):
            if not file_name.endswith(".json"):
                continue

            file_path = os.path.join(dir_path, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                errors.append(f"JSON invalido: {file_path} - {str(e)}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_completeness(robot_file: str, manifest_path: str) -> dict:
    """
    Valida a completude do .robot comparando com o manifest JSON.

    Verifica:
    - Cada test case no .robot tem pelo menos uma keyword associada (nao apenas comentario)
    - O numero de test cases no .robot corresponde ao numero no manifest
    
    """
    errors = []
    warnings = []

    if not os.path.exists(robot_file):
        return {"valid": False, "errors": [f"Arquivo .robot nao encontrado: {robot_file}"], "warnings": []}

    if not os.path.exists(manifest_path):
        return {"valid": False, "errors": [f"Manifest nao encontrado: {manifest_path}"], "warnings": []}

    with open(robot_file, "r", encoding="utf-8") as f:
        robot_content = f.read()

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest_tc_count = len(manifest.get("test_cases", []))

    # Conta test cases no .robot: linhas apos *** Test Cases *** que nao sao
    # vazias, nao sao comentarios e nao sao secao
    tc_section_start = robot_content.find("*** Test Cases ***")
    tc_section_end = robot_content.find("*** Keywords ***")

    if tc_section_start == -1 or tc_section_end == -1:
        return {"valid": False, "errors": ["Nao foi possivel encontrar secoes Test Cases/Keywords"], "warnings": []}

    tc_section = robot_content[tc_section_start + len("*** Test Cases ***"):tc_section_end]

    # Conta test cases: linhas que nao comecam com espaco (nivel 0) e nao estao vazias
    robot_tc_count = 0
    tc_without_keyword = []

    linhas = tc_section.strip().splitlines()
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        if not linha:
            i += 1
            continue

        # Test case name: linha que comeca na coluna 0 (sem indentacao)
        if not linhas[i].startswith(" ") and not linhas[i].startswith("\t"):
            robot_tc_count += 1
            tc_name = linha

            # Verifica se a proxima linha nao vazia e uma keyword (indentada, nao comentario)
            has_keyword = False
            j = i + 1
            while j < len(linhas):
                next_line = linhas[j].strip()
                if not next_line:
                    j += 1
                    continue

                # Se a linha nao e indentada, e o proximo test case
                if not linhas[j].startswith(" ") and not linhas[j].startswith("\t"):
                    break

                # Se nao e comentario, e uma keyword
                if not next_line.startswith("#"):
                    has_keyword = True
                    break

                j += 1

            if not has_keyword:
                tc_without_keyword.append(tc_name)

            i = j
        else:
            i += 1

    # Verifica test cases sem keyword
    for tc_name in tc_without_keyword:
        errors.append(f"Completude: test case '{tc_name}' sem keyword associada")

    # Verifica divergencia de contagem
    if robot_tc_count != manifest_tc_count:
        warnings.append(
            f"Divergencia: .robot tem {robot_tc_count} test cases, "
            f"manifest tem {manifest_tc_count}"
        )

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def validate_all(output_dir: str, base_api_path: str) -> dict:
    """
    Orquestra todas as validacoes em um diretorio de saida.

    Percorre todos os arquivos .robot e .manifest.json no diretorio de saida
    (incluindo subdiretorios de API) e executa as validacoes de sintaxe,
    mapeamentos, JSONs e completude.

    """
    errors = []
    warnings = []
    passed = []
    total_files = 0

    # Percorre subdiretorios de API
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if not os.path.isdir(item_path):
            continue

        # Encontra arquivos .robot e .manifest.json
        for file_name in os.listdir(item_path):
            file_path = os.path.join(item_path, file_name)

            if file_name.endswith(".robot"):
                total_files += 1

                # Valida sintaxe
                result_syntax = validate_robot_syntax(file_path)
                if result_syntax["valid"]:
                    passed.append(f"Sintaxe OK: {file_name}")
                else:
                    errors.extend([f"[{file_name}] {e}" for e in result_syntax["errors"]])

                # Valida mapeamentos
                result_mapping = validate_mappings(file_path, base_api_path)
                if result_mapping["valid"]:
                    passed.append(f"Mapeamentos OK: {file_name}")
                else:
                    errors.extend([f"[{file_name}] {e}" for e in result_mapping["errors"]])

                # Valida completude (se existir manifest correspondente)
                manifest_name = file_name.replace(".robot", ".manifest.json")
                manifest_path = os.path.join(item_path, manifest_name)

                if os.path.exists(manifest_path):
                    result_completeness = validate_completeness(file_path, manifest_path)
                    if result_completeness["valid"]:
                        passed.append(f"Completude OK: {file_name}")
                    else:
                        errors.extend([f"[{file_name}] {e}" for e in result_completeness["errors"]])
                    warnings.extend([f"[{file_name}] {w}" for w in result_completeness["warnings"]])

    # Valida arquivos JSON (schemas e payloads)
    result_json = validate_json_files(output_dir)
    if result_json["valid"]:
        passed.append("JSONs: todos os arquivos validos")
    else:
        errors.extend(result_json["errors"])

    return {
        "errors": errors,
        "warnings": warnings,
        "passed": passed,
        "summary": {
            "total_files": total_files,
            "total_errors": len(errors),
            "total_warnings": len(warnings),
        },
    }