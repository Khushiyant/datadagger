#!/usr/bin/env python3
"""
DataDagger - Influence Archaeology OSINT Tool
Main CLI entry point
"""

import click
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()

from .commands.search import search
from .commands.track import track
from .commands.network import network
from .commands.timeline import timeline
from .commands.export import export_data
from .commands.sentiment import sentiment
from .commands.origin import origin
from .commands.correlate import correlate
from .commands.config import config
from .commands.demo import demo
from .commands.pricing import pricing
from .commands.setup import setup

console = Console()

@click.group()
@click.version_option(version='1.0.0')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """
    DataDagger - Influence Archaeology OSINT Tool
    
    Map how ideas, narratives, and information spread through digital communities.
    Designed for security research, threat intelligence, and misinformation analysis.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        console.print(Panel.fit(
            "[bold blue]DataDagger - Influence Archaeology OSINT Tool[/bold blue]\n"
            "Mapping information flow across digital communities",
            border_style="blue"
        ))

# Add command groups
cli.add_command(demo)
cli.add_command(setup)
cli.add_command(pricing)
cli.add_command(config)
cli.add_command(search)
cli.add_command(track)
cli.add_command(network)
cli.add_command(timeline)
cli.add_command(export_data)
cli.add_command(sentiment)
cli.add_command(origin)
cli.add_command(correlate)

if __name__ == '__main__':
    cli()
