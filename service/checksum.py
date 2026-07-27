"""
Modulo de checksum (hash) para idempotencia do manifest JSON.

Responsavel por:
- Calcular um hash SHA-256 deterministico dos dados do manifest (ignorando
  o proprio campo checksum para evitar recursao)
- Adicionar o checksum ao manifest antes de serializar
- Verificar se o checksum no manifest coincide com o calculado
- Comparar um manifest novo com um existente para detectar se houve mudanca

Isso garante idempotencia: se o orquestrador reprocessar a mesma collection,
o checksum nao muda, e o orquestrador pode pular a regeneracao do .robot.

"""

import copy
import hashlib
import json
import os
from typing import Any


def _strip_checksum(data: dict) -> dict:
    """
    Remove o campo 'checksum' de uma copia do dicionario para calculo de hash.

    Isso evara recursao (o checksum nao pode ser parte do calculo do proprio checksum).

    """
    dados_limpos = copy.deepcopy(data)
    dados_limpos.pop("checksum", None)
    return dados_limpos


def calculate_checksum(data: dict) -> str:
    """
    Calcula um hash SHA-256 deterministico dos dados do manifest.

    O hash e calculado sobre a representacao JSON canonica dos dados (sem
    o campo checksum, com sort_keys=True para garantir determinismo).
    Isso significa que o mesmo manifest sempre gera o mesmo hash, permitindo
    detectar se os dados mudaram entre geracoes.

    """
    dados_limpos = _strip_checksum(data)

    # Serializa com sort_keys para garantir determinismo (mesma ordem de chaves)
    json_canonico = json.dumps(dados_limpos, sort_keys=True, ensure_ascii=False)

    return hashlib.sha256(json_canonico.encode("utf-8")).hexdigest()


def add_checksum_to_manifest(data: dict) -> dict:
    """
    Adiciona o campo "checksum" ao dicionario do manifest e retorna a copia.

    Calcula o hash dos dados (ignorando qualquer checksum existente) e adiciona
    o resultado como campo "checksum" no dicionario retornado. O dicionario
    original nao e modificado.

    """
    resultado = copy.deepcopy(data)
    resultado["checksum"] = calculate_checksum(data)
    return resultado


def verify_checksum(data: dict) -> bool:
    """
    Verifica se o checksum no manifest coincide com o calculado.

    Compara o valor do campo "checksum" no dicionario com o hash recalculado
    (ignorando o proprio checksum no calculo). Se os dados foram alterados
    apos o checksum ter sido gerado, a verificacao falha.

    """
    checksum_existente = data.get("checksum")
    if not checksum_existente:
        return False

    checksum_calculado = calculate_checksum(data)
    return checksum_existente == checksum_calculado


def has_manifest_changed(new_data: dict, manifest_path: str) -> bool:
    """
    Compara novos dados de manifest com um manifest existente no arquivo.

    Le o manifest do arquivo (se existir), extrai o checksum, calcula o
    checksum dos novos dados e compara. Se o arquivo nao existe, retorna
    True (primeira geracao). Se os checksums coincidem, retorna False (nao
    houve mudanca, o orquestrador pode pular a regeneracao).

    """
    if not os.path.exists(manifest_path):
        return True

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_existente = json.load(f)
    except (json.JSONDecodeError, OSError):
        return True

    checksum_existente = manifest_existente.get("checksum")
    if not checksum_existente:
        return True

    novo_checksum = calculate_checksum(new_data)
    return novo_checksum != checksum_existente