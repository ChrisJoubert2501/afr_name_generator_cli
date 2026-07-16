# Afrikaans Name Generator

### How to run

Create and activate a local virtual environment:
`python3 -m venv .venv`
`source .venv/bin/activate`

On Debian/Ubuntu, install `python3-venv` first if virtual environment creation fails:
`sudo apt install python3.10-venv`

Install for local development:
`python -m pip install --upgrade pip setuptools`
`python -m pip install -e .[dev]`

Initialise database:  
`python -m ang init`

Generate (10) names:  
`python -m ang generate -n 10`

List all items in the database:  
`python -m ang list-all`

### Testing

`python -m pytest`

## Inspiration

Based on the typer cli tutorial at:  
https://realpython.com/python-typer-cli/
