"""Presentation helpers for the ANG CLI."""

from typing import Any, Dict, List, Tuple

import typer

from ang import ERROR_STRINGS


def get_error_message(response: int) -> str:
    return ERROR_STRINGS.get(response, "unknown error")


def exit_with_error(message: str, response: int) -> None:
    typer.secho(
        f'{message} "{get_error_message(response)}"',
        fg=typer.colors.RED,
    )
    raise typer.Exit(1)


def error(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED)


def plain(message: str) -> None:
    typer.echo(message)


def success(message: str) -> None:
    typer.secho(message, fg=typer.colors.GREEN)


def generated_name(name: str) -> None:
    typer.secho(name, fg=typer.colors.BLUE)


def canceled() -> None:
    typer.echo("Operation canceled")


def confirm(message: str) -> bool:
    return typer.confirm(message)


def list_entries(
    entries: List[Dict[str, Any]],
    title: str,
    value_label: str,
    value_key: str,
    empty_message: str,
    extra_columns: List[Tuple[str, str, int]] = None,
    exit_on_empty: bool = True,
) -> None:
    if len(entries) == 0:
        typer.secho(
            empty_message,
            fg=typer.colors.MAGENTA,
        )
        if exit_on_empty:
            raise typer.Exit()
        return

    typer.secho(f"\n{title}:\n", fg=typer.colors.BLUE, bold=True)

    table_columns = [
        ("Index.", "_index", 6),
        (value_label, value_key, 22),
        *(extra_columns or []),
        ("Prevalence", "prevalence", 10),
    ]

    headers = " | ".join(
        f"{label:<{width}}" for label, _, width in table_columns
    )

    typer.secho(headers, fg=typer.colors.BLUE, bold=True)

    typer.secho("-" * len(headers), fg=typer.colors.BLUE)

    for index, entry in enumerate(entries, 1):
        row_values = []
        for _, entry_key, width in table_columns:
            if entry_key == "_index":
                value = str(index)
            else:
                value = str(entry[entry_key])
            row_values.append(f"{value:<{width}}")

        typer.secho(
            " | ".join(row_values),
            fg=typer.colors.BLUE,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)
