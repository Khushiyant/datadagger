"""
Mastodon scraper - Free alternative to Twitter API
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

class MastodonScraper:
    """Scraper for Mastodon using the free Mastodon API"""
    
    def __init__(self, instance_url: str = None):
        """Initialize Mastodon API client"""
        self.instance_url = instance_url or os.getenv('MASTODON_INSTANCE_URL', 'https://mastodon.social')
        self.access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        
        # Remove trailing slash
        if self.instance_url.endswith('/'):
            self.instance_url = self.instance_url[:-1]
        
        self.headers = {}
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search(self, query: str, start_date: datetime, end_date: datetime, 
               limit: int = 100) -> List[Dict]:
        """
        Search Mastodon for posts matching the query within date range
        
        Args:
            query: Search term, hashtag, or phrase
            start_date: Start of search period
            end_date: End of search period
            limit: Maximum number of results
            
        Returns:
            List of post dictionaries
        """
        results = []
        
        try:
            # Mastodon search endpoint
            search_url = f"{self.instance_url}/api/v2/search"
            
            params = {
                'q': query,
                'type': 'statuses',  # Only search for posts
                'limit': min(40, limit),  # Mastodon API limit is 40
                'resolve': 'true'
            }
            
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                statuses = data.get('statuses', [])
                
                for status in statuses:
                    # Parse creation date
                    created_at = datetime.fromisoformat(
                        status['created_at'].replace('Z', '+00:00')
                    ).replace(tzinfo=None)
                    
                    # Check if post is within date range
                    if start_date <= created_at <= end_date:
                        post_data = {
                            'id': status['id'],
                            'content': self._clean_content(status['content']),
                            'author': status['account']['username'],
                            'author_display_name': status['account']['display_name'],
                            'created_at': created_at,
                            'reblogs_count': status.get('reblogs_count', 0),
                            'favourites_count': status.get('favourites_count', 0),
                            'replies_count': status.get('replies_count', 0),
                            'url': status['url'],
                            'platform': 'mastodon',
                            'post_type': 'status',
                            'instance': self.instance_url,
                            'language': status.get('language', 'unknown'),
                            'sensitive': status.get('sensitive', False)
                        }
                        
                        results.append(post_data)
                        
                        if len(results) >= limit:
                            break
                
                # Rate limiting - be respectful
                time.sleep(0.5)
                
            else:
                print(f"Error searching Mastodon: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error searching Mastodon: {str(e)}")
            
        return results
    
    def get_public_timeline(self, limit: int = 50, local: bool = False) -> List[Dict]:
        """
        Get posts from the public timeline
        
        Args:
            limit: Maximum number of posts
            local: If True, only local posts; if False, federated timeline
            
        Returns:
            List of post dictionaries
        """
        try:
            timeline_url = f"{self.instance_url}/api/v1/timelines/public"
            
            params = {
                'limit': min(40, limit),
                'local': str(local).lower()
            }
            
            response = self.session.get(timeline_url, params=params)
            
            if response.status_code == 200:
                statuses = response.json()
                results = []
                
                for status in statuses:
                    created_at = datetime.fromisoformat(
                        status['created_at'].replace('Z', '+00:00')
                    ).replace(tzinfo=None)
                    
                    post_data = {
                        'id': status['id'],
                        'content': self._clean_content(status['content']),
                        'author': status['account']['username'],
                        'author_display_name': status['account']['display_name'],
                        'created_at': created_at,
                        'reblogs_count': status.get('reblogs_count', 0),
                        'favourites_count': status.get('favourites_count', 0),
                        'replies_count': status.get('replies_count', 0),
                        'url': status['url'],
                        'platform': 'mastodon',
                        'post_type': 'status',
                        'instance': self.instance_url,
                        'language': status.get('language', 'unknown'),
                        'sensitive': status.get('sensitive', False)
                    }
                    
                    results.append(post_data)
                
                return results
                
            else:
                print(f"Error getting timeline: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting Mastodon timeline: {str(e)}")
            return []
    
    def search_hashtag(self, hashtag: str, limit: int = 50) -> List[Dict]:
        """
        Search for posts with a specific hashtag
        
        Args:
            hashtag: Hashtag to search for (with or without #)
            limit: Maximum results
            
        Returns:
            List of post dictionaries
        """
        # Ensure hashtag starts with #
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        # Use the search function
        return self.search(hashtag, datetime.now() - timedelta(days=30), datetime.now(), limit)
    
    def get_instance_info(self) -> Dict:
        """Get information about the Mastodon instance"""
        try:
            info_url = f"{self.instance_url}/api/v1/instance"
            response = self.session.get(info_url)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting instance info: {str(e)}")
            return {}
    
    def _clean_content(self, html_content: str) -> str:
        """Remove HTML tags from Mastodon content"""
        import re
        
        if not html_content:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        import html
        clean_text = html.unescape(clean_text)
        
        # Clean up whitespace
        clean_text = ' '.join(clean_text.split())
        
        return clean_text
    
    @classmethod
    def get_popular_instances(cls) -> List[str]:
        """Get a list of popular Mastodon instances"""
        return [
            'https://mastodon.social',
            'https://mastodon.online',
            'https://mas.to',
            'https://mstdn.social',
            'https://fosstodon.org',
            'https://infosec.exchange',
            'https://hachyderm.io',
            'https://tech.lgbt',
            'https://toot.community'
        ]
