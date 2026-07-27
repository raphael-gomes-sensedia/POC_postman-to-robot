"""
Modulo de mapeamento (mapper) entre dados da collection Postman e o base-api.robot.

Responsavel por:
- Parsear o arquivo base-api.robot e extrair as listas @{api_*} e variaveis ${oper_*}
- Fazer fuzzy matching entre o slug da API da collection e os slugs das listas @{api_*}
- Fazer fuzzy matching entre o path da URL das requests e os paths das variaveis ${oper_*}

"""

import os
import re
import unicodedata
from typing import Optional
from urllib.parse import urlparse


def normalize(text: str) -> str:
    """
    Normaliza texto para comparacao de similaridade.

    Remove acentos, converte para minusculas, substitui underscores por hifens
    e remove espacos extras. Esta transformacao garante que "Gestão_Pedidos"
    e "gestao-pedidos" sejam tratados como iguais durante o matching.

    Parametros:
        text (str): Texto a ser normalizado.

    Retorna:
        str: Texto normalizado sem acentos, em minusculas, com hifens.
    """
    if not text:
        return ""

    texto = unicodedata.normalize("NFKD", text)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower().replace("_", "-")
    texto = texto.strip()

    return texto


def token_overlap(str1: str, str2: str) -> float:
    """
    Calcula a similaridade entre duas strings baseada em overlap de tokens.

    Divide cada string em tokens (usando hifens e espacos como separadores),
    conta quantos tokens estao em comum e divide pelo maior numero de tokens.
    Retorna um valor entre 0.0 (sem tokens em comum) e 1.0 (todos os tokens em comum).

    """
    norm1 = normalize(str1)
    norm2 = normalize(str2)

    if not norm1 or not norm2:
        return 0.0

    tokens1 = set(re.split(r"[- ]", norm1))
    tokens2 = set(re.split(r"[- ]", norm2))

    tokens1.discard("")
    tokens2.discard("")

    if not tokens1 or not tokens2:
        return 0.0

    intersecao = tokens1 & tokens2
    max_tokens = max(len(tokens1), len(tokens2))

    return len(intersecao) / max_tokens if max_tokens > 0 else 0.0


