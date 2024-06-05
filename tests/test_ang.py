# -*- coding: utf-8 -*-

import json

import pytest
from typer.testing import CliRunner

from ang import DB_READ_ERROR, SUCCESS, __app_name__, __version__, ang, cli

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


@pytest.fixture
def mock_json_file(tmp_path):
    name_entry = [{"first_name": "Pieter", "prevalence": 10}]
    db_file = tmp_path / "ang.json"
    with db_file.open("w") as db:
        json.dump(name_entry, db, indent=4)
    return db_file


test_data1 = {
    "first_name": ["Jan"],
    "prevalence": 10,
    "entry": {"first_name": "Jan", "prevalence": 10},
}
test_data2 = {
    "first_name": ["Helgard"],
    "prevalence": 2,
    "entry": {"first_name": "Helgard", "prevalence": 2},
}


@pytest.mark.parametrize(
    "first_name, prevalence, expected",
    [
        pytest.param(
            test_data1["first_name"],
            test_data1["prevalence"],
            (test_data1["entry"], SUCCESS),
        ),
        pytest.param(
            test_data2["first_name"],
            test_data2["prevalence"],
            (test_data2["entry"], SUCCESS),
        ),
    ],
)
def test_add(mock_json_file, first_name, prevalence, expected):
    namer = ang.Namer(mock_json_file)
    assert namer.add(first_name, prevalence) == expected
    read = namer._db_handler.read_names()
    assert len(read.name_list) == 2
