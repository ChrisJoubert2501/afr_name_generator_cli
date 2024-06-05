# -*- coding: utf-8 -*-

"""This module provides the ANG model-controller."""

from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from ang import DB_READ_ERROR, NAME_IDX_ERROR
from ang.database import DatabaseHandler


class CurrentName(NamedTuple):
    name: Dict[str, Any]
    error: int


class Namer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, first_name: List[str], prevalence: int = 5) -> CurrentName:
        """Add a new name to the database."""

        first_name_text = " ".join(first_name)

        entry = {
            "first_name": first_name_text,
            "prevalence": prevalence,
        }

        read = self._db_handler.read_names()

        if read.error == DB_READ_ERROR:
            return CurrentName(entry, read.error)

        read.name_list.append(entry)
        write = self._db_handler.write_names(read.name_list)

        return CurrentName(entry, write.error)

    def get_name_list(self) -> List[Dict[str, Any]]:
        """Return the name list."""
        read = self._db_handler.read_names()
        return read.name_list

    def set_prevalence(
        self, name_idx: int, new_prevalence: int
    ) -> CurrentName:
        """Set a prevalence on a name."""

        read = self._db_handler.read_names()

        if read.error:
            return CurrentName({}, read.error)

        try:
            name_entry = read.name_list[name_idx - 1]
        except IndexError:
            return CurrentName({}, NAME_IDX_ERROR)

        name_entry["prevalence"] = new_prevalence
        write = self._db_handler.write_names(read.name_list)

        return CurrentName(name_entry, write.error)

    def remove(self, name_idx: int) -> CurrentName:
        """Remove a name from the database using its id or index."""

        read = self._db_handler.read_names()

        if read.error:
            return CurrentName({}, read.error)
        try:
            name_entry = read.name_list.pop(name_idx - 1)
        except IndexError:
            return CurrentName({}, NAME_IDX_ERROR)

        write = self._db_handler.write_names(read.name_list)

        return CurrentName(name_entry, write.error)

    def remove_all(self) -> CurrentName:
        """Remove all names from the database."""
        write = self._db_handler.write_names([])
        return CurrentName({}, write.error)
