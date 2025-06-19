"""
Test configuration and fixtures for DataDagger
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


@pytest.fixture
def sample_posts():
    """Sample posts for testing"""
    return [
        {
            'id': 'post_1',
            'content': 'Birds aren\'t real - they\'re government surveillance drones! #BirdsArentReal',
            'author': 'truth_seeker_2019',
            'platform': 'reddit',
            'created_at': datetime.now() - timedelta(days=5),
            'engagement_score': 42,
            'subreddit': 'conspiracy',
            'url': 'https://reddit.com/r/conspiracy/post_1'
        },
        {
            'id': 'post_2', 
            'content': 'I thought birds aren\'t real was satire but my nephew actually believes it now...',
            'author': 'confused_uncle',
            'platform': 'reddit',
            'created_at': datetime.now() - timedelta(days=3),
            'engagement_score': 156,
            'subreddit': 'facepalm',
            'url': 'https://reddit.com/r/facepalm/post_2'
        },
        {
            'id': 'post_3',
            'content': 'Documentary idea: How did \'Birds Aren\'t Real\' go from joke to belief system?',
            'author': 'doc_filmmaker',
            'platform': 'mastodon',
            'created_at': datetime.now() - timedelta(days=1),
            'engagement_score': 89,
            'instance': 'mastodon.social',
            'url': 'https://mastodon.social/@doc_filmmaker/post_3'
        }
    ]


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for config files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        'REDDIT_CLIENT_ID': 'test_reddit_id',
        'REDDIT_CLIENT_SECRET': 'test_reddit_secret',
        'REDDIT_USER_AGENT': 'DataDagger:Test:1.0.0',
        'MASTODON_ACCESS_TOKEN': 'test_mastodon_token',
        'MASTODON_API_BASE_URL': 'https://mastodon.social',
        'TWITTER_BEARER_TOKEN': 'test_twitter_bearer',
        'TWITTER_API_KEY': 'test_twitter_key',
        'TWITTER_API_SECRET': 'test_twitter_secret',
        'TWITTER_ACCESS_TOKEN': 'test_twitter_access',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_twitter_access_secret'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def text_analyzer():
    """Create TextAnalyzer instance for testing"""
    from datadagger.analyzers.text_analyzer import TextAnalyzer
    return TextAnalyzer()


@pytest.fixture
def mock_reddit_scraper():
    """Mock Reddit scraper"""
    scraper = Mock()
    scraper.search.return_value = [
        {
            'id': 'reddit_1',
            'content': 'Test reddit post content',
            'author': 'test_user',
            'platform': 'reddit',
            'created_at': datetime.now(),
            'engagement_score': 10,
            'subreddit': 'test'
        }
    ]
    return scraper


@pytest.fixture
def mock_mastodon_scraper():
    """Mock Mastodon scraper"""
    scraper = Mock()
    scraper.search.return_value = [
        {
            'id': 'mastodon_1',
            'content': 'Test mastodon post content',
            'author': 'test_user@mastodon.social',
            'platform': 'mastodon',
            'created_at': datetime.now(),
            'engagement_score': 5,
            'instance': 'mastodon.social'
        }
    ]
    return scraper


@pytest.fixture
def mock_twitter_scraper():
    """Mock Twitter scraper"""
    scraper = Mock()
    scraper.search.return_value = [
        {
            'id': 'twitter_1',
            'content': 'Test twitter post content',
            'author': 'test_user',
            'platform': 'twitter',
            'created_at': datetime.now(),
            'engagement_score': 20,
            'retweet_count': 5,
            'like_count': 15
        }
    ]
    return scraper
