# -*- coding: utf-8 -*-

import json

import pytest
from typer.testing import CliRunner

from ang import NAME_IDX_ERROR, SUCCESS, SURNAME_IDX_ERROR, __app_name__, __version__, ang, cli

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


@pytest.fixture
def mock_json_file(tmp_path):
    database = {
        "names": [{"name": "Pieter", "prevalence": 10}],
        "surnames": [],
    }
    db_file = tmp_path / "ang.json"
    with db_file.open("w") as db:
        json.dump(database, db, indent=4)
    return db_file


test_data1 = {
    "name": ["Jan"],
    "prevalence": 10,
    "entry": {"name": "Jan", "prevalence": 10},
}
test_data2 = {
    "name": ["Helgard"],
    "prevalence": 2,
    "entry": {"name": "Helgard", "prevalence": 2},
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
def test_add(mock_json_file, name, prevalence, expected):
    namer = ang.Namer(mock_json_file)
    assert namer.add_name(name, prevalence) == expected
    read = namer._db_handler.read_names()
    assert len(read.name_list) == 2


def test_generate_returns_empty_when_names_or_surnames_are_missing(
    mock_json_file,
):
    namer = ang.Namer(mock_json_file)
    assert namer.generate_random_name_surname(1) == []


def test_generate_uses_prevalence_as_weights(tmp_path, monkeypatch):
    database = {
        "names": [
            {"name": "Pieter", "prevalence": 10},
            {"name": "Jan", "prevalence": 1},
        ],
        "surnames": [
            {"surname": "Botha", "prevalence": 8},
            {"surname": "Nel", "prevalence": 2},
        ],
    }
    db_file = tmp_path / "ang.json"
    with db_file.open("w") as db:
        json.dump(database, db, indent=4)

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


def test_set_prevalence_cli_uses_name_key(tmp_path, monkeypatch):
    database = {
        "names": [{"name": "Pieter", "prevalence": 10}],
        "surnames": [],
    }
    db_file = tmp_path / "ang.json"
    with db_file.open("w") as db:
        json.dump(database, db, indent=4)

    config_file = tmp_path / "config.ini"
    config_file.write_text(f"[General]\ndatabase = {db_file}\n")
    monkeypatch.setattr(cli.config, "CONFIG_FILE_PATH", config_file)

    result = runner.invoke(cli.app, ["set-prevalence", "1", "4"])

    assert result.exit_code == 0
    assert 'Success: Set prevalence (4) on name # 1 "Pieter"' in result.stdout


def test_list_commands_show_names_and_surnames(tmp_path, monkeypatch):
    database = {
        "names": [{"name": "Pieter", "prevalence": 10}],
        "surnames": [{"surname": "Botha", "prevalence": 8}],
    }
    db_file = tmp_path / "ang.json"
    with db_file.open("w") as db:
        json.dump(database, db, indent=4)

    config_file = tmp_path / "config.ini"
    config_file.write_text(f"[General]\ndatabase = {db_file}\n")
    monkeypatch.setattr(cli.config, "CONFIG_FILE_PATH", config_file)

    names_result = runner.invoke(cli.app, ["list-names"])
    surnames_result = runner.invoke(cli.app, ["list-surnames"])

    assert names_result.exit_code == 0
    assert "Name list:" in names_result.stdout
    assert "Pieter" in names_result.stdout
    assert surnames_result.exit_code == 0
    assert "Surname list:" in surnames_result.stdout
    assert "Botha" in surnames_result.stdout


def test_remove_surname_cli_uses_surname_wording(tmp_path, monkeypatch):
    database = {
        "names": [],
        "surnames": [{"surname": "Botha", "prevalence": 8}],
    }
    db_file = tmp_path / "ang.json"
    with db_file.open("w") as db:
        json.dump(database, db, indent=4)

    config_file = tmp_path / "config.ini"
    config_file.write_text(f"[General]\ndatabase = {db_file}\n")
    monkeypatch.setattr(cli.config, "CONFIG_FILE_PATH", config_file)

    result = runner.invoke(cli.app, ["remove-surname", "1", "--force"])

    assert result.exit_code == 0
    assert "Surname # 1: 'Botha' was removed" in result.stdout


def test_generate_rejects_non_positive_number():
    result = runner.invoke(cli.app, ["generate", "-n", "0"])

    assert result.exit_code != 0
    assert "Invalid value" in result.stdout


def test_name_indexes_are_one_based(mock_json_file):
    namer = ang.Namer(mock_json_file)

    assert namer.set_name_prevalence(0, 4).response == NAME_IDX_ERROR
    assert namer.remove_name_by_idx(0).response == NAME_IDX_ERROR


def test_surname_indexes_are_one_based(tmp_path):
    database = {
        "names": [],
        "surnames": [{"surname": "Botha", "prevalence": 10}],
    }
    db_file = tmp_path / "ang.json"
    with db_file.open("w") as db:
        json.dump(database, db, indent=4)

    namer = ang.Namer(db_file)

    assert namer.remove_surname_by_idx(0).response == SURNAME_IDX_ERROR
