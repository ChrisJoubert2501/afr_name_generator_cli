# -*- coding: utf-8 -*-

"""This module provides the ANG model-controller."""

import random
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from ang import NAME_IDX_ERROR, SURNAME_IDX_ERROR
from ang.database.database import DatabaseHandler


class CurrentName(NamedTuple):
    name: Dict[str, Any]
    response: int


class CurrentSurname(NamedTuple):
    surname: Dict[str, Any]
    response: int


class Namer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    @staticmethod
    def _to_list_index(entry_idx: int) -> int:
        if entry_idx < 1:
            raise IndexError
        return entry_idx - 1

    def add_name(self, name_input: List[str], prevalence: int) -> CurrentName:
        """Add a new name to the database."""

        name_text = " ".join(name_input)

        entry = {
            "name": name_text,
            "prevalence": prevalence,
        }

        response = self._db_handler.add_name(entry)

        return CurrentName(entry, response.response_code)

    def get_name_list(self) -> List[Dict[str, Any]]:
        """Return the name list."""
        read = self._db_handler.read_names()
        return read.name_list

    def add_surname(
        self, surname_input: List[str], prevalence: int
    ) -> CurrentSurname:
        """Add a new surname to the database."""

        surname_text = " ".join(surname_input)

        entry = {
            "surname": surname_text,
            "prevalence": prevalence,
        }

        response = self._db_handler.add_surname(entry)

        return CurrentSurname(entry, response.response_code)

    def get_surname_list(self) -> List[Dict[str, Any]]:
        """Return the name list."""
        read = self._db_handler.read_surnames()
        return read.surname_list

    def set_name_prevalence(
        self, name_idx: int, new_prevalence: int
    ) -> CurrentName:
        """Set a prevalence on a name."""

        read = self._db_handler.read_names()

        if read.response_code:
            return CurrentName({}, read.response_code)

        try:
            name_entry = read.name_list[self._to_list_index(name_idx)]
        except IndexError:
            return CurrentName({}, NAME_IDX_ERROR)

        name_entry["prevalence"] = new_prevalence
        write = self._db_handler.write_names(read.name_list)

        return CurrentName(name_entry, write.response_code)

    def remove_name_by_idx(self, name_idx: int) -> CurrentName:
        """Remove a name from the database using its index."""

        read = self._db_handler.read_names()

        if read.response_code:
            return CurrentName({}, read.response_code)
        try:
            name_entry = read.name_list.pop(self._to_list_index(name_idx))
        except IndexError:
            return CurrentName({}, NAME_IDX_ERROR)

        write = self._db_handler.write_names(read.name_list)

        return CurrentName(name_entry, write.response_code)

    def remove_surname_by_idx(self, surname_idx: int) -> CurrentSurname:
        """Remove a surname from the database using its index."""

        read = self._db_handler.read_surnames()

        if read.response_code:
            return CurrentSurname({}, read.response_code)
        try:
            surname_entry = read.surname_list.pop(
                self._to_list_index(surname_idx)
            )
        except IndexError:
            return CurrentSurname({}, SURNAME_IDX_ERROR)

        write = self._db_handler.write_surnames(read.surname_list)

        return CurrentSurname(surname_entry, write.response_code)

    def remove_all(self) -> CurrentName:
        """Remove all first names and surnames from the database."""
        write = self._db_handler.write_database({"names": [], "surnames": []})
        return CurrentName({}, write.response_code)

    def generate_random_name_surname(self, number: int) -> List[str]:
        """Generates names"""
        names_read = self._db_handler.read_names()
        surnames_read = self._db_handler.read_surnames()

        if not names_read.name_list or not surnames_read.surname_list:
            return []

        sampled_names = random.choices(
            names_read.name_list,
            weights=[entry["prevalence"] for entry in names_read.name_list],
            k=number,
        )
        sampled_surnames = random.choices(
            surnames_read.surname_list,
            weights=[entry["prevalence"] for entry in surnames_read.surname_list],
            k=number,
        )

        generated_names = []
        for name_entry, surname_entry in zip(sampled_names, sampled_surnames):
            generated_names.append(
                f'{name_entry["name"]} {surname_entry["surname"]}'
            )

        return generated_names
