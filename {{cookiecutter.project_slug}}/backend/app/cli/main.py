"""
Main CLI entry point for {{cookiecutter.project_name}}.
"""

import click
from rich.console import Console

from .router import setup_commands
from ..utils.logging import setup_cli_logging

console = Console()


@click.group()
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set log level"
)
@click.pass_context
def cli(ctx, verbose, log_level):
    """{{cookiecutter.project_name}} CLI - Manage your AI-powered backend."""
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['log_level'] = log_level
    
    # Setup logging for CLI
    setup_cli_logging(log_level, verbose)
    
    if verbose:
        console.print(f"[bold green]{{cookiecutter.project_name}} CLI initialized[/bold green]")


# Setup all commands
setup_commands(cli)


if __name__ == "__main__":
    cli()
