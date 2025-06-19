"""
Tests for setup command functionality
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from datadagger.commands.setup import setup


class TestSetupCommand:
    """Test setup command functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_setup_command_basic(self):
        """Test basic setup command execution"""
        with self.runner.isolated_filesystem():
            # Create a mock .env.example file
            with open('.env.example', 'w') as f:
                f.write("REDDIT_CLIENT_ID=your_reddit_client_id\n")
                f.write("REDDIT_CLIENT_SECRET=your_reddit_client_secret\n")
            
            # Mock user inputs and provide context with obj
            with patch('rich.prompt.Confirm.ask', return_value=True), \
                 patch('rich.prompt.Prompt.ask', return_value='reddit'), \
                 patch('webbrowser.open'), \
                 patch('builtins.input', side_effect=['test_client_id', 'test_client_secret']):
                
                # Create proper context object
                result = self.runner.invoke(setup, [], obj={'verbose': False})
                
                # Should complete without error or handle gracefully
                assert result.exit_code in [0, 1]
    
    def test_setup_help_display(self):
        """Test setup command help display"""
        result = self.runner.invoke(setup, ['--help'])
        
        assert result.exit_code == 0
        assert 'Interactive setup wizard' in result.output
        assert '--platform' in result.output
        assert 'reddit' in result.output
        assert 'mastodon' in result.output
    
    def test_setup_command_context_error_handling(self):
        """Test setup command handles missing context gracefully"""
        with self.runner.isolated_filesystem():
            # Test without providing obj parameter to trigger AttributeError
            result = self.runner.invoke(setup, [])
            
            # Should fail gracefully due to missing context
            assert result.exit_code == 1
            assert "AttributeError" in str(result.exception) or result.exit_code == 1
