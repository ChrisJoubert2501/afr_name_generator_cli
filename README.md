# Afrikaans Name Generator

### How to run

Create and activate a local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Debian/Ubuntu, install `python3-venv` first if virtual environment creation fails:

```bash
sudo apt install python3.10-venv
```

Install for local development:

```bash
python -m pip install --upgrade pip setuptools
python -m pip install -e .[dev]
```

The editable install (`-e`) keeps the installed `ang` command linked to this checkout, so code changes under `ang/` are picked up without reinstalling.

Initialise database:

```bash
python -m ang init
```

Generate (10) names:

```bash
python -m ang generate -n 10
```

List all items in the database:

```bash
python -m ang list-all
```

### Testing

```bash
python -m pytest
```

## Inspiration

Based on the typer cli tutorial at:  
https://realpython.com/python-typer-cli/
