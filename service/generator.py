"""Gerador de arquivos .robot a partir de dados parseados."""


def generate_robot(parsed_data, output_dir, base_resource, environment):
    """Gera os arquivos .robot a partir dos dados parseados."""
    click.echo(f"Gerando arquivos em: {output_dir}")
