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

Enable shell completion for commands and options:

```bash
ang --install-completion
```

This installs a small completion hook for your current shell by updating the shell's startup configuration, such as `~/.bashrc` for Bash.

Restart your shell after installing completion. You can inspect the generated completion script without installing it:

```bash
ang --show-completion
```

Initialise database:

```bash
python -m ang init
```

Generate (10) mixed names:

```bash
python -m ang generate -n 10
```

`generate` defaults to `--gender mixed`, which randomly alternates between man and woman name pools. Neutral names are included when generating man or woman names.

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
