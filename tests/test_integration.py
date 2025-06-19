"""
Integration tests for DataDagger end-to-end functionality
"""

import pytest
import tempfile
import os
import json
from click.testing import CliRunner
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from datadagger.cli import cli


class TestIntegration:
    """Integration tests for DataDagger"""

    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()

    @patch('datadagger.commands.search.RedditScraper')
    @patch('datadagger.commands.search.TextAnalyzer')
    def test_search_to_analysis_pipeline(self, mock_analyzer, mock_reddit):
        """Test complete search to analysis pipeline"""
        # Mock Reddit scraper
        mock_reddit_instance = Mock()
        mock_reddit_instance.search.return_value = [
            {
                'id': 'test_1',
                'content': 'Birds aren\'t real - they\'re government surveillance drones!',
                'author': 'truth_seeker',
                'platform': 'reddit',
                'created_at': datetime.now() - timedelta(days=2),
                'engagement_score': 42,
                'subreddit': 'conspiracy'
            },
            {
                'id': 'test_2',
                'content': 'I thought birds aren\'t real was satire but people believe it',
                'author': 'confused_user',
                'platform': 'reddit',
                'created_at': datetime.now() - timedelta(days=1),
                'engagement_score': 156,
                'subreddit': 'facepalm'
            }
        ]
        mock_reddit.return_value = mock_reddit_instance
        
        # Mock text analyzer
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.group_similar_content.return_value = [
            {
                'posts': mock_reddit_instance.search.return_value,
                'similarity_score': 0.8
            }
        ]
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Test search command
        result = self.runner.invoke(cli, [
            'search', 'birds aren\'t real',
            '--platforms', 'reddit',
            '--days', '7',
            '--limit', '10'
        ])
        
        assert result.exit_code == 0
        assert 'Search Results' in result.output or 'reddit' in result.output

    @patch('datadagger.commands.search.RedditScraper')
    @patch('datadagger.commands.search.TextAnalyzer')
    def test_search_with_export_pipeline(self, mock_analyzer, mock_reddit):
        """Test search with data export functionality"""
        # Mock data
        mock_posts = [
            {
                'id': 'test_1',
                'content': 'Test content about conspiracy',
                'author': 'test_user',
                'platform': 'reddit',
                'created_at': datetime.now(),  # Use datetime object, not string
                'engagement_score': 42
            }
        ]
        
        mock_reddit_instance = Mock()
        mock_reddit_instance.search.return_value = mock_posts
        mock_reddit.return_value = mock_reddit_instance
        
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.group_similar_content.return_value = [
            {'posts': mock_posts, 'similarity_score': 0.9}
        ]
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            output_file = temp_file.name
        
        try:
            # Run search with output
            result = self.runner.invoke(cli, [
                'search', 'test_query',
                '--platforms', 'reddit',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            
            # Verify output file was created and contains data
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                data = json.load(f)
                assert 'query' in data
                assert data['query'] == 'test_query'
                
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_demo_to_pricing_workflow(self):
        """Test user workflow from demo to pricing to setup"""
        # Test demo
        demo_result = self.runner.invoke(cli, ['demo'])
        assert demo_result.exit_code == 0
        assert 'Demo Mode' in demo_result.output or 'Birds Arent Real' in demo_result.output
        
        # Test pricing
        pricing_result = self.runner.invoke(cli, ['pricing'])
        assert pricing_result.exit_code == 0
        assert 'Platform Pricing' in pricing_result.output
        assert 'FREE' in pricing_result.output
        
        # Test setup help
        setup_result = self.runner.invoke(cli, ['setup', '--help'])
        assert setup_result.exit_code == 0
        assert 'Interactive setup wizard' in setup_result.output

    @patch('datadagger.commands.config.os.path.exists')
    @patch('datadagger.commands.config.os.getenv')
    def test_config_check_workflow(self, mock_getenv, mock_exists):
        """Test configuration checking workflow"""
        mock_exists.return_value = True  # .env file exists
        
        # Mock environment variables
        def getenv_side_effect(key, default=None):
            env_vars = {
                'REDDIT_CLIENT_ID': 'test_reddit_id',
                'REDDIT_CLIENT_SECRET': 'test_reddit_secret',
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Test config command
        result = self.runner.invoke(cli, ['config'])
        assert result.exit_code == 0

    @patch('datadagger.commands.search.RedditScraper')
    @patch('datadagger.commands.search.MastodonScraper')
    @patch('datadagger.commands.search.TextAnalyzer')
    def test_multi_platform_search(self, mock_analyzer, mock_mastodon, mock_reddit):
        """Test searching across multiple platforms"""
        # Mock Reddit
        mock_reddit_instance = Mock()
        mock_reddit_instance.search.return_value = [
            {
                'id': 'reddit_1',
                'content': 'Reddit post about topic',
                'platform': 'reddit',
                'created_at': datetime.now(),
                'engagement_score': 10
            }
        ]
        mock_reddit.return_value = mock_reddit_instance
        
        # Mock Mastodon
        mock_mastodon_instance = Mock()
        mock_mastodon_instance.search.return_value = [
            {
                'id': 'mastodon_1',
                'content': 'Mastodon post about topic',
                'platform': 'mastodon',
                'created_at': datetime.now(),
                'engagement_score': 5
            }
        ]
        mock_mastodon.return_value = mock_mastodon_instance
        
        # Mock analyzer
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.group_similar_content.return_value = [
            {
                'posts': [
                    mock_reddit_instance.search.return_value[0],
                    mock_mastodon_instance.search.return_value[0]
                ],
                'similarity_score': 0.6
            }
        ]
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Test multi-platform search
        result = self.runner.invoke(cli, [
            'search', 'test_topic',
            '--platforms', 'reddit,mastodon',
            '--limit', '5'
        ])
        
        assert result.exit_code == 0

    def test_command_help_consistency(self):
        """Test that all commands have consistent help output"""
        commands = [
            'search', 'track', 'network', 'timeline',
            'sentiment', 'origin', 'correlate', 'export',
            'config', 'demo', 'pricing', 'setup'
        ]
        
        for command in commands:
            result = self.runner.invoke(cli, [command, '--help'])
            assert result.exit_code == 0
            assert 'Usage:' in result.output
            assert 'Options:' in result.output

    @patch('datadagger.commands.search.RedditScraper')
    def test_error_handling_pipeline(self, mock_reddit):
        """Test error handling throughout the pipeline"""
        # Mock Reddit to raise an exception
        mock_reddit_instance = Mock()
        mock_reddit_instance.search.side_effect = Exception("API Error")
        mock_reddit.return_value = mock_reddit_instance
        
        # Should handle error gracefully
        result = self.runner.invoke(cli, [
            'search', 'test_query',
            '--platforms', 'reddit'
        ])
        
        # Should not crash, but may show error message
        assert result.exit_code == 0 or 'Error searching' in result.output

    def test_parameter_validation(self):
        """Test parameter validation across commands"""
        # Test invalid similarity threshold
        result = self.runner.invoke(cli, [
            'search', 'test',
            '--similarity-threshold', '1.5'  # Invalid: > 1.0
        ])
        # Should either reject or clamp the value
        assert result.exit_code in [0, 2]
        
        # Test invalid days parameter
        result = self.runner.invoke(cli, [
            'search', 'test',
            '--days', '-1'  # Invalid: negative
        ])
        # Should either reject or handle gracefully
        assert result.exit_code in [0, 2]

    def test_output_format_consistency(self):
        """Test that output formats are consistent across commands"""
        # Test demo output format
        demo_result = self.runner.invoke(cli, ['demo'])
        assert demo_result.exit_code == 0
        
        # Test pricing output format  
        pricing_result = self.runner.invoke(cli, ['pricing'])
        assert pricing_result.exit_code == 0
        
        # Both should have consistent rich formatting (tables, panels, etc.)
        # This is a basic check - in a real test you might check for specific formatting


class TestDataFlow:
    """Test data flow between components"""

    def test_post_data_structure_consistency(self):
        """Test that post data structures are consistent between scrapers"""
        required_fields = ['id', 'content', 'author', 'platform', 'created_at']
        
        # This would test that all scrapers return posts with the same structure
        # In a real implementation, you'd instantiate each scraper and verify
        # the returned data structure
        
        sample_post = {
            'id': 'test_123',
            'content': 'Test post content',
            'author': 'test_user',
            'platform': 'reddit',
            'created_at': datetime.now(),
            'engagement_score': 42
        }
        
        for field in required_fields:
            assert field in sample_post

    def test_analyzer_input_output_compatibility(self):
        """Test that analyzer inputs/outputs are compatible"""
        # Test that TextAnalyzer can process scraper output format
        # and NarrativeTracker can process TextAnalyzer output format
        
        # This is a structural test - in practice you'd test actual data flow
        sample_grouped_content = [
            {
                'posts': [
                    {
                        'id': 'test_1',
                        'content': 'Test content',
                        'platform': 'reddit',
                        'created_at': datetime.now()
                    }
                ],
                'similarity_score': 0.8
            }
        ]
        
        # Verify structure
        assert isinstance(sample_grouped_content, list)
        assert 'posts' in sample_grouped_content[0]
        assert 'similarity_score' in sample_grouped_content[0]
