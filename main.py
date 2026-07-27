"""Postman-to-Robot: Gerador de Esqueleto Robot Framework a partir de Postman Collections.

FLUXO:
  1. Script Python (este): Parseia collection, gera esqueleto .robot + manifest JSON
     e extrai schemas/payloads deterministicamente
  2. Agente opencode (robot-test-writer): Preenche Keywords, mapeia
      variaveis do base-api.robot, adiciona validacoes e schemas
  3. Validator Python: Valida o resultado apos o subagente preencher
"""

import os
import sys
import click

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.parser import parse_collection
from service.generator import generate_robot
from service.extractor import extract_all


@click.command()
@click.option("--input", "input_file", required=True, help="Caminho para o arquivo da collection Postman (JSON)")
@click.option("--output", "output_dir", required=True, help="Diretorio de saida para os arquivos .robot")
def main(input_file, output_dir):
    """Gerador de esqueleto Robot Framework a partir de collections Postman.

    Gera a estrutura deterministica do .robot, manifests JSON com dados
    estruturados e extrai schemas/payloads. Keywords e logica nao-deterministica
    sao preenchidas pelos agentes opencode.
    """
    click.echo("=" * 60)
    click.echo("Postman-to-Robot - Gerador de Esqueleto")
    click.echo("=" * 60)
    click.echo()

    click.echo("[1/3] Parseando collection...")
    data = parse_collection(input_file)

    collection_name = data["collection_name"]
    variables = data["variables"]
    requests = data["requests"]

    click.echo(f"  Collection: {collection_name}")
    click.echo(f"  Variaveis da collection: {len(variables)}")
    click.echo(f"  Requests validos: {len(requests)}")
    click.echo()

    click.echo("[2/3] Gerando esqueleto .robot + manifest JSON...")
    files = generate_robot(data, output_dir)

    robot_files = [f for f in files if f.endswith(".robot")]
    manifest_files = [f for f in files if f.endswith(".manifest.json")]

    click.echo()
    click.echo(f"  {len(robot_files)} arquivos .robot gerados")
    click.echo(f"  {len(manifest_files)} manifests JSON gerados")
    for f in files:
        click.echo(f"  - {os.path.basename(f)}")
    click.echo()

    click.echo("[3/3] Extraindo schemas e payloads...")
    resultado_extracao = extract_all(data, output_dir)

    click.echo(f"  Payloads extraidos: {len(resultado_extracao['payloads'])}")
    click.echo(f"  Schemas extraidos: {len(resultado_extracao['schemas'])}")

    if resultado_extracao["payloads"]:
        for p in resultado_extracao["payloads"]:
            click.echo(f"  - resources/{p['file_name']}")

    if resultado_extracao["schemas"]:
        for s in resultado_extracao["schemas"]:
            click.echo(f"  - schemas/{s['file_name']}")

    click.echo()
    click.echo("Proximo passo: executar o orquestrador opencode para")
    click.echo("preencher keywords, validacoes e schemas via LLM.")
    click.echo("Apos o subagente, executar: python validator.py --output <output_dir>")
    click.echo("Done!")


if __name__ == "__main__":
    main()
