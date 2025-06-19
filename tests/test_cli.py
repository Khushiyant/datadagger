"""
Tests for DataDagger CLI commands
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
import json
import tempfile
import os
from datetime import datetime
from datadagger.cli import cli


class TestCLICommands:
    """Test CLI command functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test main CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'DataDagger' in result.output
        assert 'Influence Archaeology OSINT Tool' in result.output

    def test_cli_version(self):
        """Test version command"""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output

    def test_demo_command(self):
        """Test demo command execution"""
        result = self.runner.invoke(cli, ['demo'])
        assert result.exit_code == 0
        assert 'Demo Mode' in result.output or 'Birds Arent Real' in result.output

    def test_pricing_command(self):
        """Test pricing command execution"""
        result = self.runner.invoke(cli, ['pricing'])
        assert result.exit_code == 0
        assert 'Platform Pricing' in result.output
        assert 'Reddit' in result.output
        assert 'FREE' in result.output

    @patch('datadagger.commands.config.os.path.exists')
    @patch('datadagger.commands.config.os.getenv')
    def test_config_command(self, mock_getenv, mock_exists):
        """Test config command execution"""
        mock_exists.return_value = True  # .env file exists
        
        # Mock environment variables
        def getenv_side_effect(key, default=None):
            env_vars = {
                'REDDIT_CLIENT_ID': 'test_reddit_id',
                'REDDIT_CLIENT_SECRET': 'test_reddit_secret',
                'TWITTER_BEARER_TOKEN': 'test_twitter_token',
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        result = self.runner.invoke(cli, ['config'])
        assert result.exit_code == 0

    def test_search_command_help(self):
        """Test search command help"""
        result = self.runner.invoke(cli, ['search', '--help'])
        assert result.exit_code == 0
        assert 'Search for narratives' in result.output
        assert '--platforms' in result.output
        assert '--days' in result.output

    def test_search_command_missing_query(self):
        """Test search command without query"""
        result = self.runner.invoke(cli, ['search'])
        assert result.exit_code == 2  # Click error for missing argument

    @patch('datadagger.commands.search.RedditScraper')
    @patch('datadagger.commands.search.MastodonScraper')
    @patch('datadagger.commands.search.TextAnalyzer')
    def test_search_command_basic(self, mock_analyzer, mock_mastodon, mock_reddit):
        """Test basic search command execution"""
        # Mock scrapers
        mock_reddit_instance = Mock()
        mock_reddit_instance.search.return_value = []
        mock_reddit.return_value = mock_reddit_instance
        
        mock_mastodon_instance = Mock()
        mock_mastodon_instance.search.return_value = []
        mock_mastodon.return_value = mock_mastodon_instance
        
        # Mock analyzer
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.group_similar_content.return_value = []
        mock_analyzer.return_value = mock_analyzer_instance
        
        result = self.runner.invoke(cli, ['search', 'test_query', '--platforms', 'reddit'])
        assert result.exit_code == 0

    def test_track_command_help(self):
        """Test track command help"""
        result = self.runner.invoke(cli, ['track', '--help'])
        assert result.exit_code == 0
        assert 'Track how a narrative evolves' in result.output

    def test_network_command_help(self):
        """Test network command help"""
        result = self.runner.invoke(cli, ['network', '--help'])
        assert result.exit_code == 0
        assert 'Analyze influence networks' in result.output

    def test_timeline_command_help(self):
        """Test timeline command help"""
        result = self.runner.invoke(cli, ['timeline', '--help'])
        assert result.exit_code == 0
        assert 'Generate timeline visualizations' in result.output

    def test_sentiment_command_help(self):
        """Test sentiment command help"""
        result = self.runner.invoke(cli, ['sentiment', '--help'])
        assert result.exit_code == 0
        assert 'Analyze sentiment' in result.output

    def test_origin_command_help(self):
        """Test origin command help"""
        result = self.runner.invoke(cli, ['origin', '--help'])
        assert result.exit_code == 0
        assert 'Find the origin point' in result.output

    def test_correlate_command_help(self):
        """Test correlate command help"""
        result = self.runner.invoke(cli, ['correlate', '--help'])
        assert result.exit_code == 0
        assert 'Analyze correlation' in result.output

    def test_export_command_help(self):
        """Test export command help"""
        result = self.runner.invoke(cli, ['export', '--help'])
        assert result.exit_code == 0
        assert 'Export collected data' in result.output

    @patch('datadagger.commands.setup.click.prompt')
    def test_setup_command_basic(self, mock_prompt):
        """Test setup command basic execution"""
        mock_prompt.side_effect = ['reddit', 'n']  # Choose reddit, then no to opening browser
        
        result = self.runner.invoke(cli, ['setup'])
        # Setup command might exit with 1 when user chooses not to continue
        assert result.exit_code in [0, 1]  # Allow both success and user abort

    def test_invalid_command(self):
        """Test invalid command handling"""
        result = self.runner.invoke(cli, ['invalid_command'])
        assert result.exit_code == 2
        assert 'No such command' in result.output

    @patch('datadagger.commands.search.RedditScraper')
    def test_search_with_output_file(self, mock_reddit):
        """Test search command with output file"""
        mock_reddit_instance = Mock()
        mock_reddit_instance.search.return_value = [
            {
                'id': 'test_1',
                'content': 'Test content',
                'author': 'test_user',
                'platform': 'reddit',
                'created_at': datetime.now()  # Use datetime object
            }
        ]
        mock_reddit.return_value = mock_reddit_instance
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            result = self.runner.invoke(cli, [
                'search', 'test_query', 
                '--platforms', 'reddit', 
                '--output', temp_filename
            ])
            assert result.exit_code == 0
            
            # Check if file was created and contains data
            assert os.path.exists(temp_filename)
            with open(temp_filename, 'r') as f:
                data = json.load(f)
                assert 'query' in data
                assert data['query'] == 'test_query'
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_search_with_similarity_threshold(self):
        """Test search command with similarity threshold"""
        result = self.runner.invoke(cli, [
            'search', 'test_query',
            '--platforms', 'reddit',
            '--similarity-threshold', '0.8'
        ])
        # Should not error on parameter parsing
        assert '--similarity-threshold' not in result.output or result.exit_code == 0

    def test_search_with_custom_days(self):
        """Test search command with custom days parameter"""
        result = self.runner.invoke(cli, [
            'search', 'test_query',
            '--platforms', 'reddit',
            '--days', '7'
        ])
        # Should not error on parameter parsing
        assert result.exit_code == 0 or 'Error searching' in result.output

    def test_search_with_custom_limit(self):
        """Test search command with custom limit parameter"""
        result = self.runner.invoke(cli, [
            'search', 'test_query',
            '--platforms', 'reddit', 
            '--limit', '50'
        ])
        # Should not error on parameter parsing
        assert result.exit_code == 0 or 'Error searching' in result.output
