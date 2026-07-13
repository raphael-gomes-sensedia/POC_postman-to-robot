"""Postman-to-Robot: Gerador de Esqueleto Robot Framework a partir de Postman Collections.

FLUXO:
  1. Script Python (este): Parseia collection e gera esqueleto .robot
     (Settings, Variables, nomes de Test Cases, Keywords vazias)
  2. Agente opencode (robot-test-writer): Preenche Keywords, mapeia
     variaveis do base-api.robot, adiciona validacoes e schemas
"""

import os
import sys
import click

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.parser import parse_collection
from service.generator import generate_robot


@click.command()
@click.option("--input", "input_file", required=True, help="Caminho para o arquivo da collection Postman (JSON)")
@click.option("--output", "output_dir", required=True, help="Diretorio de saida para os arquivos .robot")
def main(input_file, output_dir):
    """Gerador de esqueleto Robot Framework a partir de collections Postman.

    Gera a estrutura deterministica do .robot. Keywords e logica
    nao-deterministica sao preenchidas pelos agentes opencode.
    """
    click.echo("=" * 60)
    click.echo("Postman-to-Robot - Gerador de Esqueleto")
    click.echo("=" * 60)
    click.echo()

    click.echo("[1/2] Parseando collection...")
    data = parse_collection(input_file)

    collection_name = data["collection_name"]
    variables = data["variables"]
    requests = data["requests"]

    click.echo(f"  Collection: {collection_name}")
    click.echo(f"  Variaveis da collection: {len(variables)}")
    click.echo(f"  Requests validos: {len(requests)}")
    click.echo()

    click.echo("[2/2] Gerando esqueleto .robot...")
    files = generate_robot(data, output_dir)

    click.echo()
    click.echo(f"{len(files)} esqueletos gerados em: {output_dir}")
    for f in files:
        click.echo(f"  - {os.path.basename(f)}")

    click.echo()
    click.echo("Proximo passo: executar o orquestrador opencode para")
    click.echo("preencher keywords, validacoes e schemas via LLM.")
    click.echo("Done!")


if __name__ == "__main__":
    main()
