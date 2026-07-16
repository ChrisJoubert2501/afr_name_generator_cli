import json

import pytest
from typer.testing import CliRunner

from ang import (
    GENDER_ERROR,
    JSON_ERROR,
    NAME_IDX_ERROR,
    SUCCESS,
    SURNAME_IDX_ERROR,
    __app_name__,
    __version__,
    ang,
    cli,
    presenter,
)

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


def test_root_command_shows_help():
    result = runner.invoke(cli.app)

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Commands" in result.output
    assert "init" in result.output
    assert "set-prevalence" not in result.output
    assert "set-name-prevalence" in result.output
    assert "Set a name's prevalence using its index or value." in result.output
    assert "set-surname-prevalence" in result.output
    assert (
        "Set a surname's prevalence using its index or value." in result.output
    )
    assert "set-name-gender" in result.output
    assert "db-heal" in result.output


def test_cli_error_message_handles_json_errors():
    assert presenter.get_error_message(JSON_ERROR) == "database JSON error"


def test_cli_handles_invalid_config_file(tmp_path, monkeypatch):
    config_file = tmp_path / "config.ini"
    config_file.write_text("[General]\n")
    monkeypatch.setattr(cli.config, "CONFIG_FILE_PATH", config_file)

    result = runner.invoke(cli.app, ["list-names"])

    assert result.exit_code == 1
    assert 'Config file is invalid. Please, run "ang init"' in result.stdout


def test_list_names_surfaces_database_read_errors(tmp_path, monkeypatch):
    db_file = tmp_path / "ang.json"
    db_file.write_text("{")

    config_file = tmp_path / "config.ini"
    config_file.write_text(f"[General]\ndatabase = {db_file}\n")
    monkeypatch.setattr(cli.config, "CONFIG_FILE_PATH", config_file)

    result = runner.invoke(cli.app, ["list-names"])

    assert result.exit_code == 1
    assert 'Reading names failed with "database JSON error"' in result.stdout


@pytest.fixture
def database_file(tmp_path):
    def _database_file(database):
        db_file = tmp_path / "ang.json"
        with db_file.open("w") as db:
            json.dump(database, db, indent=4)
        return db_file

    return _database_file


@pytest.fixture
def configured_cli_database(tmp_path, monkeypatch, database_file):
    def _configured_cli_database(database):
        db_file = database_file(database)
        config_file = tmp_path / "config.ini"
        config_file.write_text(f"[General]\ndatabase = {db_file}\n")
        monkeypatch.setattr(cli.config, "CONFIG_FILE_PATH", config_file)
        return db_file

    return _configured_cli_database


@pytest.fixture
def names_only_database_file(database_file):
    return database_file(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [],
        }
    )


test_data1 = {
    "name": ["Jan"],
    "prevalence": 10,
    "entry": {"name": "Jan", "prevalence": 10, "gender": "man"},
}
test_data2 = {
    "name": ["Helgard"],
    "prevalence": 2,
    "entry": {"name": "Helgard", "prevalence": 2, "gender": "man"},
}


@pytest.mark.parametrize(
    "name, prevalence, expected",
    [
        pytest.param(
            test_data1["name"],
            test_data1["prevalence"],
            (test_data1["entry"], SUCCESS),
        ),
        pytest.param(
            test_data2["name"],
            test_data2["prevalence"],
            (test_data2["entry"], SUCCESS),
        ),
    ],
)
def test_add(names_only_database_file, name, prevalence, expected):
    namer = ang.Namer(names_only_database_file)
    assert namer.add_name(name, prevalence, "man") == expected
    assert len(namer.get_name_list().name_list) == 2


def test_add_name_rejects_invalid_gender(names_only_database_file):
    namer = ang.Namer(names_only_database_file)

    assert namer.add_name(["Jan"], 10, "invalid").response == GENDER_ERROR


def test_add_name_cli_accepts_gender(configured_cli_database):
    db_file = configured_cli_database({"names": [], "surnames": []})

    result = runner.invoke(cli.app, ["add-name", "Pieter", "--gender", "man"])

    assert result.exit_code == 0
    assert "and gender: man" in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == [
        {"name": "Pieter", "prevalence": 10, "gender": "man"}
    ]


