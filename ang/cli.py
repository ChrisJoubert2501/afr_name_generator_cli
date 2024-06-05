# -*- coding: utf-8 -*-
"""This module provides the ANG CLI."""

from pathlib import Path
from typing import List, Optional

import typer

from ang import ERRORS, __app_name__, __version__, ang, config, database

app = typer.Typer()


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="ang database location?",
    ),
) -> None:
    """Initialize the ang database."""

    app_init_error = config.init_app(db_path)

    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))

    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    else:
        typer.secho(f"The ang database is {db_path}", fg=typer.colors.GREEN)


def get_namer() -> ang.Namer:

    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "ang init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if db_path.exists():
        return ang.Namer(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "ang init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


@app.command()
def add(
    first_name: List[str] = typer.Argument(...),
    prevalence: int = typer.Option(2, "--prevalence", "-p", min=1, max=10),
) -> None:
    """Add a new name with a prevalence (between 1-10, optional)."""
    namer = get_namer()
    name_entry, error = namer.add(first_name, prevalence)
    if error:
        typer.secho(
            f'Adding name failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""First name: "{name_entry['first_name']}" was added """
            f"""with prevalence: {name_entry['prevalence']}""",
            fg=typer.colors.GREEN,
        )


@app.command(name="list")
def list_all() -> None:
    """List all first names."""

    namer = get_namer()

    name_list = namer.get_name_list()

    if len(name_list) == 0:
        typer.secho(
            "There are no names in the name database yet",
            fg=typer.colors.MAGENTA,
        )
        raise typer.Exit()

    typer.secho("\nname list:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
        "Index.  ",
        "| First Name            ",
        "| Prevalence  ",
    )

    headers = "".join(columns)

    typer.secho(headers, fg=typer.colors.BLUE, bold=True)

    typer.secho("-" * len(headers), fg=typer.colors.BLUE)

    for id, name in enumerate(name_list, 1):

        first_name, prevalence = name.values()

        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {first_name}{(len(columns[1]) - len(first_name) - 2) * ' '}"
            f"| {prevalence}",
            fg=typer.colors.BLUE,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)


@app.command(name="set_prevalence")
def set_prevalence(
    name_index: int = typer.Argument(...),
    new_prevalence: int = typer.Argument(..., min=1, max=10),
) -> None:
    """Set a name's prevalence using its Index."""

    namer = get_namer()

    name_entry, error = namer.set_prevalence(name_index, new_prevalence)

    if error:
        typer.secho(
            f'Setting prevalence on name # "{name_index}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    else:
        typer.secho(
            f"""Success: Set prevalence ({name_entry['prevalence']}) on name # {name_index}"""
            f""" "{name_entry['first_name']}" """,
            fg=typer.colors.GREEN,
        )


@app.command()
def remove(
    name_idx: int = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a name using its index."""
    namer = get_namer()

    def _remove():
        name_entry, error = namer.remove(name_idx)
        if error:

            typer.secho(
                f'Removing name # {name_idx} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

        else:
            typer.secho(
                f"""Name # {name_idx}: '{name_entry["first_name"]}' was removed""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        name_list = namer.get_name_list()
        try:
            name_entry = name_list[name_idx - 1]
        except IndexError:
            typer.secho("Invalid name index", fg=typer.colors.RED)
            raise typer.Exit(1)

        delete = typer.confirm(
            f"Delete name # {name_idx}: {name_entry['first_name']}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")


@app.command(name="clear")
def remove_all(
    force: bool = typer.Option(
        ...,
        prompt="Delete all names?",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove all names."""

    namer = get_namer()

    if force:
        error = namer.remove_all().error

        if error:
            typer.secho(
                f'Removing names failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho("All names were removed", fg=typer.colors.GREEN)

    else:
        typer.echo("Operation canceled")


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
