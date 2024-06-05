# -*- coding: utf-8 -*-

"""This module provides the ANG database functionality."""

import configparser
import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, TypedDict

from schema import SchemaError

from ang import (
    ALREADY_EXISTS_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    SCHEMA_ERROR,
    SUCCESS,
)
from ang.database.presets.default_database import default_database_string
from ang.database.presets.empty_database import empty_database_string
from ang.database.schema import (
    ang_database_schema,
    name_entry_schema,
    surname_entry_schema,
)

DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_ang_database.json"
)


def get_database_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def init_database(db_path: Path) -> int:
    """Create the database."""
    try:
        default_database = json.loads(default_database_string)
        validated_database = ang_database_schema.validate(default_database)

        with db_path.open("w") as db:
            json.dump(validated_database, db, indent=4)
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    except SchemaError:
        return SCHEMA_ERROR


class NameEntry(TypedDict):
    name: str
    prevalence: int


class SurnameEntry(TypedDict):
    surname: str
    prevalence: int


class ANGDatabase(TypedDict):
    names: List[NameEntry]
    surnames: List[SurnameEntry]


class DBReadResponse(NamedTuple):
    database: ANGDatabase
    response_code: int


class DBNameResponse(NamedTuple):
    name_list: List[NameEntry]
    response_code: int


class DBSurnameResponse(NamedTuple):
    surname_list: List[SurnameEntry]
    response_code: int


class DBCRUDResponse(NamedTuple):
    response_code: int


class DatabaseHandler:

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_database(self) -> DBReadResponse:

        try:
            with self._db_path.open("r") as db:
                try:
                    database = json.load(db)
                    validated_database = ang_database_schema.validate(database)
                    return DBReadResponse(validated_database, SUCCESS)
                except json.JSONDecodeError:
                    empty_database = json.loads(empty_database_string)
                    return DBReadResponse(empty_database, JSON_ERROR)
                except SchemaError:
                    empty_database = json.loads(empty_database_string)
                    return DBReadResponse(empty_database, SCHEMA_ERROR)
        except OSError:
            # Catch file IO problems
            empty_database = json.loads(empty_database_string)
            return DBReadResponse(empty_database_string, DB_READ_ERROR)

    def write_database(self, database: ANGDatabase) -> DBCRUDResponse:

        database["names"].sort(key=lambda x: x["name"], reverse=False)
        database["surnames"].sort(key=lambda x: x["surname"], reverse=False)

        try:
            with self._db_path.open("w") as db:
                json.dump(database, db, indent=4)
            return DBCRUDResponse(SUCCESS)

        except OSError:
            # Catch file IO problems
            return DBCRUDResponse(DB_WRITE_ERROR)

    def read_names(self) -> DBNameResponse:
        database_read = self.read_database()

        return DBNameResponse(
            database_read.database["names"], database_read.response_code
        )

    def read_surnames(self) -> DBSurnameResponse:
        database_read = self.read_database()
        return DBSurnameResponse(
            database_read.database["surnames"], database_read.response_code
        )

    def write_names(self, name_list: List[Dict[str, Any]]) -> DBCRUDResponse:
        database_read = self.read_database()
        database = database_read.database

        database["names"] = sorted(
            name_list, key=lambda x: x["name"], reverse=False
        )

        database_write = self.write_database(database)

        return DBCRUDResponse(database_write.response_code)

    def add_name(
        self,
        name_entry,
    ) -> DBCRUDResponse:
        database_read = self.read_database()
        database = database_read.database

        name_entry["name"] = name_entry["name"].title()

        validated_name_entry = name_entry_schema.validate(name_entry)

        for existing_name_entry in database["names"]:
            if existing_name_entry["name"] == validated_name_entry["name"]:
                return DBCRUDResponse(ALREADY_EXISTS_ERROR)

        database["names"].append(validated_name_entry)
        database_write = self.write_database(database)

        return DBCRUDResponse(database_write.response_code)

    def write_surnames(
        self, surname_list: List[Dict[str, Any]]
    ) -> DBNameResponse:
        database_read = self.read_database()
        database = database_read.database

        database["surnames"] = sorted(
            surname_list, key=lambda x: x["surname"], reverse=False
        )

        database_write = self.write_database(database)

        return DBCRUDResponse(database_write.response_code)

    def add_surname(
        self,
        surname_entry,
    ) -> DBCRUDResponse:
        database_read = self.read_database()
        database = database_read.database

        surname_entry["surname"] = surname_entry["surname"].title()

        validated_surname_entry = surname_entry_schema.validate(surname_entry)

        for existing_name_entry in database["surnames"]:
            if (
                existing_name_entry["surname"]
                == validated_surname_entry["surname"]
            ):
                return DBCRUDResponse(ALREADY_EXISTS_ERROR)

        database["surnames"].append(validated_surname_entry)

        database_write = self.write_database(database)

        return DBCRUDResponse(database_write.response_code)
