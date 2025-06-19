"""
Setup wizard for easy configuration
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import os
import webbrowser

console = Console()

@click.command()
@click.option('--platform', '-p', type=click.Choice(['reddit', 'mastodon', 'all']),
              help='Which platform to set up')
@click.pass_context
def setup(ctx, platform):
    """
    Interactive setup wizard for API keys.
    
    Guides you through setting up free API access for Reddit and Mastodon.
    
    Examples:
    \b
        datadagger setup
        datadagger setup --platform reddit
        datadagger setup --platform mastodon
    """
    verbose = ctx.obj.get('verbose', False)
    
    console.print(Panel.fit(
        "[bold green]🚀 DataDagger Setup Wizard[/bold green]\n"
        "Let's get you set up with FREE APIs!",
        border_style="green"
    ))
    
    # Check if .env exists
    env_path = '.env'
    if not os.path.exists(env_path):
        if Confirm.ask("No .env file found. Create one from template?"):
            import shutil
            shutil.copy('.env.example', env_path)
            console.print("✅ Created .env file")
        else:
            console.print("❌ Setup cancelled")
            return
    
    # Determine which platforms to set up
    if platform is None:
        platform = Prompt.ask(
            "Which platform would you like to set up?",
            choices=['reddit', 'mastodon', 'all'],
            default='all'
        )
    
    if platform in ['reddit', 'all']:
        _setup_reddit()
    
    if platform in ['mastodon', 'all']:
        _setup_mastodon()
    
    # Final verification
    console.print(f"\n[green]🎉 Setup complete![/green]")
    console.print("Run 'datadagger config' to verify your configuration")
    console.print("Try 'datadagger demo' to see DataDagger in action")

def _setup_reddit():
    """Set up Reddit API"""
    console.print(f"\n[blue]🤖 Setting up Reddit API (FREE)[/blue]")
    
    # Instructions
    console.print("Reddit provides free API access for personal use.")
    console.print("You'll need to create a 'script' application.")
    
    if Confirm.ask("Open Reddit Apps page in browser?", default=True):
        webbrowser.open("https://www.reddit.com/prefs/apps/")
    
    console.print("\n[yellow]Steps:[/yellow]")
    console.print("1. Click 'Create App' or 'Create Another App'")
    console.print("2. Choose 'script' as the app type")
    console.print("3. Fill in any name and description")
    console.print("4. Set redirect URI to: http://localhost:8080")
    console.print("5. Click 'Create app'")
    
    # Get credentials
    console.print(f"\n[cyan]Enter your Reddit API credentials:[/cyan]")
    
    client_id = Prompt.ask(
        "Client ID (appears under your app name, looks like: 'abc123XYZ')",
        password=False
    )
    
    client_secret = Prompt.ask(
        "Client Secret (the 'secret' field)",
        password=True
    )
    
    # Update .env file
    _update_env_file('REDDIT_CLIENT_ID', client_id)
    _update_env_file('REDDIT_CLIENT_SECRET', client_secret)
    
    console.print("✅ Reddit API configured!")

def _setup_mastodon():
    """Set up Mastodon API"""
    console.print(f"\n[blue]🐘 Setting up Mastodon API (FREE)[/blue]")
    
    # Choose instance
    console.print("Mastodon is decentralized - you need to choose an instance.")
    console.print("Popular instances:")
    console.print("• mastodon.social (general purpose)")
    console.print("• fosstodon.org (FOSS community)")
    console.print("• infosec.exchange (security focused)")
    console.print("• hachyderm.io (tech community)")
    
    instance_url = Prompt.ask(
        "Mastodon instance URL",
        default="https://mastodon.social"
    )
    
    # Ensure proper format
    if not instance_url.startswith('http'):
        instance_url = f"https://{instance_url}"
    if instance_url.endswith('/'):
        instance_url = instance_url[:-1]
    
    # Update .env
    _update_env_file('MASTODON_INSTANCE_URL', instance_url)
    
    console.print(f"✅ Mastodon instance set to: {instance_url}")
    
    # Access token (optional)
    if Confirm.ask("Do you want to set up an access token for private data access?", default=False):
        if Confirm.ask("Open Mastodon settings in browser?", default=True):
            webbrowser.open(f"{instance_url}/settings/applications")
        
        console.print("\n[yellow]Steps for access token:[/yellow]")
        console.print("1. Go to Preferences → Development")
        console.print("2. Click 'New Application'")
        console.print("3. Fill in application name (e.g., 'DataDagger')")
        console.print("4. Select required scopes (read:statuses is minimum)")
        console.print("5. Click 'Submit'")
        console.print("6. Copy the access token")
        
        access_token = Prompt.ask(
            "Access Token (optional - leave blank for public data only)",
            default="",
            password=True
        )
        
        if access_token:
            _update_env_file('MASTODON_ACCESS_TOKEN', access_token)
            console.print("✅ Mastodon access token configured!")
        else:
            console.print("ℹ️  Using public data access only")
    else:
        console.print("ℹ️  Using public data access only")

def _update_env_file(key, value):
    """Update or add a key-value pair in .env file"""
    env_path = '.env'
    
    # Read existing content
    lines = []
    key_found = False
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    # Update existing key or mark for addition
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            key_found = True
            break
    
    # Add new key if not found
    if not key_found:
        lines.append(f'{key}={value}\n')
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(lines)

def _show_twitter_info():
    """Show information about Twitter's paid API"""
    console.print(f"\n[red]💰 Twitter API (PAID - $100+/month)[/red]")
    console.print("Twitter discontinued free API access in February 2023.")
    console.print("Current pricing:")
    console.print("• Basic: $100/month (10K tweets)")
    console.print("• Pro: $5,000/month (1M tweets)")
    console.print("• Enterprise: Custom pricing")
    
    if Confirm.ask("Open Twitter API pricing page?", default=False):
        webbrowser.open("https://developer.twitter.com/en/products/twitter-api")
