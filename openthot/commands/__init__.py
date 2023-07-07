import typer

from openthot.commands import run, standalone

cli = typer.Typer(name="openthot")


cli.add_typer(run.run, name="run")
cli.command()(standalone.standalone)

if __name__ == "__main__":
    typer.run(cli)
