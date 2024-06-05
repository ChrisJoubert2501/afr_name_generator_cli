# -*- coding: utf-8 -*-

"""This module provides the ANG model-controller."""

import random
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from ang import DB_READ_ERROR, NAME_IDX_ERROR, SURNAME_IDX_ERROR
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

    def add_name(self, name_input: List[str], prevalence: int) -> CurrentName:
        """Add a new name to the database."""

        name_text = " ".join(name_input)

        entry = {
            "name": name_text,
            "prevalence": prevalence,
        }

        read = self._db_handler.read_names()

        if read.response_code == DB_READ_ERROR:
            return CurrentName(entry, read.response_code)

        read.name_list.append(entry)
        write = self._db_handler.write_names(read.name_list)

        return CurrentName(entry, write.response_code)

    def get_name_list(self) -> List[Dict[str, Any]]:
        """Return the name list."""
        read = self._db_handler.read_names()
        return read.name_list

    def add_surname(
        self, surname_input: List[str], prevalence: int
    ) -> CurrentName:
        """Add a new surname to the database."""

        surname_text = " ".join(surname_input)

        entry = {
            "surname": surname_text,
            "prevalence": prevalence,
        }

        read = self._db_handler.read_surnames()

        if read.response_code == DB_READ_ERROR:
            return CurrentSurname(entry, read.response_code)

        read.surname_list.append(entry)
        write = self._db_handler.write_surnames(read.surname_list)

        return CurrentSurname(entry, write.response_code)

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
            name_entry = read.name_list[name_idx - 1]
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
            name_entry = read.name_list.pop(name_idx - 1)
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
            surname_entry = read.surname_list.pop(surname_idx - 1)
        except IndexError:
            return CurrentSurname({}, SURNAME_IDX_ERROR)

        write = self._db_handler.write_surnames(read.surname_list)

        return CurrentSurname(surname_entry, write.response_code)

    def remove_all_names(self) -> CurrentName:
        """Remove all names from the database."""
        write = self._db_handler.write_names([])
        return CurrentName({}, write.response_code)

    def generate_random_name_surname(self, number) -> List[str]:
        """Generates names"""
        names_read = self._db_handler.read_names()
        surnames_read = self._db_handler.read_surnames()

        if (
            len(names_read.name_list)
            == 0 | len(surnames_read.surname_list)
            == 0
        ):
            return []

        sampled_names = random.choices(names_read.name_list, k=number)
        sampled_surnames = random.choices(surnames_read.surname_list, k=number)

        generated_names = []
        for name_entry, surname_entry in zip(sampled_names, sampled_surnames):
            generated_names.append(
                f'{name_entry["name"]} {surname_entry["surname"]}'
            )

        return generated_names
