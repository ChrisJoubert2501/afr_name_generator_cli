"""This module provides the ANG model-controller."""

import random
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from ang import (
    GENDER_ERROR,
    GENERATE_GENDERS,
    NAME_GENDERS,
    NAME_IDX_ERROR,
    NAME_POOL_ERROR,
    SUCCESS,
    SURNAME_IDX_ERROR,
    SURNAME_POOL_ERROR,
)
from ang.database.database import DatabaseHandler


class CurrentName(NamedTuple):
    name: Dict[str, Any]
    response: int


class CurrentSurname(NamedTuple):
    surname: Dict[str, Any]
    response: int


class CurrentNameList(NamedTuple):
    name_list: List[Dict[str, Any]]
    response: int


class CurrentSurnameList(NamedTuple):
    surname_list: List[Dict[str, Any]]
    response: int


class DatabaseHeal(NamedTuple):
    changed_entries: int
    response: int


class GeneratedNames(NamedTuple):
    generated_names: List[str]
    response: int


class Namer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    @staticmethod
    def _to_list_index(entry_idx: int) -> int:
        if entry_idx < 1:
            raise IndexError
        return entry_idx - 1

    @staticmethod
    def _is_index_identifier(identifier: str) -> bool:
        return identifier.isdecimal()

    @classmethod
    def _get_entry_by_identifier(
        cls,
        entries: List[Dict[str, Any]],
        entry_key: str,
        identifier: str,
    ) -> Dict[str, Any]:
        identifier = str(identifier)

        if cls._is_index_identifier(identifier):
            return entries[cls._to_list_index(int(identifier))]

        normalized_identifier = identifier.title()

        for entry in entries:
            if entry[entry_key] == normalized_identifier:
                return entry

        raise IndexError

    @staticmethod
    def _normalize_name_gender(gender: str) -> str:
        normalized_gender = str(gender).lower()
        if normalized_gender not in NAME_GENDERS:
            raise ValueError
        return normalized_gender

    @staticmethod
    def _normalize_generate_gender(gender: str) -> str:
        normalized_gender = str(gender).lower()
        if normalized_gender not in GENERATE_GENDERS:
            raise ValueError
        return normalized_gender

    @staticmethod
    def _get_generation_name_pool(
        name_list: List[Dict[str, Any]], gender: str
    ) -> List[Dict[str, Any]]:
        if gender == "man":
            compatible_genders = ("man", "neutral")
        elif gender == "woman":
            compatible_genders = ("woman", "neutral")
        else:
            compatible_genders = ("neutral",)

        return [
            name_entry
            for name_entry in name_list
            if name_entry["gender"] in compatible_genders
        ]

    @staticmethod
    def _sample_entries(
        entries: List[Dict[str, Any]], number: int
    ) -> List[Dict[str, Any]]:
        return random.choices(
            entries,
            weights=[entry["prevalence"] for entry in entries],
            k=number,
        )

    def add_name(
        self, name_input: List[str], prevalence: int, gender: str
    ) -> CurrentName:
        """Add a new name to the database."""

        try:
            normalized_gender = self._normalize_name_gender(gender)
        except ValueError:
            return CurrentName({}, GENDER_ERROR)

        return self._add_entry_response(
            name_input,
            prevalence,
            "name",
            self._db_handler.add_name,
            CurrentName,
            {"gender": normalized_gender},
        )

    def _add_entry_response(
        self,
        entry_input: List[str],
        prevalence: int,
        entry_key: str,
        add_entry,
        response_type,
        extra_fields=None,
    ):
        entry = {
            entry_key: " ".join(entry_input),
            "prevalence": prevalence,
        }

        if extra_fields:
            entry.update(extra_fields)

        response = add_entry(entry)

        return response_type(entry, response.response_code)

    def get_name_list(self, gender: str = None) -> CurrentNameList:
        """Return the name list."""
        if gender is not None:
            try:
                gender = self._normalize_name_gender(gender)
            except ValueError:
                return CurrentNameList([], GENDER_ERROR)

        read = self._db_handler.read_names()

        if gender is not None:
            return CurrentNameList(
                [
                    name_entry
                    for name_entry in read.name_list
                    if name_entry["gender"] == gender
                ],
                read.response_code,
            )

        return CurrentNameList(read.name_list, read.response_code)

    def add_surname(
        self, surname_input: List[str], prevalence: int
    ) -> CurrentSurname:
        """Add a new surname to the database."""

        return self._add_entry_response(
            surname_input,
            prevalence,
            "surname",
            self._db_handler.add_surname,
            CurrentSurname,
        )

    def get_surname_list(self) -> CurrentSurnameList:
        """Return the surname list."""
        read = self._db_handler.read_surnames()
        return CurrentSurnameList(read.surname_list, read.response_code)

    def _set_entry_prevalence_response(
        self,
        entries: List[Dict[str, Any]],
        write_entries,
        entry_key: str,
        identifier: str,
        new_prevalence: int,
        error_code: int,
        response_type,
    ):
        entry, response = self._get_entry_response(
            entries, entry_key, identifier, error_code, response_type
        )

        if response:
            return response_type({}, response)

        entry["prevalence"] = new_prevalence
        write = write_entries(entries)

        return response_type(entry, write.response_code)

    def set_name_prevalence(
        self, name_identifier: str, new_prevalence: int
    ) -> CurrentName:
        """Set a prevalence on a name using its index or value."""

        read = self._db_handler.read_names()

        if read.response_code:
            return CurrentName({}, read.response_code)

        return self._set_entry_prevalence_response(
            read.name_list,
            self._db_handler.write_names,
            "name",
            name_identifier,
            new_prevalence,
            NAME_IDX_ERROR,
            CurrentName,
        )

    def set_surname_prevalence(
        self, surname_identifier: str, new_prevalence: int
    ) -> CurrentSurname:
        """Set a prevalence on a surname using its index or value."""

        read = self._db_handler.read_surnames()

        if read.response_code:
            return CurrentSurname({}, read.response_code)

        return self._set_entry_prevalence_response(
            read.surname_list,
            self._db_handler.write_surnames,
            "surname",
            surname_identifier,
            new_prevalence,
            SURNAME_IDX_ERROR,
            CurrentSurname,
        )

    def set_name_gender(
        self, name_identifier: str, new_gender: str
    ) -> CurrentName:
        """Set a gender on a name using its index or value."""

        try:
            normalized_gender = self._normalize_name_gender(new_gender)
        except ValueError:
            return CurrentName({}, GENDER_ERROR)

        read = self._db_handler.read_names()

        if read.response_code:
            return CurrentName({}, read.response_code)

        name_entry, response = self._get_entry_response(
            read.name_list,
            "name",
            name_identifier,
            NAME_IDX_ERROR,
            CurrentName,
        )

        if response:
            return CurrentName({}, response)

        name_entry["gender"] = normalized_gender
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

    def _get_entry_response(
        self,
        entries: List[Dict[str, Any]],
        entry_key: str,
        identifier: str,
        error_code: int,
        response_type,
    ):
        try:
            entry = self._get_entry_by_identifier(
                entries, entry_key, identifier
            )
        except IndexError:
            return response_type({}, error_code)

        return response_type(entry, SUCCESS)

    def _remove_entry_response(
        self,
        entries: List[Dict[str, Any]],
        write_entries,
        entry_key: str,
        identifier: str,
        error_code: int,
        response_type,
    ):
        entry, response = self._get_entry_response(
            entries, entry_key, identifier, error_code, response_type
        )

        if response:
            return response_type({}, response)

        try:
            entries.remove(entry)
        except ValueError:
            return response_type({}, error_code)

        write = write_entries(entries)

        return response_type(entry, write.response_code)

    def remove_name(self, name_identifier: str) -> CurrentName:
        """Remove a name from the database using its index or value."""
        read = self._db_handler.read_names()

        if read.response_code:
            return CurrentName({}, read.response_code)

        return self._remove_entry_response(
            read.name_list,
            self._db_handler.write_names,
            "name",
            name_identifier,
            NAME_IDX_ERROR,
            CurrentName,
        )

    def get_name(self, name_identifier: str) -> CurrentName:
        """Return a name using its index or value."""

        read = self._db_handler.read_names()

        if read.response_code:
            return CurrentName({}, read.response_code)

        return self._get_entry_response(
            read.name_list,
            "name",
            name_identifier,
            NAME_IDX_ERROR,
            CurrentName,
        )

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

    def remove_surname(self, surname_identifier: str) -> CurrentSurname:
        """Remove a surname from the database using its index or value."""
        read = self._db_handler.read_surnames()

        if read.response_code:
            return CurrentSurname({}, read.response_code)

        return self._remove_entry_response(
            read.surname_list,
            self._db_handler.write_surnames,
            "surname",
            surname_identifier,
            SURNAME_IDX_ERROR,
            CurrentSurname,
        )

    def get_surname(self, surname_identifier: str) -> CurrentSurname:
        """Return a surname using its index or value."""

        read = self._db_handler.read_surnames()

        if read.response_code:
            return CurrentSurname({}, read.response_code)

        return self._get_entry_response(
            read.surname_list,
            "surname",
            surname_identifier,
            SURNAME_IDX_ERROR,
            CurrentSurname,
        )

    def remove_all(self) -> CurrentName:
        """Remove all first names and surnames from the database."""
        write = self._db_handler.write_database({"names": [], "surnames": []})
        return CurrentName({}, write.response_code)

    def heal_database(self) -> DatabaseHeal:
        """Write inferred missing database values."""
        heal = self._db_handler.heal_database()
        return DatabaseHeal(heal.changed_entries, heal.response_code)

    def generate_random_name_surname(
        self, number: int, gender: str = "mixed"
    ) -> GeneratedNames:
        """Generates names"""
        try:
            normalized_gender = self._normalize_generate_gender(gender)
        except ValueError:
            return GeneratedNames([], GENDER_ERROR)

        names_read = self._db_handler.read_names()
        surnames_read = self._db_handler.read_surnames()

        if names_read.response_code:
            return GeneratedNames([], names_read.response_code)

        if surnames_read.response_code:
            return GeneratedNames([], surnames_read.response_code)

        if not surnames_read.surname_list:
            return GeneratedNames([], SURNAME_POOL_ERROR)

        if normalized_gender == "mixed":
            man_name_pool = self._get_generation_name_pool(
                names_read.name_list, "man"
            )
            woman_name_pool = self._get_generation_name_pool(
                names_read.name_list, "woman"
            )

            if not man_name_pool or not woman_name_pool:
                return GeneratedNames([], NAME_POOL_ERROR)

            sampled_surnames = self._sample_entries(
                surnames_read.surname_list, number
            )

            generated_names = []
            for surname_entry in sampled_surnames:
                selected_gender = random.choice(("man", "woman"))
                name_pool = (
                    man_name_pool
                    if selected_gender == "man"
                    else woman_name_pool
                )
                name_entry = self._sample_entries(name_pool, 1)[0]
                generated_names.append(
                    f"{name_entry['name']} {surname_entry['surname']}"
                )

            return GeneratedNames(generated_names, SUCCESS)

        name_pool = self._get_generation_name_pool(
            names_read.name_list, normalized_gender
        )

        if not name_pool:
            return GeneratedNames([], NAME_POOL_ERROR)

        sampled_names = self._sample_entries(name_pool, number)
        sampled_surnames = self._sample_entries(
            surnames_read.surname_list, number
        )

        generated_names = []
        for name_entry, surname_entry in zip(sampled_names, sampled_surnames):
            generated_names.append(
                f"{name_entry['name']} {surname_entry['surname']}"
            )

        return GeneratedNames(generated_names, SUCCESS)
