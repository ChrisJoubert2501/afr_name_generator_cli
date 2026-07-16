"""Presentation helpers for the ANG CLI."""

from typing import Any, Dict, List

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