def test_add_name_cli_prompts_for_gender(configured_cli_database):
    db_file = configured_cli_database({"names": [], "surnames": []})

    result = runner.invoke(cli.app, ["add-name", "Pieter"], input="woman\n")

    assert result.exit_code == 0
    assert "Gender:" in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == [
        {"name": "Pieter", "prevalence": 10, "gender": "woman"}
    ]


def test_missing_name_gender_is_inferred_as_man(database_file):
    db_file = database_file(
        {
            "names": [{"name": "Pieter", "prevalence": 10}],
            "surnames": [],
        }
    )

    namer = ang.Namer(db_file)

    assert namer.get_name_list().name_list == [
        {"name": "Pieter", "prevalence": 10, "gender": "man"}
    ]


def test_db_heal_writes_missing_name_gender(configured_cli_database):
    db_file = configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10}],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["db-heal", "--force"])

    assert result.exit_code == 0
    assert "1 missing name gender value(s) added" in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == [
        {"name": "Pieter", "prevalence": 10, "gender": "man"}
    ]


def test_generate_returns_empty_when_names_or_surnames_are_missing(
    names_only_database_file,
):
    namer = ang.Namer(names_only_database_file)
    assert namer.generate_random_name_surname(1) == []


def test_generate_uses_prevalence_as_weights(database_file, monkeypatch):
    database = {
        "names": [
            {"name": "Pieter", "prevalence": 10, "gender": "man"},
            {"name": "Jan", "prevalence": 1, "gender": "man"},
        ],
        "surnames": [
            {"surname": "Botha", "prevalence": 8},
            {"surname": "Nel", "prevalence": 2},
        ],
    }
    db_file = database_file(database)

    calls = []

    def fake_choices(population, weights, k):
        calls.append((population, weights, k))
        return [population[0]] * k

    monkeypatch.setattr(ang.random, "choices", fake_choices)

    namer = ang.Namer(db_file)
    assert namer.generate_random_name_surname(2) == [
        "Pieter Botha",
        "Pieter Botha",
    ]
    assert calls == [
        (database["names"], [10, 1], 2),
        (database["surnames"], [8, 2], 2),
    ]


def test_set_name_prevalence_cli_accepts_name_index(
    configured_cli_database,
):
    configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["set-name-prevalence", "1", "4"])

    assert result.exit_code == 0
    assert 'Success: Set prevalence (4) on name "Pieter"' in result.stdout


def test_set_name_prevalence_cli_accepts_name_value(
    configured_cli_database,
):
    db_file = configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["set-name-prevalence", "pieter", "4"])

    assert result.exit_code == 0
    assert 'Success: Set prevalence (4) on name "Pieter"' in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == [
        {"name": "Pieter", "prevalence": 4, "gender": "man"}
    ]


def test_set_surname_prevalence_cli_accepts_surname_value(
    configured_cli_database,
):
    db_file = configured_cli_database(
        {
            "names": [],
            "surnames": [{"surname": "Botha", "prevalence": 8}],
        }
    )

    result = runner.invoke(cli.app, ["set-surname-prevalence", "botha", "4"])

    assert result.exit_code == 0
    assert 'Success: Set prevalence (4) on surname "Botha"' in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["surnames"] == [{"surname": "Botha", "prevalence": 4}]


def test_list_commands_show_names_and_surnames(configured_cli_database):
    configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [{"surname": "Botha", "prevalence": 8}],
        }
    )

    names_result = runner.invoke(cli.app, ["list-names"])
    surnames_result = runner.invoke(cli.app, ["list-surnames"])

    assert names_result.exit_code == 0
    assert "Man name list:" in names_result.stdout
    assert "Pieter" in names_result.stdout
    assert "Gender" in names_result.stdout
    assert surnames_result.exit_code == 0
    assert "Surname list:" in surnames_result.stdout
    assert "Botha" in surnames_result.stdout


