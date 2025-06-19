"""
Tests for data storage and management utilities
"""

import pytest
import tempfile
import os
import json
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from datadagger.utils.data_store import DataStore


class TestDataStore:
    """Test data storage functionality"""
    
    def setup_method(self):
        """Set up test database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.data_store = DataStore(self.db_path)
    
    def teardown_method(self):
        """Clean up test database after each test"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_data_store_initialization(self):
        """Test DataStore initialization"""
        assert self.data_store is not None
        assert self.data_store.db_path == self.db_path
        assert os.path.exists(self.db_path)
    
    def test_data_store_default_path(self):
        """Test DataStore initialization with default path"""
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test.db'}):
            store = DataStore()
            assert store.db_path == 'test.db'
    
    def test_database_tables_created(self):
        """Test that database tables are created during initialization"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check posts table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
            assert cursor.fetchone() is not None
    
    def test_store_posts_basic(self):
        """Test storing posts to database"""
        posts = [
            {
                'id': 'test_post_1',
                'platform': 'reddit',
                'content': 'Test content 1',
                'author': 'test_user',
                'created_at': datetime.now(),
                'score': 10,
                'num_comments': 5
            },
            {
                'id': 'test_post_2',
                'platform': 'twitter',
                'content': 'Test content 2',
                'author': 'test_user2',
                'created_at': datetime.now(),
                'like_count': 15,
                'retweet_count': 3
            }
        ]
        
        result = self.data_store.store_posts(posts, 'test_query')
        assert result == 2
        
        # Verify posts were saved
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts WHERE query = ?", ('test_query',))
            count = cursor.fetchone()[0]
            assert count == 2
    
    def test_store_posts_empty_list(self):
        """Test storing empty list of posts"""
        result = self.data_store.store_posts([], 'test_query')
        assert result == 0
        
        # Verify no posts were saved
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts")
            count = cursor.fetchone()[0]
            assert count == 0
    
    def test_store_posts_with_metadata(self):
        """Test storing posts with metadata"""
        posts = [
            {
                'id': 'test_post_1',
                'platform': 'reddit',
                'content': 'Test content',
                'author': 'test_user',
                'created_at': datetime.now(),
                'subreddit': 'test_subreddit',
                'score': 100
            }
        ]
        
        result = self.data_store.store_posts(posts, 'test_query')
        assert result == 1
        
        # Verify metadata was saved as JSON
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT metadata FROM posts WHERE id = ?", ('test_post_1',))
            metadata = cursor.fetchone()[0]
            parsed_metadata = json.loads(metadata)
            assert parsed_metadata['subreddit'] == 'test_subreddit'
    
    def test_get_posts_by_query(self):
        """Test retrieving posts by query"""
        # Save some test posts
        posts = [
            {
                'id': 'query1_post1',
                'platform': 'reddit',
                'content': 'Content for query 1',
                'author': 'user1',
                'created_at': datetime.now()
            }
        ]
        self.data_store.store_posts(posts, 'query1')
        
        # Retrieve posts
        retrieved_posts = self.data_store.get_posts(query='query1')
        assert len(retrieved_posts) == 1
        assert retrieved_posts[0]['id'] == 'query1_post1'
        assert retrieved_posts[0]['content'] == 'Content for query 1'
    
    def test_get_posts_by_platform(self):
        """Test retrieving posts by platform"""
        # Save posts from different platforms
        reddit_posts = [
            {
                'id': 'reddit_post1',
                'platform': 'reddit',
                'content': 'Reddit content',
                'author': 'reddit_user',
                'created_at': datetime.now()
            }
        ]
        twitter_posts = [
            {
                'id': 'twitter_post1',
                'platform': 'twitter',
                'content': 'Twitter content',
                'author': 'twitter_user',
                'created_at': datetime.now()
            }
        ]
        
        self.data_store.store_posts(reddit_posts, 'test_query')
        self.data_store.store_posts(twitter_posts, 'test_query')
        
        # Retrieve Reddit posts only
        reddit_retrieved = self.data_store.get_posts(platform='reddit')
        assert len(reddit_retrieved) == 1
        assert reddit_retrieved[0]['platform'] == 'reddit'
        
        # Retrieve Twitter posts only
        twitter_retrieved = self.data_store.get_posts(platform='twitter')
        assert len(twitter_retrieved) == 1
        assert twitter_retrieved[0]['platform'] == 'twitter'
    
    def test_get_posts_with_date_filter(self):
        """Test retrieving posts with date filters"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        # Save posts with different dates
        posts = [
            {
                'id': 'old_post',
                'platform': 'reddit',
                'content': 'Old content',
                'author': 'user1',
                'created_at': yesterday
            },
            {
                'id': 'new_post',
                'platform': 'reddit',
                'content': 'New content',
                'author': 'user2',
                'created_at': now
            }
        ]
        
        self.data_store.store_posts(posts, 'date_test')
        
        # Get posts from today only
        recent_posts = self.data_store.get_posts(
            query='date_test',
            start_date=now - timedelta(hours=1)
        )
        assert len(recent_posts) == 1
        assert recent_posts[0]['id'] == 'new_post'
    
    def test_store_analysis(self):
        """Test storing analysis results"""
        analysis_results = {
            'similarity_score': 0.85,
            'keywords': ['test', 'analysis'],
            'summary': 'Test analysis summary'
        }
        
        analysis_params = {
            'threshold': 0.7,
            'method': 'cosine'
        }
        
        analysis_id = self.data_store.store_analysis(
            'similarity_analysis',
            'test_query',
            analysis_results,
            analysis_params
        )
        
        assert analysis_id is not None
        assert isinstance(analysis_id, int)
    
    def test_get_analysis_history(self):
        """Test retrieving analysis history"""
        # Store some analysis results
        analysis_results = {
            'score': 0.9,
            'keywords': ['history', 'test']
        }
        
        self.data_store.store_analysis(
            'test_analysis',
            'history_query',
            analysis_results
        )
        
        # Retrieve analysis history
        history = self.data_store.get_analysis_history(
            analysis_type='test_analysis'
        )
        
        assert len(history) >= 1
        assert history[0]['analysis_type'] == 'test_analysis'
        assert history[0]['query'] == 'history_query'
    
    def test_get_posts_with_limit(self):
        """Test retrieving posts with limit"""
        # Save multiple posts
        posts = [
            {
                'id': f'limit_test_{i}',
                'platform': 'reddit',
                'content': f'Content {i}',
                'author': f'user{i}',
                'created_at': datetime.now()
            }
            for i in range(10)
        ]
        
        self.data_store.store_posts(posts, 'limit_test')
        
        # Get only 5 posts
        limited_posts = self.data_store.get_posts(
            query='limit_test',
            limit=5
        )
        
        assert len(limited_posts) == 5
    
    def test_error_handling_json_decode(self):
        """Test error handling for invalid JSON metadata"""
        # Manually insert a post with invalid JSON metadata
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO posts (id, platform, content, author, created_at, metadata, query)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'invalid_json_post',
                'reddit',
                'Test content',
                'test_user',
                datetime.now(),
                'invalid json {',  # Invalid JSON
                'test_query'
            ))
            conn.commit()
        
        # Should handle invalid JSON gracefully
        posts = self.data_store.get_posts(query='test_query')
        assert len(posts) == 1
        assert posts[0]['id'] == 'invalid_json_post'
    
    def test_engagement_score_calculation(self):
        """Test engagement score calculation for different platforms"""
        # Test Reddit engagement calculation
        reddit_post = {
            'id': 'reddit_engagement',
            'platform': 'reddit',
            'content': 'Reddit content',
            'author': 'reddit_user',
            'created_at': datetime.now(),
            'score': 100,
            'num_comments': 25
        }
        
        # Test Twitter engagement calculation
        twitter_post = {
            'id': 'twitter_engagement',
            'platform': 'twitter',
            'content': 'Twitter content',
            'author': 'twitter_user',
            'created_at': datetime.now(),
            'like_count': 50,
            'retweet_count': 10,
            'reply_count': 5
        }
        
        self.data_store.store_posts([reddit_post, twitter_post], 'engagement_test')
        
        # Verify engagement scores were calculated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check Reddit engagement (score + comments)
            cursor.execute(
                "SELECT engagement_score FROM posts WHERE id = ?",
                ('reddit_engagement',)
            )
            reddit_engagement = cursor.fetchone()[0]
            assert reddit_engagement == 125  # 100 + 25
            
            # Check Twitter engagement (likes + retweets + replies)
            cursor.execute(
                "SELECT engagement_score FROM posts WHERE id = ?",
                ('twitter_engagement',)
            )
            twitter_engagement = cursor.fetchone()[0]
            assert twitter_engagement == 65  # 50 + 10 + 5
    
    def test_database_error_handling(self):
        """Test error handling for database operations"""
        posts = [
            {
                'id': 'error_test',
                'platform': 'reddit',
                'content': 'Test content',
                'author': 'test_user',
                'created_at': 'invalid_date'  # Invalid date
            }
        ]
        
        # Should handle errors gracefully
        result = self.data_store.store_posts(posts, 'error_test')
        # Should return 0 as no posts were successfully stored
        assert result == 0
