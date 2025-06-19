"""
Configuration check and setup command
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os

console = Console()

@click.command()
@click.pass_context
def config(ctx):
    """
    Check configuration and API key status.
    
    Examples:
    \b
        datadagger config
    """
    verbose = ctx.obj.get('verbose', False)
    
    console.print(Panel.fit(
        "[bold blue]DataDagger Configuration Status[/bold blue]",
        border_style="blue"
    ))
    
    # Check environment file
    env_file_exists = os.path.exists('.env')
    if env_file_exists:
        console.print("✅ .env file found")
    else:
        console.print("❌ .env file not found")
        console.print("   Run: cp .env.example .env")
    
    # Check API keys
    table = Table(title="API Configuration Status")
    table.add_column("Platform", style="cyan", no_wrap=True)
    table.add_column("Status", style="white")
    table.add_column("Required Variables", style="yellow")
    
    # Twitter status
    twitter_bearer = os.getenv('TWITTER_BEARER_TOKEN')
    if twitter_bearer and not twitter_bearer.startswith('your_'):
        twitter_status = "✅ Configured (Paid API)"
    else:
        twitter_status = "❌ Not configured (Paid: $100+/month)"
    
    table.add_row(
        "Twitter",
        twitter_status,
        "TWITTER_BEARER_TOKEN (Paid API)"
    )
    
    # Mastodon status  
    mastodon_token = os.getenv('MASTODON_ACCESS_TOKEN')
    mastodon_instance = os.getenv('MASTODON_INSTANCE_URL')
    
    if mastodon_instance:  # Token is optional for public data
        mastodon_status = "✅ Configured (Free)"
    else:
        mastodon_status = "❌ Not configured (Free alternative)"
    
    table.add_row(
        "Mastodon",
        mastodon_status,
        "MASTODON_INSTANCE_URL (Free)"
    )
    
    # Reddit status
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    if (reddit_id and not reddit_id.startswith('your_') and 
        reddit_secret and not reddit_secret.startswith('your_')):
        reddit_status = "✅ Configured"
    else:
        reddit_status = "❌ Not configured"
    
    table.add_row(
        "Reddit",
        reddit_status,
        "REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET"
    )
    
    console.print(table)
    
    # Show next steps if not configured
    twitter_configured = twitter_bearer and not twitter_bearer.startswith('your_')
    reddit_configured = (reddit_id and not reddit_id.startswith('your_') and 
                        reddit_secret and not reddit_secret.startswith('your_'))
    mastodon_configured = mastodon_instance and not mastodon_instance.startswith('your_')
    
    if not twitter_configured and not reddit_configured and not mastodon_configured:
        console.print("\n[red]⚠️  No API keys configured![/red]")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Edit your .env file with API credentials")
        console.print("2. Get Reddit API keys (FREE): https://www.reddit.com/prefs/apps/")
        console.print("3. Set up Mastodon (FREE): Choose instance from mastodon.social")
        console.print("4. Twitter API (PAID): $100+/month at https://developer.twitter.com/")
        console.print("5. Run 'datadagger config' again to verify")
    
    elif not reddit_configured and not mastodon_configured:
        console.print("\n[yellow]💡 Consider adding free alternatives:[/yellow]")
        console.print("   - Reddit API (free)")
        console.print("   - Mastodon API (free)")
    
    else:
        console.print("\n[green]🎉 Platform(s) configured! You can now use DataDagger.[/green]")
        if not reddit_configured:
            console.print("[yellow]💡 Consider adding Reddit API for more comprehensive analysis (free)[/yellow]")
        if not mastodon_configured:
            console.print("[yellow]💡 Consider adding Mastodon for Twitter-like content (free)[/yellow]")
        if twitter_configured:
            console.print("[blue]💰 Twitter API active - paid tier detected[/blue]")
    
    # Show database status
    db_path = os.getenv('DATABASE_URL', 'sqlite:///datadagger.db')
    if db_path.startswith('sqlite:///'):
        db_file = db_path[10:]
        if os.path.exists(db_file):
            console.print(f"\n[blue]📊 Database:[/blue] {db_file} (exists)")
        else:
            console.print(f"\n[blue]📊 Database:[/blue] {db_file} (will be created)")
    else:
        console.print(f"\n[blue]📊 Database:[/blue] {db_path}")
    
    if verbose:
        console.print(f"\n[dim]Working directory: {os.getcwd()}[/dim]")
        console.print(f"[dim]Environment file: {'.env' if env_file_exists else 'Not found'}[/dim]")
