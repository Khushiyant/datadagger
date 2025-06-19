"""
Twitter scraper for collecting tweets and user data
"""

import os
import tweepy
from datetime import datetime
from typing import List, Dict, Optional
import time

class TwitterScraper:
    """Scraper for Twitter using Tweepy (Twitter API v2)"""
    
    def __init__(self):
        """Initialize Twitter API client"""
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        if not bearer_token:
            raise ValueError("Twitter Bearer Token not found. Please set TWITTER_BEARER_TOKEN in your .env file")
        
        self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    
    def search(self, query: str, start_date: datetime, end_date: datetime, 
               limit: int = 100) -> List[Dict]:
        """
        Search Twitter for tweets matching the query within date range
        
        Args:
            query: Search term, hashtag, or phrase
            start_date: Start of search period
            end_date: End of search period
            limit: Maximum number of results
            
        Returns:
            List of tweet dictionaries
        """
        results = []
        
        try:
            # Format dates for Twitter API
            start_time = start_date.isoformat()
            end_time = end_date.isoformat()
            
            # Search tweets
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                start_time=start_time,
                end_time=end_time,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations', 'lang'],
                user_fields=['username', 'name', 'verified', 'public_metrics'],
                expansions=['author_id'],
                max_results=min(100, limit)
            ).flatten(limit=limit)
            
            # Get user data from includes
            users_dict = {}
            
            for tweet in tweets:
                # Create tweet data
                tweet_data = {
                    'id': tweet.id,
                    'content': tweet.text,
                    'author_id': tweet.author_id,
                    'author_username': None,  # Will be filled from user data
                    'created_at': tweet.created_at,
                    'retweet_count': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                    'like_count': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                    'reply_count': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                    'quote_count': tweet.public_metrics.get('quote_count', 0) if tweet.public_metrics else 0,
                    'language': getattr(tweet, 'lang', 'unknown'),
                    'platform': 'twitter',
                    'post_type': 'tweet',
                    'url': f"https://twitter.com/i/web/status/{tweet.id}"
                }
                
                results.append(tweet_data)
        
        except Exception as e:
            print(f"Error searching Twitter: {str(e)}")
            
        return results
    
    def get_user_tweets(self, username: str, limit: int = 50) -> List[Dict]:
        """
        Get recent tweets from a specific user
        
        Args:
            username: Twitter username (without @)
            limit: Maximum number of tweets
            
        Returns:
            List of tweet dictionaries
        """
        try:
            # Get user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                return []
            
            user_id = user.data.id
            
            # Get user's tweets
            tweets = tweepy.Paginator(
                self.client.get_users_tweets,
                id=user_id,
                tweet_fields=['created_at', 'public_metrics', 'lang'],
                max_results=min(100, limit)
            ).flatten(limit=limit)
            
            results = []
            for tweet in tweets:
                tweet_data = {
                    'id': tweet.id,
                    'content': tweet.text,
                    'author_id': user_id,
                    'author_username': username,
                    'created_at': tweet.created_at,
                    'retweet_count': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                    'like_count': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                    'reply_count': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                    'quote_count': tweet.public_metrics.get('quote_count', 0) if tweet.public_metrics else 0,
                    'language': getattr(tweet, 'lang', 'unknown'),
                    'platform': 'twitter',
                    'post_type': 'tweet',
                    'url': f"https://twitter.com/{username}/status/{tweet.id}"
                }
                results.append(tweet_data)
            
            return results
            
        except Exception as e:
            print(f"Error getting user tweets for {username}: {str(e)}")
            return []
    
    def search_hashtag(self, hashtag: str, limit: int = 100) -> List[Dict]:
        """
        Search for tweets containing a specific hashtag
        
        Args:
            hashtag: Hashtag to search for (with or without #)
            limit: Maximum results
            
        Returns:
            List of tweet dictionaries
        """
        # Ensure hashtag starts with #
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        return self.search(hashtag, datetime.now().replace(day=1), datetime.now(), limit)
