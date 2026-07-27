"""Validator pos-geracao: valida arquivos .robot apos o subagente preencher.

Script autônomo que valida o resultado do subagente LLM:
1. Sintaxe Robot (secoes obrigatorias)
2. Mapeamentos @{api_*} e ${oper_*} contra base-api.robot
3. Arquivos JSON (schemas e payloads) validos
4. Completude de test cases (vs manifest)

Uso:
    python validator.py --output output/
"""

import os
import sys
import click

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.validator_service import validate_all


@click.command()
@click.option("--output", "output_dir", required=True, help="Diretorio de saida com os arquivos .robot gerados")
@click.option("--base-resource", "base_api_path",
              default=None,
              help="Caminho para o base-api.robot (padrao: .opencode/context/resource/base-api.robot)")
def main(output_dir, base_api_path):
    """Valida arquivos .robot gerados apos o preenchimento pelo subagente.

    Executa validacoes deterministicas de sintaxe, mapeamentos, JSONs e
    completude. Imprime o relatorio no stdout e retorna exit code 0 (sucesso)
    ou 1 (falha).
    """
    if base_api_path is None:
        base_api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            ".opencode", "context", "resource", "base-api.robot"
        )

    click.echo("=" * 60)
    click.echo("Postman-to-Robot - Validator")
    click.echo("=" * 60)
    click.echo()

    if not os.path.exists(output_dir):
        click.echo(f"Erro: diretorio de saida nao encontrado: {output_dir}")
        sys.exit(1)

    if not os.path.exists(base_api_path):
        click.echo(f"Erro: base-api.robot nao encontrado: {base_api_path}")
        sys.exit(1)

    click.echo(f"Validando: {output_dir}")
    click.echo(f"Base API:  {base_api_path}")
    click.echo()

    report = validate_all(output_dir, base_api_path)

    # Imprime validacoes que passaram
    for p in report["passed"]:
        click.echo(f"  [OK] {p}")

    # Imprime warnings
    for w in report["warnings"]:
        click.echo(f"  [WARN] {w}")

    # Imprime erros
    for e in report["errors"]:
        click.echo(f"  [ERRO] {e}")

    # Resumo
    click.echo()
    click.echo("---")
    click.echo(f"Resumo: {len(report['passed'])} OK, {report['summary']['total_errors']} erros, {report['summary']['total_warnings']} avisos")
    click.echo(f"Arquivos validados: {report['summary']['total_files']}")

    if report["summary"]["total_errors"] > 0:
        click.echo()
        click.echo("VALIDACAO FALHOU")
        sys.exit(1)
    else:
        click.echo()
        click.echo("VALIDACAO OK")
        sys.exit(0)


if __name__ == "__main__":
    main()