def test_list_names_groups_names_by_gender(configured_cli_database):
    configured_cli_database(
        {
            "names": [
                {"name": "Pieter", "prevalence": 10, "gender": "man"},
                {"name": "Anna", "prevalence": 10, "gender": "woman"},
                {"name": "Alex", "prevalence": 10, "gender": "neutral"},
            ],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["list-names"])

    assert result.exit_code == 0
    assert result.stdout.index("Man name list") < result.stdout.index(
        "Woman name list"
    )
    assert result.stdout.index("Woman name list") < result.stdout.index(
        "Neutral name list"
    )
    assert "Pieter" in result.stdout
    assert "Anna" in result.stdout
    assert "Alex" in result.stdout


def test_list_names_filters_by_exact_gender(configured_cli_database):
    configured_cli_database(
        {
            "names": [
                {"name": "Pieter", "prevalence": 10, "gender": "man"},
                {"name": "Anna", "prevalence": 10, "gender": "woman"},
                {"name": "Alex", "prevalence": 10, "gender": "neutral"},
            ],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["list-names", "--gender", "woman"])

    assert result.exit_code == 0
    assert "Woman name list" in result.stdout
    assert "Anna" in result.stdout
    assert "Pieter" not in result.stdout
    assert "Alex" not in result.stdout


def test_list_all_filters_names_by_exact_gender(configured_cli_database):
    configured_cli_database(
        {
            "names": [
                {"name": "Pieter", "prevalence": 10, "gender": "man"},
                {"name": "Anna", "prevalence": 10, "gender": "woman"},
            ],
            "surnames": [{"surname": "Botha", "prevalence": 8}],
        }
    )

    result = runner.invoke(cli.app, ["list-all", "--gender", "woman"])

    assert result.exit_code == 0
    assert "Anna" in result.stdout
    assert "Pieter" not in result.stdout
    assert "Surname list" in result.stdout
    assert "Botha" in result.stdout


def test_set_name_gender_cli_accepts_name_value(configured_cli_database):
    db_file = configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["set-name-gender", "pieter", "woman"])

    assert result.exit_code == 0
    assert 'Success: Set gender (woman) on name "Pieter"' in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == [
        {"name": "Pieter", "prevalence": 10, "gender": "woman"}
    ]


def test_remove_surname_cli_uses_surname_wording(configured_cli_database):
    configured_cli_database(
        {
            "names": [],
            "surnames": [{"surname": "Botha", "prevalence": 8}],
        }
    )

    result = runner.invoke(cli.app, ["remove-surname", "1", "--force"])

    assert result.exit_code == 0
    assert "Surname 'Botha' was removed" in result.stdout


def test_remove_name_cli_accepts_name_value(configured_cli_database):
    db_file = configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["remove-name", "Pieter", "--force"])

    assert result.exit_code == 0
    assert "Name 'Pieter' was removed" in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == []


def test_remove_surname_cli_accepts_surname_value(configured_cli_database):
    db_file = configured_cli_database(
        {
            "names": [],
            "surnames": [{"surname": "Botha", "prevalence": 8}],
        }
    )

    result = runner.invoke(cli.app, ["remove-surname", "botha", "--force"])

    assert result.exit_code == 0
    assert "Surname 'Botha' was removed" in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["surnames"] == []


def test_remove_name_cancel_does_not_delete(configured_cli_database):
    db_file = configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [],
        }
    )

    result = runner.invoke(cli.app, ["remove-name", "Pieter"], input="n\n")

    assert result.exit_code == 0
    assert "Operation canceled" in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == [
        {"name": "Pieter", "prevalence": 10, "gender": "man"}
    ]


def test_remove_all_removes_names_and_surnames(
    configured_cli_database,
):
    db_file = configured_cli_database(
        {
            "names": [{"name": "Pieter", "prevalence": 10, "gender": "man"}],
            "surnames": [{"surname": "Botha", "prevalence": 8}],
        }
    )

    result = runner.invoke(cli.app, ["remove-all", "--force"])

    assert result.exit_code == 0
    assert "All names and surnames were removed" in result.stdout
    with db_file.open("r") as db:
        database = json.load(db)
    assert database["names"] == []
    assert database["surnames"] == []


def test_generate_rejects_non_positive_number():
    result = runner.invoke(cli.app, ["generate", "-n", "0"])

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_name_indexes_are_one_based(names_only_database_file):
    namer = ang.Namer(names_only_database_file)

    assert namer.set_name_prevalence("0", 4).response == NAME_IDX_ERROR
    assert namer.remove_name_by_idx(0).response == NAME_IDX_ERROR


def test_surname_indexes_are_one_based(database_file):
    database = {
        "names": [],
        "surnames": [{"surname": "Botha", "prevalence": 10}],
    }
    db_file = database_file(database)

    namer = ang.Namer(db_file)

    assert namer.set_surname_prevalence("0", 4).response == SURNAME_IDX_ERROR
    assert namer.remove_surname_by_idx(0).response == SURNAME_IDX_ERROR
