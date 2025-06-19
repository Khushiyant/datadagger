"""
Sentiment analysis command
"""

import click
from rich.console import Console

console = Console()

@click.command()
@click.option('--query', '-q', required=True, help='Query to analyze sentiment for')
@click.option('--platform', '-p', default='all', help='Platform to analyze')
@click.option('--timeline', '-t', is_flag=True, help='Show sentiment over time')
@click.pass_context
def sentiment(ctx, query, platform, timeline):
    """
    Analyze sentiment of narratives over time.
    
    Examples:
    \b
        datadagger sentiment --query "vaccine" --platform twitter --timeline
    """
    console.print("[yellow]Sentiment analysis coming soon...[/yellow]")
