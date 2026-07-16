"""This module provides the ANG CLI."""

from pathlib import Path
from typing import List, Optional

import typer

from ang import NAME_GENDERS, __app_name__, __version__, ang, config, presenter
from ang.database import database

app = typer.Typer(no_args_is_help=True)


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
        presenter.exit_with_error(
            "Creating config file failed with", app_init_error
        )

    db_init_error = database.init_database(Path(db_path))

    if db_init_error:
        presenter.exit_with_error(
            "Creating database failed with", db_init_error
        )

    else:
        presenter.success(f"The ang database is stored at\n{db_path}")


def get_namer() -> ang.Namer:

    if config.CONFIG_FILE_PATH.exists():
        try:
            db_path = config.get_database_path(config.CONFIG_FILE_PATH)
        except KeyError:
            presenter.error('Config file is invalid. Please, run "ang init"')
            raise typer.Exit(1)
    else:
        presenter.error('Config file not found. Please, run "ang init"')
        raise typer.Exit(1)

    if db_path.exists():
        return ang.Namer(db_path)
    else:
        presenter.error('Database not found. Please, run "ang init"')
        raise typer.Exit(1)


def _normalize_cli_name_gender(gender: str) -> str:
    normalized_gender = str(gender).lower()
    if normalized_gender not in NAME_GENDERS:
        presenter.error("Gender must be one of: " + ", ".join(NAME_GENDERS))
        raise typer.Exit(1)
    return normalized_gender


def _list_all_names(gender: Optional[str] = None) -> None:
    """List all first names."""

    namer = get_namer()
    normalized_gender = None

    if gender is not None:
        normalized_gender = _normalize_cli_name_gender(gender)

    name_response = namer.get_name_list()

    if name_response.response:
        presenter.exit_with_error(
            "Reading names failed with", name_response.response
        )

    if normalized_gender is not None:
        filtered_name_list = [
            name_entry
            for name_entry in name_response.name_list
            if name_entry["gender"] == normalized_gender
        ]

        presenter.list_entries(
            filtered_name_list,
            f"{normalized_gender.title()} name list",
            "Name",
            "name",
            f"There are no {normalized_gender} names in the name database yet",
            [("Gender", "gender", 8)],
        )
        return

    if len(name_response.name_list) == 0:
        presenter.list_entries(
            name_response.name_list,
            "Name list",
            "Name",
            "name",
            "There are no names in the name database yet",
            [("Gender", "gender", 8)],
        )
        return

    for name_gender in NAME_GENDERS:
        gender_name_list = [
            name_entry
            for name_entry in name_response.name_list
            if name_entry["gender"] == name_gender
        ]
        presenter.list_entries(
            gender_name_list,
            f"{name_gender.title()} name list",
            "Name",
            "name",
            f"There are no {name_gender} names in the name database yet",
            [("Gender", "gender", 8)],
            exit_on_empty=False,
        )


