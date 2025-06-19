"""
Origin tracking command for finding patient zero
"""

import click
from rich.console import Console

console = Console()

@click.command()
@click.option('--query', '-q', required=True, help='Narrative to find origin of')
@click.option('--threshold', '-t', default=0.8, type=float, help='Similarity threshold')
@click.option('--depth', '-d', default=5, type=int, help='Search depth')
@click.pass_context
def origin(ctx, query, threshold, depth):
    """
    Find the origin point (patient zero) of a narrative.
    
    Examples:
    \b
        datadagger origin --query "birds aren't real" --threshold 0.8
    """
    console.print("[yellow]Origin tracking coming soon...[/yellow]")
