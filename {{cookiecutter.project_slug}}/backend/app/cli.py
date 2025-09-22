#!/usr/bin/env python3
"""
CLI entry point for {{cookiecutter.project_name}}.
This allows running the CLI with: python -m app.cli
"""

if __name__ == "__main__":
    from app.cli.main import cli
    cli()
