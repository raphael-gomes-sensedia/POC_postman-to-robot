"""Postman-to-Robot: Gerador de Testes Robot Framework a partir de Postman Collections."""

import click


@click.command()
@click.option("--input", "input_file", default="/input", help="Caminho para o arquivo da collection Postman (JSON)")
@click.option("--output", "output_dir", default="/output", help="Diretório de saída para os arquivos .robot")
@click.option("--base-resource", "base_resource", default="/test-base/base-api.robot", help="Caminho para o base-api.robot")
@click.option("--env", "environment", default="dev", help="Ambiente (dev, hml)")
@click.option("--ai-api", "ai_api", default="opencode", help="Provedor de IA (opencode, openai)")
@click.option("--ai-model", "ai_model", default="opencode/oci", help="Modelo de IA")
def main(input_file, output_dir, base_resource, environment, ai_api, ai_model):
    """Gerador de testes Robot Framework a partir de collections Postman."""
    click.echo(f"Input: {input_file}")
    click.echo(f"Output: {output_dir}")
    click.echo(f"Base Resource: {base_resource}")
    click.echo(f"Environment: {environment}")
    click.echo(f"AI API: {ai_api}")
    click.echo(f"AI Model: {ai_model}")
    click.echo("Hello World - POC Gerador de Testes Robot Framework")


if __name__ == "__main__":
    main()
