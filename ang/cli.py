# -*- coding: utf-8 -*-
"""This module provides the ANG CLI."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from ang import ERROR_STRINGS, __app_name__, __version__, ang, config
from ang.database import database

app = typer.Typer()


def _get_error_message(response: int) -> str:
    return ERROR_STRINGS.get(response, "unknown error")


def _exit_with_error(message: str, response: int) -> None:
    typer.secho(
        f'{message} "{_get_error_message(response)}"',
        fg=typer.colors.RED,
    )
    raise typer.Exit(1)


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
        _exit_with_error("Creating config file failed with", app_init_error)

    db_init_error = database.init_database(Path(db_path))

    if db_init_error:
        _exit_with_error("Creating database failed with", db_init_error)

    else:
        typer.secho(
            f"The ang database is stored at\n{db_path}", fg=typer.colors.GREEN
        )


def get_namer() -> ang.Namer:

    if config.CONFIG_FILE_PATH.exists():
        try:
            db_path = config.get_database_path(config.CONFIG_FILE_PATH)
        except KeyError:
            typer.secho(
                'Config file is invalid. Please, run "ang init"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
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


def _list_entries(
    entries: List[Dict[str, Any]],
    title: str,
    value_label: str,
    value_key: str,
    empty_message: str,
) -> None:
    if len(entries) == 0:
        typer.secho(
            empty_message,
            fg=typer.colors.MAGENTA,
        )
        raise typer.Exit()

    typer.secho(f"\n{title}:\n", fg=typer.colors.BLUE, bold=True)

    columns = (
        "Index.  ",
        f"| {value_label:<22}",
        "| Prevalence  ",
    )

    headers = "".join(columns)

    typer.secho(headers, fg=typer.colors.BLUE, bold=True)

    typer.secho("-" * len(headers), fg=typer.colors.BLUE)

    for index, entry in enumerate(entries, 1):

        value = entry[value_key]
        prevalence = entry["prevalence"]

        typer.secho(
            f"{index}{(len(columns[0]) - len(str(index))) * ' '}"
            f"| {value}{(len(columns[1]) - len(value) - 2) * ' '}"
            f"| {prevalence}",
            fg=typer.colors.BLUE,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)


def _list_all_names() -> None:
    """List all first names."""

    namer = get_namer()
    name_response = namer.get_name_list()

    if name_response.response:
        _exit_with_error("Reading names failed with", name_response.response)

    _list_entries(
        name_response.name_list,
        "Name list",
        "Name",
        "name",
        "There are no names in the name database yet",
    )


def _list_all_surnames() -> None:
    """List all surnames."""

    namer = get_namer()
    surname_response = namer.get_surname_list()

    if surname_response.response:
        _exit_with_error(
            "Reading surnames failed with", surname_response.response
        )

    _list_entries(
        surname_response.surname_list,
        "Surname list",
        "Surname",
        "surname",
        "There are no surnames in the name database yet",
    )


@app.command()
def add_name(
    name_input: List[str] = typer.Argument(...),
    prevalence: int = typer.Option(10, "--prevalence", "-p", min=1, max=10),
) -> None:
    """Add a new name with a prevalence (between 1-10, optional)."""
    namer = get_namer()
    name_entry, response = namer.add_name(name_input, prevalence)
    if response:
        _exit_with_error("Adding name failed with", response)
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
        _exit_with_error("Adding surname failed with", response)
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


@app.command(name="set-prevalence")
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
        _exit_with_error(
            f'Setting prevalence on name # "{name_index}" failed with',
            response,
        )

    else:
        typer.secho(
            f"""Success: Set prevalence ({name_entry['prevalence']}) on name # {name_index}"""
            f""" "{name_entry['name']}" """,
            fg=typer.colors.GREEN,
        )


@app.command()
def remove_name(
    name_identifier: str = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a name using its index or value."""
    namer = get_namer()

    def _remove():
        name_entry, response = namer.remove_name(name_identifier)
        if response:

            _exit_with_error(
                f"Removing name {name_identifier} failed with", response
            )

        else:
            typer.secho(
                f"""Name '{name_entry["name"]}' was removed""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        name_entry, response = namer.get_name(name_identifier)
        if response:
            _exit_with_error(
                f"Removing name {name_identifier} failed with", response
            )

        delete = typer.confirm(f"Delete name: {name_entry['name']}?")
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")


@app.command()
def remove_surname(
    surname_identifier: str = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a surname using its index or value."""
    namer = get_namer()

    def _remove():
        surname_entry, response = namer.remove_surname(surname_identifier)
        if response:

            _exit_with_error(
                f"Removing surname {surname_identifier} failed with", response
            )

        else:
            typer.secho(
                f"""Surname '{surname_entry["surname"]}' was removed""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        surname_entry, response = namer.get_surname(surname_identifier)
        if response:
            _exit_with_error(
                f"Removing surname {surname_identifier} failed with", response
            )

        delete = typer.confirm(f"Delete surname: {surname_entry['surname']}?")
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")


@app.command(name="clear")
def remove_all(
    force: bool = typer.Option(
        ...,
        prompt="Delete all names and surnames?",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove all names and surnames."""

    namer = get_namer()

    if force:
        response = namer.remove_all().response

        if response:
            _exit_with_error("Removing names and surnames failed with", response)
        else:
            typer.secho(
                "All names and surnames were removed", fg=typer.colors.GREEN
            )

    else:
        typer.echo("Operation canceled")


@app.command(name="generate")
def generate(
    number: int = typer.Option(
        1,
        "--number",
        "-n",
        min=1,
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
