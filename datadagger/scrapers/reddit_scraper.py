"""
Reddit scraper for collecting posts and comments
"""

import os
import praw
from datetime import datetime
from typing import List, Dict, Optional
import time

class RedditScraper:
    """Scraper for Reddit using PRAW (Python Reddit API Wrapper)"""
    
    def __init__(self):
        """Initialize Reddit API client"""
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'DataDagger/1.0')
        
        if not client_id or not client_secret:
            raise ValueError("Reddit API credentials not found. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in your .env file")
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def search(self, query: str, start_date: datetime, end_date: datetime, 
               limit: int = 100) -> List[Dict]:
        """
        Search Reddit for posts matching the query within date range
        
        Args:
            query: Search term or phrase
            start_date: Start of search period
            end_date: End of search period
            limit: Maximum number of results
            
        Returns:
            List of post dictionaries
        """
        results = []
        
        try:
            # Search across multiple subreddits
            subreddits = ['all']  # Start with r/all, can be expanded
            
            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search submissions
                for submission in subreddit.search(query, limit=limit, sort='new'):
                    created_date = datetime.fromtimestamp(submission.created_utc)
                    
                    if start_date <= created_date <= end_date:
                        post_data = {
                            'id': submission.id,
                            'title': submission.title,
                            'content': submission.selftext if submission.selftext else submission.title,
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'subreddit': submission.subreddit.display_name,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'created_at': created_date,
                            'url': submission.url,
                            'permalink': f"https://reddit.com{submission.permalink}",
                            'platform': 'reddit',
                            'post_type': 'submission'
                        }
                        results.append(post_data)
                
                # Add small delay to respect rate limits
                time.sleep(0.1)
                
                if len(results) >= limit:
                    break
        
        except Exception as e:
            print(f"Error searching Reddit: {str(e)}")
            
        return results[:limit]
    
    def get_comments(self, submission_id: str, limit: int = 50) -> List[Dict]:
        """
        Get comments for a specific submission
        
        Args:
            submission_id: Reddit submission ID
            limit: Maximum number of comments
            
        Returns:
            List of comment dictionaries
        """
        try:
            submission = self.reddit.submission(id=submission_id)
            submission.comments.replace_more(limit=0)  # Remove "more comments" objects
            
            comments = []
            for comment in submission.comments.list()[:limit]:
                if hasattr(comment, 'body') and comment.body != '[deleted]':
                    comment_data = {
                        'id': comment.id,
                        'content': comment.body,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'score': comment.score,
                        'created_at': datetime.fromtimestamp(comment.created_utc),
                        'parent_id': submission_id,
                        'platform': 'reddit',
                        'post_type': 'comment'
                    }
                    comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            print(f"Error getting comments: {str(e)}")
            return []
    
    def search_subreddit(self, subreddit_name: str, query: str, 
                        limit: int = 100) -> List[Dict]:
        """
        Search within a specific subreddit
        
        Args:
            subreddit_name: Name of the subreddit
            query: Search query
            limit: Maximum results
            
        Returns:
            List of post dictionaries
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            results = []
            
            for submission in subreddit.search(query, limit=limit):
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'content': submission.selftext if submission.selftext else submission.title,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': submission.subreddit.display_name,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_at': datetime.fromtimestamp(submission.created_utc),
                    'url': submission.url,
                    'permalink': f"https://reddit.com{submission.permalink}",
                    'platform': 'reddit',
                    'post_type': 'submission'
                }
                results.append(post_data)
            
            return results
            
        except Exception as e:
            print(f"Error searching subreddit {subreddit_name}: {str(e)}")
            return []
