"""
Demo command to showcase DataDagger functionality
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import time
from datetime import datetime, timedelta

console = Console()

# Sample demo data
DEMO_DATA = {
    "birds_arent_real": [
        {
            "id": "demo_001",
            "content": "Birds aren't real - they're government surveillance drones! Wake up sheeple! #BirdsArentReal",
            "author": "truth_seeker_2019",
            "platform": "twitter",
            "created_at": datetime.now() - timedelta(days=5),
            "engagement_score": 42,
            "location": "viral_origin"
        },
        {
            "id": "demo_002", 
            "content": "I thought birds aren't real was satire but my nephew actually believes it now...",
            "author": "confused_uncle",
            "platform": "reddit",
            "created_at": datetime.now() - timedelta(days=3),
            "engagement_score": 156,
            "location": "mainstream_spread"
        },
        {
            "id": "demo_003",
            "content": "Documentary idea: How did 'Birds Aren't Real' go from joke to belief system?",
            "author": "doc_filmmaker", 
            "platform": "twitter",
            "created_at": datetime.now() - timedelta(days=1),
            "engagement_score": 89,
            "location": "meta_analysis"
        }
    ],
    "flat_earth": [
        {
            "id": "demo_004",
            "content": "NASA lies! The earth is flat and they've been hiding it for decades! Do your own research!",
            "author": "flat_truth",
            "platform": "reddit", 
            "created_at": datetime.now() - timedelta(days=10),
            "engagement_score": 234,
            "location": "conspiracy_hub"
        },
        {
            "id": "demo_005",
            "content": "Why flat earth theory persists despite overwhelming evidence - psychological analysis",
            "author": "science_educator",
            "platform": "twitter",
            "created_at": datetime.now() - timedelta(days=2),
            "engagement_score": 445,
            "location": "educational_response"
        }
    ]
}

@click.command()
@click.option('--query', '-q', default='birds_arent_real', 
              type=click.Choice(['birds_arent_real', 'flat_earth']),
              help='Demo query to analyze')
@click.option('--show-timeline', '-t', is_flag=True, help='Show timeline analysis')
@click.option('--show-network', '-n', is_flag=True, help='Show network analysis')
@click.option('--output', '-o', help='Save demo results to file')
@click.pass_context
def demo(ctx, query, show_timeline, show_network, output):
    """
    Run a demo of DataDagger capabilities using sample data.
    
    This command demonstrates key features without requiring API keys.
    
    Examples:
    \b
        datadagger demo
        datadagger demo --query flat_earth --show-timeline
        datadagger demo --show-network --output demo_results.json
    """
    verbose = ctx.obj.get('verbose', False)
    
    console.print(Panel.fit(
        "[bold yellow]🎭 DataDagger Demo Mode[/bold yellow]\n"
        "Showcasing capabilities with sample data\n\n"
        "[dim]Note: Real search supports FREE platforms (Reddit, Mastodon)\n"
        "Twitter requires paid API access ($100+/month since Feb 2023)[/dim]",
        border_style="yellow"
    ))
    
    if verbose:
        console.print(f"[blue]Demo query:[/blue] {query}")
        console.print(f"[blue]Timeline analysis:[/blue] {'enabled' if show_timeline else 'disabled'}")
        console.print(f"[blue]Network analysis:[/blue] {'enabled' if show_network else 'disabled'}")
    
    # Simulate data collection
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task1 = progress.add_task("Collecting demo data...", total=None)
        time.sleep(1)  # Simulate API calls
        
        task2 = progress.add_task("Analyzing content similarity...", total=None)
        time.sleep(1)  # Simulate processing
        
        if show_timeline:
            task3 = progress.add_task("Generating timeline analysis...", total=None)
            time.sleep(1)
        
        if show_network:
            task4 = progress.add_task("Mapping influence networks...", total=None)
            time.sleep(1)
    
    # Get demo data
    posts = DEMO_DATA.get(query, [])
    
    # Display results
    _display_demo_results(posts, query, verbose)
    
    if show_timeline:
        _display_timeline_analysis(posts)
    
    if show_network:
        _display_network_analysis(posts)
    
    # Save results if requested
    if output:
        demo_results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'posts': [_serialize_post(post) for post in posts],
            'analysis': {
                'total_posts': len(posts),
                'platforms': list(set(post['platform'] for post in posts)),
                'date_range': {
                    'earliest': min(post['created_at'] for post in posts).isoformat(),
                    'latest': max(post['created_at'] for post in posts).isoformat()
                },
                'avg_engagement': sum(post['engagement_score'] for post in posts) / len(posts)
            }
        }
        
        with open(output, 'w') as f:
            json.dump(demo_results, f, indent=2)
        
        console.print(f"\n[green]Demo results saved to {output}[/green]")
    
    # Show next steps
    console.print(f"\n[blue]💡 Next Steps:[/blue]")
    console.print("1. Set up FREE APIs: datadagger config")
    console.print("   • Reddit API (free): https://www.reddit.com/prefs/apps/") 
    console.print("   • Mastodon API (free): https://mastodon.social")
    console.print("2. Try real searches: datadagger search 'your query' --platforms reddit,mastodon")
    console.print("3. Track narratives: datadagger track --query 'narrative' --start-date 2024-01-01 --end-date 2024-12-31")
    console.print("\n[dim]💰 Twitter API available for $100+/month if needed[/dim]")

def _display_demo_results(posts, query, verbose=False):
    """Display demo search results"""
    
    table = Table(title=f"Demo Results: {query.replace('_', ' ').title()}")
    table.add_column("Platform", style="cyan", no_wrap=True)
    table.add_column("Author", style="green")
    table.add_column("Content Preview", style="white")
    table.add_column("Engagement", style="magenta")
    table.add_column("Days Ago", style="yellow")
    
    for post in posts:
        days_ago = (datetime.now() - post['created_at']).days
        content_preview = post['content'][:80] + "..." if len(post['content']) > 80 else post['content']
        
        table.add_row(
            post['platform'].title(),
            post['author'],
            content_preview,
            str(post['engagement_score']),
            f"{days_ago}d ago"
        )
    
    console.print(table)
    
    if verbose:
        console.print(f"\n[blue]Analysis Summary:[/blue]")
        console.print(f"• Total posts: {len(posts)}")
        console.print(f"• Platforms: {', '.join(set(post['platform'] for post in posts))}")
        console.print(f"• Average engagement: {sum(post['engagement_score'] for post in posts) / len(posts):.1f}")

def _display_timeline_analysis(posts):
    """Display timeline analysis"""
    
    console.print(f"\n[yellow]📈 Timeline Analysis[/yellow]")
    
    # Sort posts by date
    sorted_posts = sorted(posts, key=lambda x: x['created_at'])
    
    timeline_table = Table(title="Narrative Evolution Timeline")
    timeline_table.add_column("Stage", style="cyan")
    timeline_table.add_column("Time", style="yellow")
    timeline_table.add_column("Platform", style="green")
    timeline_table.add_column("Content Type", style="magenta")
    timeline_table.add_column("Engagement", style="white")
    
    stages = ["Origin", "Spread", "Mainstream", "Meta-Analysis"]
    
    for i, post in enumerate(sorted_posts):
        stage = stages[min(i, len(stages)-1)]
        time_str = post['created_at'].strftime("%Y-%m-%d")
        
        timeline_table.add_row(
            stage,
            time_str,
            post['platform'].title(),
            post.get('location', 'general').replace('_', ' ').title(),
            str(post['engagement_score'])
        )
    
    console.print(timeline_table)

def _display_network_analysis(posts):
    """Display network analysis"""
    
    console.print(f"\n[cyan]🕸️  Network Analysis[/cyan]")
    
    # Simulate influence network
    network_table = Table(title="Key Influencers & Connections")
    network_table.add_column("Author", style="green")
    network_table.add_column("Platform", style="cyan")
    network_table.add_column("Influence Score", style="magenta")
    network_table.add_column("Connection Type", style="yellow")
    
    for post in posts:
        # Simulate influence scoring
        influence_score = min(100, post['engagement_score'] * 2)
        
        if influence_score > 200:
            connection_type = "Hub"
        elif influence_score > 100:
            connection_type = "Bridge"
        else:
            connection_type = "Node"
        
        network_table.add_row(
            post['author'],
            post['platform'].title(),
            str(influence_score),
            connection_type
        )
    
    console.print(network_table)
    
    console.print(f"\n[dim]• Network analysis shows information flow patterns[/dim]")
    console.print(f"[dim]• Hub accounts drive initial spread[/dim]")
    console.print(f"[dim]• Bridge accounts connect different communities[/dim]")

def _serialize_post(post):
    """Convert post to JSON-serializable format"""
    serialized = post.copy()
    serialized['created_at'] = post['created_at'].isoformat()
    return serialized
