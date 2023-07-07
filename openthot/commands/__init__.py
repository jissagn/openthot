import typer

from openthot.commands import run

cli = typer.Typer(name="openthot")


# cli.add_typer(cache.cache, "cache")
# cli.add_typer(config.config, name="config")
# cli.add_typer(devserver.devserver, "devserver")
# cli.add_typer(docs.docs, "docs")
cli.add_typer(run.run, name="run")
# cli.add_typer(routes_command, "routes")


# @cli.command()
# def version():
#     """
#     Shows the version of the project.
#     """
#     click.echo(f"{__version__} ({__build__})")


if __name__ == "__main__":
    typer.run(cli)
