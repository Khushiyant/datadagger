"""
Track command for narrative evolution over time
"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
import json

# Conditional imports to handle missing dependencies
try:
    from ..analyzers.narrative_tracker import NarrativeTracker
except ImportError:
    NarrativeTracker = None

try:
    from ..visualizers.timeline_viz import TimelineVisualizer
except ImportError:
    TimelineVisualizer = None

console = Console()

@click.command()
@click.option('--query', '-q', required=True, help='Query to track over time')
@click.option('--start-date', '-s', required=True, 
              help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', required=True,
              help='End date (YYYY-MM-DD)')
@click.option('--platforms', '-p', default='reddit,twitter',
              help='Platforms to search')
@click.option('--output', '-o', help='Output file for visualization')
@click.option('--granularity', '-g', default='daily',
              type=click.Choice(['hourly', 'daily', 'weekly']),
              help='Time granularity for tracking')
@click.pass_context
def track(ctx, query, start_date, end_date, platforms, output, granularity):
    """
    Track how a narrative evolves over time.
    
    Examples:
    \b
        datadagger track --query "covid lab leak" --start-date 2020-01-01 --end-date 2023-01-01
        datadagger track --query "#stopthesteal" --start-date 2020-11-01 --end-date 2021-01-31 --granularity hourly
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        console.print("[red]Error: Invalid date format. Use YYYY-MM-DD[/red]")
        return
    
    if verbose:
        console.print(f"[blue]Tracking narrative:[/blue] {query}")
        console.print(f"[blue]Period:[/blue] {start_date} to {end_date}")
        console.print(f"[blue]Granularity:[/blue] {granularity}")
    
    if NarrativeTracker is None:
        console.print("[red]Error: Narrative tracking not available (missing dependencies)[/red]")
        console.print("[yellow]Please install all required dependencies with: pip install -r requirements.txt[/yellow]")
        return
    
    if TimelineVisualizer is None:
        console.print("[red]Error: Timeline visualization not available (missing dependencies)[/red]")
        console.print("[yellow]Please install all required dependencies with: pip install -r requirements.txt[/yellow]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Initialize tracker
        task1 = progress.add_task("Initializing narrative tracker...", total=None)
        tracker = NarrativeTracker()
        
        # Collect data over time periods
        task2 = progress.add_task("Collecting temporal data...", total=None)
        timeline_data = tracker.track_narrative_evolution(
            query, start_dt, end_dt, platforms.split(','), granularity
        )
        
        # Generate visualization
        task3 = progress.add_task("Generating timeline visualization...", total=None)
        visualizer = TimelineVisualizer()
        
        output_file = output or f"timeline_{query.replace(' ', '_')}_{start_date}_{end_date}.html"
        visualizer.create_timeline(timeline_data, output_file)
        
        progress.update(task3, description="✓ Timeline generated")
    
    console.print(f"[green]Timeline visualization saved to: {output_file}[/green]")
    
    if verbose:
        console.print(f"[blue]Data points collected:[/blue] {len(timeline_data)}")
        console.print(f"[blue]Peak activity period:[/blue] {_find_peak_period(timeline_data)}")

def _find_peak_period(timeline_data):
    """Find the period with highest activity"""
    if not timeline_data:
        return "No data"
    
    max_activity = max(timeline_data, key=lambda x: x.get('volume', 0))
    return max_activity.get('period', 'Unknown')
