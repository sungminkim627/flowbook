import click
from .io import load_flowbook, save_flowbook
from .executor import execute_flowbook

@click.group()
def cli():
    pass

@cli.command()
@click.argument("path")
@click.option("--node", help="Node to execute", required=True)
def run(path, node):
    flowbook = load_flowbook(path)
    execute_flowbook(flowbook, node)
    save_flowbook(flowbook, path)

if __name__ == "__main__":
    cli()
