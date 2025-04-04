from pathlib import Path
from typing import Optional
import typer
from . import __app_name__, __version__
from pythonutils.goodreads_csv_to_json import GoodReadsCsvToJson

from pythonutils import ERRORS, __app_name__, __version__, config


app = typer.Typer()

@app.command()
def goodreads_csv(
) -> None:
    typer.secho(f"Running Goodreads script!")
    goodreads = GoodReadsCsvToJson()
    goodreads.run()

@app.command()
def choose_command(
    command: str = typer.Option(
        str("Command"),
        "--command",
        "-c",
        prompt="""
What command do you want to run?
  1) GoodReads script
  2) There is no 2
""",
    ),
) -> None:
        typer.secho(f"You typed: '{command}' ({type(command)})")
        match command:
            case "1":
                typer.secho(f"You selected command GoodReads", fg=typer.colors.GREEN)
                goodreads = GoodReadsCsvToJson()
                goodreads.run()
                return
            case "2":
                  typer.secho(f"I said there is no number 2!", fg=typer.colors.GREEN)
                  return
            case _:
                "Sorry!"
                return

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return