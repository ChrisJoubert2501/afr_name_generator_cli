# -*- coding: utf-8 -*-

"""Top-level package for ANG (Afrikaans Name Generator)."""

__app_name__ = "ang"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    SCHEMA_ERROR,
    NAME_IDX_ERROR,
    SURNAME_IDX_ERROR,
) = range(9)

ERROR_STRINGS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    SCHEMA_ERROR: "schema validation error",
    NAME_IDX_ERROR: "name index error",
    SURNAME_IDX_ERROR: "surname index error",
}
