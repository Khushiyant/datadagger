"""
Search command for finding narratives across platforms
"""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
from datetime import datetime, timedelta

# Conditional imports to handle missing dependencies
try:
    from ..scrapers.reddit_scraper import RedditScraper
except ImportError:
    RedditScraper = None

try:
    from ..scrapers.twitter_scraper import TwitterScraper
except ImportError:
    TwitterScraper = None

try:
    from ..scrapers.mastodon_scraper import MastodonScraper
except ImportError:
    MastodonScraper = None

try:
    from ..analyzers.text_analyzer import TextAnalyzer
except ImportError:
    TextAnalyzer = None

try:
    from ..utils.data_store import DataStore
except ImportError:
    DataStore = None

console = Console()

@click.command()
@click.argument('query')
@click.option('--platforms', '-p', default='reddit,mastodon', 
              help='Comma-separated list of platforms to search (reddit,mastodon,twitter)')
@click.option('--days', '-d', default=30, type=int,
              help='Number of days to search back')
@click.option('--limit', '-l', default=100, type=int,
              help='Maximum number of results per platform')
@click.option('--output', '-o', help='Output file path (JSON format)')
@click.option('--similarity-threshold', '-s', default=0.7, type=float,
              help='Similarity threshold for grouping related content')
@click.pass_context
def search(ctx, query, platforms, days, limit, output, similarity_threshold):
    """
    Search for narratives across multiple platforms.
    
    QUERY: The search term, hashtag, or phrase to look for
    
    Platform Support:
    ✅ Reddit (free API)
    ✅ Mastodon (free API) 
    ⚠️  Twitter (paid API - $100+/month)
    
    Examples:
    \b
        datadagger search "birds aren't real"
        datadagger search "#stopthesteal" --platforms mastodon --days 7
        datadagger search "vaccine conspiracy" --platforms reddit,mastodon --limit 200 --output results.json
    """
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        console.print(f"[blue]Searching for:[/blue] {query}")
        console.print(f"[blue]Platforms:[/blue] {platforms}")
        console.print(f"[blue]Time range:[/blue] Last {days} days")
    
    platforms_list = [p.strip() for p in platforms.split(',')]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for platform in platforms_list:
            task = progress.add_task(f"Searching {platform}...", total=None)
            
            try:
                if platform.lower() == 'reddit':
                    if RedditScraper is None:
                        console.print(f"[yellow]Reddit scraper not available (missing dependencies)[/yellow]")
                        continue
                    scraper = RedditScraper()
                    platform_results = scraper.search(query, start_date, end_date, limit)
                elif platform.lower() == 'twitter':
                    if TwitterScraper is None:
                        console.print(f"[yellow]Twitter scraper not available (missing dependencies)[/yellow]")
                        continue
                    scraper = TwitterScraper()
                    platform_results = scraper.search(query, start_date, end_date, limit)
                elif platform.lower() == 'mastodon':
                    if MastodonScraper is None:
                        console.print(f"[yellow]Mastodon scraper not available (missing dependencies)[/yellow]")
                        continue
                    scraper = MastodonScraper()
                    platform_results = scraper.search(query, start_date, end_date, limit)
                else:
                    console.print(f"[yellow]Warning: Platform '{platform}' not supported yet[/yellow]")
                    continue
                
                results[platform] = platform_results
                progress.update(task, description=f"✓ {platform} ({len(platform_results)} results)")
                
            except Exception as e:
                console.print(f"[red]Error searching {platform}: {str(e)}[/red]")
                progress.update(task, description=f"✗ {platform} (error)")
    
    # Analyze results
    if results:
        if TextAnalyzer is None:
            console.print("[yellow]Text analyzer not available - showing raw results[/yellow]")
            # Show basic results without analysis
            for platform, posts in results.items():
                console.print(f"[blue]{platform}:[/blue] {len(posts)} posts found")
        else:
            analyzer = TextAnalyzer()
            analysis_task = progress.add_task("Analyzing content...", total=None)
            
            # Combine all results for analysis
            all_posts = []
            for platform, posts in results.items():
                for post in posts:
                    post['platform'] = platform
                    all_posts.append(post)
            
            # Group similar content
            grouped_results = analyzer.group_similar_content(all_posts, similarity_threshold)
            
            # Display results
            _display_search_results(grouped_results, verbose)
        
        # Save to file if requested
        if output:
            _save_results(output, {
                'query': query,
                'platforms': platforms_list,
                'search_period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
                'total_results': len(all_posts),
                'grouped_results': grouped_results,
                'raw_results': results
            })
            console.print(f"[green]Results saved to {output}[/green]")
    
    else:
        console.print("[yellow]No results found across any platform[/yellow]")

def _display_search_results(grouped_results, verbose=False):
    """Display search results in a formatted table"""
    
    table = Table(title="Search Results - Grouped by Similarity")
    table.add_column("Group", style="cyan", no_wrap=True)
    table.add_column("Count", style="magenta")
    table.add_column("Platforms", style="green")
    table.add_column("Sample Content", style="white")
    table.add_column("Earliest", style="yellow")
    
    for i, group in enumerate(grouped_results, 1):
        posts = group['posts']
        platforms = list(set(post['platform'] for post in posts))
        sample_content = posts[0]['content'][:100] + "..." if len(posts[0]['content']) > 100 else posts[0]['content']
        earliest_date = min(post['created_at'] for post in posts)
        
        table.add_row(
            f"Group {i}",
            str(len(posts)),
            ", ".join(platforms),
            sample_content,
            earliest_date.strftime("%Y-%m-%d %H:%M")
        )
    
    console.print(table)
    
    if verbose and grouped_results:
        console.print(f"\n[blue]Total groups found:[/blue] {len(grouped_results)}")
        console.print(f"[blue]Cross-platform groups:[/blue] {sum(1 for g in grouped_results if len(set(p['platform'] for p in g['posts'])) > 1)}")

def _save_results(output_path, data):
    """Save results to JSON file"""
    # Convert datetime objects to strings for JSON serialization
    def datetime_handler(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=datetime_handler, ensure_ascii=False)
