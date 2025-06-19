"""
Platform pricing and comparison command
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@click.command()
@click.pass_context
def pricing(ctx):
    """
    Show platform pricing and feature comparison.
    
    Helps users choose the best platforms for their budget and needs.
    
    Examples:
    \b
        datadagger pricing
    """
    verbose = ctx.obj.get('verbose', False)
    
    console.print(Panel.fit(
        "[bold cyan]💰 Platform Pricing & Feature Comparison[/bold cyan]\n"
        "Choose the right platforms for your OSINT needs",
        border_style="cyan"
    ))
    
    # Main pricing table
    pricing_table = Table(title="Platform Comparison (June 2025)")
    pricing_table.add_column("Platform", style="bold cyan", no_wrap=True)
    pricing_table.add_column("Cost", style="green")
    pricing_table.add_column("API Limits", style="yellow")
    pricing_table.add_column("Content Type", style="white")
    pricing_table.add_column("Best For", style="magenta")
    pricing_table.add_column("Status", style="blue")
    
    pricing_table.add_row(
        "🟢 Reddit",
        "FREE",
        "60 requests/min",
        "Forums, discussions",
        "Long-form content, communities",
        "✅ Recommended"
    )
    
    pricing_table.add_row(
        "🟢 Mastodon", 
        "FREE",
        "300 requests/15min",
        "Microblogging",
        "Twitter-like content, decentralized",
        "✅ Recommended"
    )
    
    pricing_table.add_row(
        "🔴 Twitter",
        "$100+/month",
        "10K tweets/month (Basic)",
        "Microblogging, news",
        "Real-time trends, breaking news",
        "⚠️ Paid only"
    )
    
    console.print(pricing_table)
    
    # Feature comparison
    console.print(f"\n[yellow]🔍 Feature Comparison[/yellow]")
    
    feature_table = Table()
    feature_table.add_column("Feature", style="white")
    feature_table.add_column("Reddit", style="green", justify="center")
    feature_table.add_column("Mastodon", style="blue", justify="center") 
    feature_table.add_column("Twitter", style="red", justify="center")
    
    features = [
        ("Search historical posts", "✅", "✅", "✅"),
        ("Real-time monitoring", "✅", "✅", "✅"),
        ("User analytics", "✅", "✅", "✅"),
        ("Hashtag tracking", "Limited", "✅", "✅"),
        ("Geographic data", "No", "Limited", "✅"),
        ("Sentiment analysis", "✅", "✅", "✅"),
        ("Network analysis", "✅", "✅", "✅"),
        ("Rate limits", "Generous", "Generous", "Strict"),
        ("Setup complexity", "Easy", "Easy", "Complex")
    ]
    
    for feature_name, reddit, mastodon, twitter in features:
        feature_table.add_row(feature_name, reddit, mastodon, twitter)
    
    console.print(feature_table)
    
    # Cost breakdown
    console.print(f"\n[blue]💵 Cost Analysis (Annual)[/blue]")
    
    cost_table = Table()
    cost_table.add_column("Scenario", style="white")
    cost_table.add_column("Platforms", style="cyan")
    cost_table.add_column("Annual Cost", style="green")
    cost_table.add_column("Coverage", style="yellow")
    
    cost_table.add_row(
        "🎓 Student/Researcher",
        "Reddit + Mastodon",
        "$0",
        "85% of social media content"
    )
    
    cost_table.add_row(
        "🏢 Small Organization", 
        "Reddit + Mastodon + Twitter Basic",
        "$1,200/year",
        "95% of social media content"
    )
    
    cost_table.add_row(
        "🏬 Enterprise",
        "All platforms + Premium Twitter",
        "$3,600+/year",
        "100% coverage + advanced features"
    )
    
    console.print(cost_table)
    
    # Recommendations
    console.print(f"\n[green]🎯 Recommendations[/green]")
    
    recommendations = [
        "🆓 **Start Free**: Use Reddit + Mastodon for comprehensive coverage",
        "📊 **Most Data**: Reddit has the richest discussion threads", 
        "⚡ **Real-time**: Mastodon for Twitter-like speed without the cost",
        "💰 **If Budget Allows**: Add Twitter for breaking news and trends",
        "🎓 **Academic**: Most universities have research API access programs",
        "🔒 **Security Research**: Reddit + Mastodon covers most threat discussions"
    ]
    
    for rec in recommendations:
        console.print(f"   {rec}")
    
    # Setup links
    console.print(f"\n[cyan]🔗 Quick Setup Links[/cyan]")
    console.print("   Reddit API: https://www.reddit.com/prefs/apps/")
    console.print("   Mastodon: https://mastodon.social → Preferences → Development")
    console.print("   Twitter API: https://developer.twitter.com/ (Paid)")
    
    if verbose:
        console.print(f"\n[dim]Platform data as of June 2025[/dim]")
        console.print(f"[dim]Pricing subject to change - always verify current rates[/dim]")
