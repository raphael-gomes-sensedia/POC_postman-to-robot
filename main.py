"""Postman-to-Robot: Gerador de Testes Robot Framework a partir de Postman Collections."""

import os
import sys
import click

# Adiciona o diretorio raiz ao path para importar os modulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.parser import parse_collection
from service.generator import generate_robot


@click.command()
@click.option("--input", "input_file", required=True, help="Caminho para o arquivo da collection Postman (JSON)")
@click.option("--output", "output_dir", required=True, help="Diretorio de saida para os arquivos .robot")
@click.option("--base-resource", "base_resource", default="../test-base/base-api.robot", help="Caminho para o base-api.robot")
@click.option("--env", "environment", default="dev", help="Ambiente (dev, hml)")
@click.option("--ai-api", "ai_api", default="opencode", help="Provedor de IA (opencode, openai)")
@click.option("--ai-model", "ai_model", default="opencode/oci", help="Modelo de IA")
def main(input_file, output_dir, base_resource, environment, ai_api, ai_model):
    """Gerador de testes Robot Framework a partir de collections Postman."""
    click.echo("=" * 60)
    click.echo("Postman-to-Robot - Gerador de Testes")
    click.echo("=" * 60)
    click.echo()

    # Fase 1: Parsear a collection
    click.echo("[1/2] Parseando collection...")
    data = parse_collection(input_file)

    collection_name = data["collection_name"]
    variables = data["variables"]
    requests = data["requests"]

    click.echo(f"  Collection: {collection_name}")
    click.echo(f"  Variaveis: {len(variables)}")
    click.echo(f"  Requests: {len(requests)}")
    click.echo()

    # Fase 2: Gerar arquivos .robot
    click.echo("[2/2] Gerando arquivos .robot...")
    files = generate_robot(data, output_dir, base_resource, environment)

    click.echo()
    click.echo(f"{len(files)} arquivos gerados em: {output_dir}")
    click.echo()
    for f in files:
        click.echo(f"  - {os.path.basename(f)}")

    click.echo()
    click.echo("Done!")


if __name__ == "__main__":
    main()