def parse_base_api(file_path: str) -> dict:
    """
    Parseia o arquivo base-api.robot e extrai listas @{api_*} e variaveis ${oper_*}.

    O formato do base-api.robot segue o padrao Robot Framework para variaveis:
        ${oper_pedidos}     /pedidos
        @{api_conecta_pedidos}     conecta-pedidos    v1.4    v1.4

    Para listas @{api_*}, extrai:
    - name: nome da lista sem @{ e } (ex: "api_conecta_pedidos")
    - slug: valor da segunda coluna (ex: "conecta-pedidos")
    - version_dev: valor da terceira coluna (ex: "v1.4")
    - version_hml: valor da quarta coluna (ex: "v1.4")

    Para variaveis ${oper_*}, extrai:
    - name: nome da variavel sem ${ e } (ex: "oper_pedidos")
    - path: valor do path (ex: "/pedidos")

    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        conteudo = f.read()

    api_arrays = []
    oper_vars = []

    # Regex para extrair listas @{api_*}: capture o nome e os valores em coluna
    # Ex: @{api_conecta_pedidos}     conecta-pedidos    v1.4    v1.4
    padrao_api = re.compile(
        r"@{api_(\w+)}\s+(\S+)\s+(v\S+)\s+(v\S+)"
    )

    # Regex para extrair variaveis ${oper_*}: capture o nome e o path
    # Ex: ${oper_pedidos}     /pedidos
    padrao_oper = re.compile(
        r"\$\{oper_(\w+)\}\s+(\S+)"
    )

    for linha in conteudo.splitlines():
        linha = linha.strip()

        # Ignora linhas vazias, comentarios e cabecalhos
        if not linha or linha.startswith("#") or linha.startswith("###"):
            continue

        # Tenta extrair lista @{api_*}
        match_api = padrao_api.search(linha)
        if match_api:
            api_arrays.append({
                "name": f"api_{match_api.group(1)}",
                "slug": match_api.group(2),
                "version_dev": match_api.group(3),
                "version_hml": match_api.group(4),
            })
            continue

        # Tenta extrair variavel ${oper_*}
        match_oper = padrao_oper.search(linha)
        if match_oper:
            oper_vars.append({
                "name": f"oper_{match_oper.group(1)}",
                "path": match_oper.group(2),
            })

    return {
        "api_arrays": api_arrays,
        "oper_vars": oper_vars,
    }


def match_api_slug(api_slug: str, api_arrays: list) -> dict:
    """
    Faz fuzzy matching entre o slug da API da collection e os slugs das listas @{api_*}.

    Compara o api_slug (gerado por generate_api_slug a partir do nome da collection)
    contra o campo "slug" de cada item em api_arrays usando token_overlap e matching
    por substring.

    """
    if not api_slug or not api_arrays:
        return {"best_match": None, "alternatives": []}

    candidatos = []
    norm_slug = normalize(api_slug)

    for arr in api_arrays:
        arr_slug = arr.get("slug", "")
        norm_arr = normalize(arr_slug)

        # Calcula confidence usando token_overlap
        confidence = token_overlap(api_slug, arr_slug)

        # Bonus de confidence se ha substring direta
        if norm_arr and norm_slug:
            if norm_slug in norm_arr or norm_arr in norm_slug:
                confidence = max(confidence, 0.7)

        if confidence > 0:
            candidatos.append({
                "array": f"@{{{arr['name']}}}",
                "slug": arr_slug,
                "confidence": round(confidence, 2),
            })

    # Ordena por confidence decrescente
    candidatos.sort(key=lambda c: c["confidence"], reverse=True)

    if not candidatos:
        return {"best_match": None, "alternatives": []}

    return {
        "best_match": candidatos[0],
        "alternatives": candidatos[1:],
    }


def _extract_path_from_url(url: str) -> str:
    """
    Extrai apenas o path de uma URL completa, ignorando protocolo, dominio e query string.

    Ex: "https://api.example.com/dev/conecta-pedidos/v1/pedidos?pagina=1"
        -> "/dev/conecta-pedidos/v1/pedidos"

    """
    if not url:
        return ""

    parsed = urlparse(url)
    path = parsed.path

    if not path:
        # Se urlparse nao conseguir extrair o path (URL sem protocolo),
        # tenta split manual
        sem_query = url.split("?")[0]
        if "://" in sem_query:
            path = sem_query.split("/", 3)[-1] if sem_query.count("/") >= 3 else ""
            if path:
                path = "/" + path
        else:
            path = sem_query

    return path or ""


def match_path(url: str, oper_vars: list) -> dict:
    """
    Faz fuzzy matching entre o path da URL da request e as variaveis ${oper_*}.

    Extrai o path da URL (ignorando protocolo, dominio e query string) e verifica
    qual variavel ${oper_*} tem o path que aparece como substring no path da URL.

    """
    if not url or not oper_vars:
        return {"best_match": None, "alternatives": []}

    url_path = _extract_path_from_url(url)

    if not url_path:
        return {"best_match": None, "alternatives": []}

    candidatos = []

    for oper in oper_vars:
        oper_path = oper.get("path", "")

        if not oper_path:
            continue

        # Verifica se o path do ${oper_*} aparece como substring no path da URL
        if oper_path in url_path:
            # Confidence baseada em quao especifico e o match
            # (path maior = mais especifico = confidence maior)
            confidence = len(oper_path) / len(url_path) if len(url_path) > 0 else 0.5
            confidence = min(confidence, 1.0)

            candidatos.append({
                "var": f"${{{oper['name']}}}",
                "path": oper_path,
                "confidence": round(confidence, 2),
            })

    # Ordena por confidence decrescente (path mais especifico primeiro)
    candidatos.sort(key=lambda c: c["confidence"], reverse=True)

    if not candidatos:
        return {"best_match": None, "alternatives": []}

    return {
        "best_match": candidatos[0],
        "alternatives": candidatos[1:],
    }