def _list_all_surnames() -> None:
    """List all surnames."""

    namer = get_namer()
    surname_response = namer.get_surname_list()

    if surname_response.response:
        presenter.exit_with_error(
            "Reading surnames failed with", surname_response.response
        )

    presenter.list_entries(
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
    gender: Optional[str] = typer.Option(
        None,
        "--gender",
        "-g",
        help="Name gender: man, woman, or neutral.",
    ),
) -> None:
    """Add a new name with a prevalence (between 1-10, optional)."""
    if gender is None:
        gender = typer.prompt("Gender")

    normalized_gender = _normalize_cli_name_gender(gender)

    namer = get_namer()
    name_entry, response = namer.add_name(
        name_input, prevalence, normalized_gender
    )
    if response:
        presenter.exit_with_error("Adding name failed with", response)
    else:
        presenter.success(
            f"""First name: "{name_entry["name"]}" was added """
            f"""with prevalence: {name_entry["prevalence"]} """
            f"""and gender: {name_entry["gender"]}"""
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
        presenter.exit_with_error("Adding surname failed with", response)
    else:
        presenter.success(
            f"""Surname: "{surname_entry["surname"]}" was added """
            f"""with prevalence: {surname_entry["prevalence"]}"""
        )


@app.command()
def list_names(
    gender: Optional[str] = typer.Option(
        None,
        "--gender",
        "-g",
        help="Only list names with this exact gender.",
    ),
) -> None:
    """List all stored names."""

    _list_all_names(gender)


@app.command()
def list_surnames() -> None:
    """List all stored surnames."""

    _list_all_surnames()


@app.command()
def list_all(
    gender: Optional[str] = typer.Option(
        None,
        "--gender",
        "-g",
        help="Only list names with this exact gender.",
    ),
) -> None:
    """List all stored names and surnames."""

    _list_all_names(gender)
    _list_all_surnames()


@app.command(name="set-name-prevalence")
def set_name_prevalence(
    name_identifier: str = typer.Argument(...),
    new_prevalence: int = typer.Argument(..., min=1, max=10),
) -> None:
    """Set a name's prevalence using its index or value."""

    namer = get_namer()

    name_entry, response = namer.set_name_prevalence(
        name_identifier, new_prevalence
    )

    if response:
        presenter.exit_with_error(
            f'Setting prevalence on name "{name_identifier}" failed with',
            response,
        )

    else:
        presenter.success(
            f"Success: Set prevalence ({name_entry['prevalence']}) "
            f'on name "{name_entry["name"]}"'
        )


@app.command(name="set-surname-prevalence")
def set_surname_prevalence(
    surname_identifier: str = typer.Argument(...),
    new_prevalence: int = typer.Argument(..., min=1, max=10),
) -> None:
    """Set a surname's prevalence using its index or value."""

    namer = get_namer()

    surname_entry, response = namer.set_surname_prevalence(
        surname_identifier, new_prevalence
    )

    if response:
        presenter.exit_with_error(
            "Setting prevalence on surname "
            f'"{surname_identifier}" failed with',
            response,
        )

    else:
        presenter.success(
            f"Success: Set prevalence ({surname_entry['prevalence']}) "
            f'on surname "{surname_entry["surname"]}"'
        )


@app.command(name="set-name-gender")
def set_name_gender(
    name_identifier: str = typer.Argument(...),
    new_gender: str = typer.Argument(...),
) -> None:
    """Set a name's gender using its index or value."""

    normalized_gender = _normalize_cli_name_gender(new_gender)
    namer = get_namer()

    name_entry, response = namer.set_name_gender(
        name_identifier, normalized_gender
    )

    if response:
        presenter.exit_with_error(
            f'Setting gender on name "{name_identifier}" failed with',
            response,
        )

    else:
        presenter.success(
            f"Success: Set gender ({name_entry['gender']}) "
            f'on name "{name_entry["name"]}"'
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
            presenter.exit_with_error(
                f"Removing name {name_identifier} failed with", response
            )

        else:
            presenter.success(
                f"""Name '{name_entry["name"]}' was removed""",
            )

    if force:
        _remove()
    else:
        name_entry, response = namer.get_name(name_identifier)
        if response:
            presenter.exit_with_error(
                f"Removing name {name_identifier} failed with", response
            )

        delete = presenter.confirm(f"Delete name: {name_entry['name']}?")
        if delete:
            _remove()
        else:
            presenter.canceled()


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
            presenter.exit_with_error(
                f"Removing surname {surname_identifier} failed with", response
            )

        else:
            presenter.success(
                f"""Surname '{surname_entry["surname"]}' was removed""",
            )

    if force:
        _remove()
    else:
        surname_entry, response = namer.get_surname(surname_identifier)
        if response:
            presenter.exit_with_error(
                f"Removing surname {surname_identifier} failed with", response
            )

        delete = presenter.confirm(
            f"Delete surname: {surname_entry['surname']}?"
        )
        if delete:
            _remove()
        else:
            presenter.canceled()


@app.command(name="remove-all")
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
            presenter.exit_with_error(
                "Removing names and surnames failed with", response
            )
        else:
            presenter.success("All names and surnames were removed")

    else:
        presenter.canceled()


@app.command(name="db-heal")
def db_heal(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Write missing default database values without confirmation.",
    ),
) -> None:
    """Write missing default values to the database."""

    if not force:
        heal = presenter.confirm("Write missing default values to database?")
        if not heal:
            presenter.canceled()
            return

    namer = get_namer()
    heal_response = namer.heal_database()

    if heal_response.response:
        presenter.exit_with_error(
            "Healing database failed with", heal_response.response
        )

    presenter.success(
        "Database healed; "
        f"{heal_response.changed_entries} missing name gender value(s) added"
    )


@app.command(name="generate")
def generate(
    number: int = typer.Option(
        1,
        "--number",
        "-n",
        min=1,
    ),
):
    """Generate random name and surname combinations."""

    namer = get_namer()

    generated_names = namer.generate_random_name_surname(number)

    if len(generated_names) == 0:
        presenter.error("There are no names/surnames in database")
        raise typer.Exit(1)

    for gen_name in generated_names:
        presenter.generated_name(gen_name)

    raise typer.Exit()


def _version_callback(value: bool) -> None:
    if value:
        presenter.plain(f"{__app_name__} v{__version__}")
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
    ),
) -> None:
    return
