# -*- coding: utf-8 -*-
"""This module provides the ANG CLI."""

from pathlib import Path
from typing import List, Optional

import typer

from ang import ERROR_STRINGS, __app_name__, __version__, ang, config
from ang.database import database

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
            f'Creating config file failed with "{ERROR_STRINGS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))

    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERROR_STRINGS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    else:
        typer.secho(
            f"The ang database is stored at\n{db_path}", fg=typer.colors.GREEN
        )


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


def _list_all_names() -> None:
    """List all first names."""

    namer = get_namer()

    name_list = namer.get_name_list()

    if len(name_list) == 0:
        typer.secho(
            "There are no names in the name database yet",
            fg=typer.colors.MAGENTA,
        )
        raise typer.Exit()

    typer.secho("\nName list:\n", fg=typer.colors.BLUE, bold=True)

    columns = (
        "Index.  ",
        "| Name                  ",
        "| Prevalence  ",
    )

    headers = "".join(columns)

    typer.secho(headers, fg=typer.colors.BLUE, bold=True)

    typer.secho("-" * len(headers), fg=typer.colors.BLUE)

    for id, name_entry in enumerate(name_list, 1):

        name, prevalence = name_entry.values()

        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {name}{(len(columns[1]) - len(name) - 2) * ' '}"
            f"| {prevalence}",
            fg=typer.colors.BLUE,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)


def _list_all_surnames() -> None:
    """List all surnames."""

    namer = get_namer()

    surname_list = namer.get_surname_list()

    if len(surname_list) == 0:
        typer.secho(
            "There are no surnames in the name database yet",
            fg=typer.colors.MAGENTA,
        )
        raise typer.Exit()

    typer.secho("\nSurname list:\n", fg=typer.colors.BLUE, bold=True)

    columns = (
        "Index.  ",
        "| Surname               ",
        "| Prevalence  ",
    )

    headers = "".join(columns)

    typer.secho(headers, fg=typer.colors.BLUE, bold=True)

    typer.secho("-" * len(headers), fg=typer.colors.BLUE)

    for id, surname_entry in enumerate(surname_list, 1):

        surname, prevalence = surname_entry.values()

        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {surname}{(len(columns[1]) - len(surname) - 2) * ' '}"
            f"| {prevalence}",
            fg=typer.colors.BLUE,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)


@app.command()
def add_name(
    name_input: List[str] = typer.Argument(...),
    prevalence: int = typer.Option(10, "--prevalence", "-p", min=1, max=10),
) -> None:
    """Add a new name with a prevalence (between 1-10, optional)."""
    namer = get_namer()
    name_entry, response = namer.add_name(name_input, prevalence)
    if response:
        typer.secho(
            f'Adding name failed with "{ERROR_STRINGS[response]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""First name: "{name_entry['name']}" was added """
            f"""with prevalence: {name_entry['prevalence']}""",
            fg=typer.colors.GREEN,
        )


@app.command()
def add_surname(
    surname_input: List[str] = typer.Argument(...),
    prevalence: int = typer.Option(10, "--prevalence", "-p", min=1, max=10),
) -> None:
    """Add a new surname with a prevalence (between 1-10, optional)."""
    namer = get_namer()
    surname_entry, response = namer.add_surname(surname_input, prevalence)
    if response:
        typer.secho(
            f'Adding surname failed with "{ERROR_STRINGS[response]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""Surname: "{surname_entry['surname']}" was added """
            f"""with prevalence: {surname_entry['prevalence']}""",
            fg=typer.colors.GREEN,
        )


@app.command()
def list_names() -> None:
    _list_all_names()


@app.command()
def list_surnames() -> None:
    _list_all_surnames()


@app.command()
def list_all() -> None:
    _list_all_names()
    _list_all_surnames()


@app.command(name="set_prevalence")
def set_prevalence(
    name_index: int = typer.Argument(...),
    new_prevalence: int = typer.Argument(..., min=1, max=10),
) -> None:
    """Set a name's prevalence using its Index."""

    namer = get_namer()

    name_entry, response = namer.set_name_prevalence(
        name_index, new_prevalence
    )

    if response:
        typer.secho(
            f'Setting prevalence on name # "{name_index}" failed with "{ERROR_STRINGS[response]}"',
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
def remove_name(
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
        name_entry, response = namer.remove_name_by_idx(name_idx)
        if response:

            typer.secho(
                f'Removing name # {name_idx} failed with "{ERROR_STRINGS[response]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

        else:
            typer.secho(
                f"""Name # {name_idx}: '{name_entry["name"]}' was removed""",
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
            f"Delete name # {name_idx}: {name_entry['name']}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")


@app.command()
def remove_surname(
    surname_idx: int = typer.Argument(...),
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
        surname_entry, response = namer.remove_surname_by_idx(surname_idx)
        if response:

            typer.secho(
                f'Removing surname # {surname_idx} failed with "{ERROR_STRINGS[response]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

        else:
            typer.secho(
                f"""Name # {surname_idx}: '{surname_entry["surname"]}' was removed""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        surname_list = namer.get_surname_list()
        try:
            surname_entry = surname_list[surname_idx - 1]
        except IndexError:
            typer.secho("Invalid surname index", fg=typer.colors.RED)
            raise typer.Exit(1)

        delete = typer.confirm(
            f"Delete surname # {surname_idx}: {surname_entry['surname']}?"
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
        response = namer.remove_all_names().response

        if response:
            typer.secho(
                f'Removing names failed with "{ERROR_STRINGS[response]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho("All names were removed", fg=typer.colors.GREEN)

    else:
        typer.echo("Operation canceled")


@app.command(name="generate")
def generate(
    number: int = typer.Option(
        1,
        "--number",
        "-n",
    )
):

    namer = get_namer()

    generated_names = namer.generate_random_name_surname(number)

    if len(generated_names) == 0:
        typer.secho(
            f"There are no names/surnames in database",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    for gen_name in generated_names:
        typer.secho(f"{gen_name}", fg=typer.colors.BLUE)

    raise typer.Exit()


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
