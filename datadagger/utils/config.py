"""
Configuration management utilities
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for DataDagger"""
    
    # API Configuration
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'DataDagger/1.0')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///datadagger.db')
    
    # Output Configuration
    DEFAULT_OUTPUT_DIR = os.getenv('DEFAULT_OUTPUT_DIR', './output')
    DEFAULT_EXPORT_FORMAT = os.getenv('DEFAULT_EXPORT_FORMAT', 'json')
    
    # Analysis Configuration
    DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv('DEFAULT_SIMILARITY_THRESHOLD', '0.7'))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '1000'))
    DEFAULT_TIME_WINDOW_DAYS = int(os.getenv('DEFAULT_TIME_WINDOW_DAYS', '30'))
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """
        Validate configuration and return status
        
        Returns:
            Dictionary with validation status for each service
        """
        validation = {
            'twitter': bool(cls.TWITTER_BEARER_TOKEN),
            'reddit': bool(cls.REDDIT_CLIENT_ID and cls.REDDIT_CLIENT_SECRET),
            'database': bool(cls.DATABASE_URL),
            'output_dir': bool(cls.DEFAULT_OUTPUT_DIR)
        }
        
        return validation
    
    @classmethod
    def get_missing_config(cls) -> Dict[str, str]:
        """
        Get missing configuration items with descriptions
        
        Returns:
            Dictionary of missing config items and their descriptions
        """
        missing = {}
        
        if not cls.TWITTER_BEARER_TOKEN:
            missing['TWITTER_BEARER_TOKEN'] = 'Twitter API Bearer Token for accessing Twitter API v2'
        
        if not cls.REDDIT_CLIENT_ID:
            missing['REDDIT_CLIENT_ID'] = 'Reddit API Client ID for accessing Reddit API'
        
        if not cls.REDDIT_CLIENT_SECRET:
            missing['REDDIT_CLIENT_SECRET'] = 'Reddit API Client Secret for accessing Reddit API'
        
        return missing
    
    @classmethod
    def ensure_output_dir(cls) -> bool:
        """
        Ensure output directory exists
        
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(cls.DEFAULT_OUTPUT_DIR, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating output directory: {str(e)}")
            return False

# Configuration validation functions
def check_api_keys() -> bool:
    """Check if required API keys are configured"""
    config = Config()
    validation = config.validate_config()
    
    if not any(validation.values()):
        print("⚠️  No API keys configured. Please set up your .env file.")
        missing = config.get_missing_config()
        for key, description in missing.items():
            print(f"   {key}: {description}")
        return False
    
    if not validation['twitter'] and not validation['reddit']:
        print("⚠️  No platform API keys configured. You need at least one of:")
        print("   - Twitter API credentials")
        print("   - Reddit API credentials")
        return False
    
    return True

def get_platform_status() -> Dict[str, str]:
    """Get status of each platform's configuration"""
    config = Config()
    validation = config.validate_config()
    
    status = {}
    status['twitter'] = "✅ Configured" if validation['twitter'] else "❌ Not configured"
    status['reddit'] = "✅ Configured" if validation['reddit'] else "❌ Not configured"
    
    return status
