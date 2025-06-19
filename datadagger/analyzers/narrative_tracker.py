"""
Narrative tracking and evolution analysis
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from collections import defaultdict

from ..scrapers.reddit_scraper import RedditScraper
from ..scrapers.twitter_scraper import TwitterScraper
from .text_analyzer import TextAnalyzer

class NarrativeTracker:
    """Track how narratives evolve over time across platforms"""
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        self.reddit_scraper = RedditScraper()
        self.twitter_scraper = TwitterScraper()
    
    def track_narrative_evolution(self, query: str, start_date: datetime, 
                                end_date: datetime, platforms: List[str], 
                                granularity: str = 'daily') -> List[Dict]:
        """
        Track narrative evolution over time
        
        Args:
            query: Search query/narrative to track
            start_date: Start of tracking period
            end_date: End of tracking period
            platforms: List of platforms to search
            granularity: Time granularity ('hourly', 'daily', 'weekly')
            
        Returns:
            Timeline data with narrative evolution
        """
        # Generate time intervals
        intervals = self._generate_time_intervals(start_date, end_date, granularity)
        
        timeline_data = []
        
        for interval_start, interval_end in intervals:
            interval_data = {
                'period': interval_start.strftime('%Y-%m-%d %H:%M'),
                'start_time': interval_start,
                'end_time': interval_end,
                'platforms': {},
                'total_volume': 0,
                'dominant_keywords': [],
                'sentiment_trend': 'neutral',
                'cross_platform_similarity': 0.0
            }
            
            all_posts = []
            
            # Collect data from each platform for this interval
            for platform in platforms:
                try:
                    if platform.lower() == 'reddit':
                        posts = self.reddit_scraper.search(query, interval_start, interval_end, 50)
                    elif platform.lower() == 'twitter':
                        posts = self.twitter_scraper.search(query, interval_start, interval_end, 50)
                    else:
                        posts = []
                    
                    platform_stats = self._analyze_platform_data(posts)
                    interval_data['platforms'][platform] = platform_stats
                    all_posts.extend(posts)
                    
                except Exception as e:
                    print(f"Error collecting data from {platform}: {str(e)}")
                    interval_data['platforms'][platform] = {
                        'post_count': 0,
                        'unique_authors': 0,
                        'avg_engagement': 0,
                        'keywords': []
                    }
            
            # Analyze combined data for this interval
            if all_posts:
                interval_data['total_volume'] = len(all_posts)
                
                # Extract dominant keywords
                combined_text = ' '.join([post.get('content', '') for post in all_posts])
                interval_data['dominant_keywords'] = self.text_analyzer.extract_keywords(combined_text, 5)
                
                # Calculate cross-platform similarity if multiple platforms
                if len([p for p in platforms if interval_data['platforms'][p]['post_count'] > 0]) > 1:
                    interval_data['cross_platform_similarity'] = self._calculate_cross_platform_similarity(
                        interval_data['platforms']
                    )
            
            timeline_data.append(interval_data)
        
        return timeline_data
    
    def _generate_time_intervals(self, start_date: datetime, end_date: datetime, 
                               granularity: str) -> List[tuple]:
        """Generate time intervals based on granularity"""
        intervals = []
        
        if granularity == 'hourly':
            delta = timedelta(hours=1)
        elif granularity == 'daily':
            delta = timedelta(days=1)
        elif granularity == 'weekly':
            delta = timedelta(weeks=1)
        else:
            delta = timedelta(days=1)  # Default to daily
        
        current = start_date
        while current < end_date:
            interval_end = min(current + delta, end_date)
            intervals.append((current, interval_end))
            current = interval_end
        
        return intervals
    
    def _analyze_platform_data(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze data from a single platform"""
        if not posts:
            return {
                'post_count': 0,
                'unique_authors': 0,
                'avg_engagement': 0,
                'keywords': []
            }
        
        # Count unique authors
        authors = set()
        total_engagement = 0
        
        for post in posts:
            if post.get('author'):
                authors.add(post['author'])
            
            # Calculate engagement based on platform
            if post.get('platform') == 'reddit':
                engagement = post.get('score', 0) + post.get('num_comments', 0)
            elif post.get('platform') == 'twitter':
                engagement = (post.get('like_count', 0) + 
                            post.get('retweet_count', 0) + 
                            post.get('reply_count', 0))
            else:
                engagement = 0
            
            total_engagement += engagement
        
        # Extract keywords
        combined_text = ' '.join([post.get('content', '') for post in posts])
        keywords = self.text_analyzer.extract_keywords(combined_text, 5)
        
        return {
            'post_count': len(posts),
            'unique_authors': len(authors),
            'avg_engagement': total_engagement / len(posts) if posts else 0,
            'keywords': keywords
        }
    
    def _calculate_cross_platform_similarity(self, platforms_data: Dict) -> float:
        """Calculate similarity of content across platforms"""
        platform_keywords = []
        
        for platform, data in platforms_data.items():
            if data['post_count'] > 0:
                platform_keywords.append(' '.join(data['keywords']))
        
        if len(platform_keywords) < 2:
            return 0.0
        
        # Calculate average pairwise similarity
        similarities = []
        for i in range(len(platform_keywords)):
            for j in range(i + 1, len(platform_keywords)):
                sim = self.text_analyzer.calculate_similarity(
                    platform_keywords[i], platform_keywords[j]
                )
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def identify_narrative_shifts(self, timeline_data: List[Dict], 
                                threshold: float = 0.3) -> List[Dict]:
        """
        Identify significant shifts in narrative content
        
        Args:
            timeline_data: Timeline data from track_narrative_evolution
            threshold: Minimum change threshold to consider a shift
            
        Returns:
            List of detected narrative shifts
        """
        shifts = []
        
        for i in range(1, len(timeline_data)):
            current = timeline_data[i]
            previous = timeline_data[i-1]
            
            # Compare keyword similarity between periods
            current_keywords = ' '.join(current['dominant_keywords'])
            previous_keywords = ' '.join(previous['dominant_keywords'])
            
            if current_keywords and previous_keywords:
                similarity = self.text_analyzer.calculate_similarity(
                    current_keywords, previous_keywords
                )
                
                # If similarity is below threshold, it's a potential shift
                if similarity < (1 - threshold):
                    shift = {
                        'period': current['period'],
                        'shift_magnitude': 1 - similarity,
                        'previous_keywords': previous['dominant_keywords'],
                        'new_keywords': current['dominant_keywords'],
                        'volume_change': current['total_volume'] - previous['total_volume'],
                        'description': self._describe_shift(previous['dominant_keywords'], 
                                                          current['dominant_keywords'])
                    }
                    shifts.append(shift)
        
        return shifts
    
    def _describe_shift(self, old_keywords: List[str], new_keywords: List[str]) -> str:
        """Generate human-readable description of narrative shift"""
        old_set = set(old_keywords)
        new_set = set(new_keywords)
        
        disappeared = old_set - new_set
        emerged = new_set - old_set
        
        description_parts = []
        
        if emerged:
            description_parts.append(f"New topics emerged: {', '.join(list(emerged)[:3])}")
        
        if disappeared:
            description_parts.append(f"Topics faded: {', '.join(list(disappeared)[:3])}")
        
        if not description_parts:
            description_parts.append("Subtle shift in narrative focus")
        
        return '; '.join(description_parts)
