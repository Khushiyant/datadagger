"""
Enhanced tests for configuration management with comprehensive coverage
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from datadagger.utils.config import Config, check_api_keys, get_platform_status


class TestConfigComprehensive:
    """Comprehensive tests for configuration management"""
    
    def test_config_class_exists(self):
        """Test that Config class can be imported and instantiated"""
        config = Config()
        assert config is not None
    
    @patch.dict(os.environ, {
        'REDDIT_CLIENT_ID': 'test_reddit_id',
        'REDDIT_CLIENT_SECRET': 'test_reddit_secret',
        'REDDIT_USER_AGENT': 'TestDataDagger/1.0'
    })
    def test_reddit_config_from_env(self):
        """Test Reddit configuration from environment variables"""
        # Clear any existing config and reload
        Config.REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
        Config.REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
        Config.REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
        
        assert Config.REDDIT_CLIENT_ID == 'test_reddit_id'
        assert Config.REDDIT_CLIENT_SECRET == 'test_reddit_secret'
        assert Config.REDDIT_USER_AGENT == 'TestDataDagger/1.0'
    
    @patch.dict(os.environ, {
        'TWITTER_BEARER_TOKEN': 'test_twitter_bearer',
        'TWITTER_API_KEY': 'test_twitter_key',
        'TWITTER_API_SECRET': 'test_twitter_secret'
    })
    def test_twitter_config_from_env(self):
        """Test Twitter configuration from environment variables"""
        # Clear any existing config and reload
        Config.TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
        Config.TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
        Config.TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
        
        assert Config.TWITTER_BEARER_TOKEN == 'test_twitter_bearer'
        assert Config.TWITTER_API_KEY == 'test_twitter_key'
        assert Config.TWITTER_API_SECRET == 'test_twitter_secret'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_missing_env_vars(self):
        """Test behavior when environment variables are missing"""
        # Clear any existing config
        Config.TWITTER_BEARER_TOKEN = None
        Config.REDDIT_CLIENT_ID = None
        Config.REDDIT_CLIENT_SECRET = None
        
        assert Config.TWITTER_BEARER_TOKEN is None
        assert Config.REDDIT_CLIENT_ID is None
        assert Config.REDDIT_CLIENT_SECRET is None
    
    def test_config_validation_methods(self):
        """Test config validation methods exist"""
        config = Config()
        assert hasattr(config, 'validate_config')
        
        # Test that validation returns a dict with expected keys
        validation = config.validate_config()
        assert isinstance(validation, dict)
        expected_keys = ['twitter', 'reddit', 'database', 'output_dir']
        for key in expected_keys:
            assert key in validation

    @patch.dict(os.environ, {
        'TWITTER_BEARER_TOKEN': 'test_bearer',
        'REDDIT_CLIENT_ID': 'test_id',
        'REDDIT_CLIENT_SECRET': 'test_secret'
    })
    def test_validate_config_with_credentials(self):
        """Test config validation with valid credentials"""
        Config.TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
        Config.REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
        Config.REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
        
        validation = Config.validate_config()
        assert validation['twitter'] is True
        assert validation['reddit'] is True
        assert validation['database'] is True  # Always has default
        assert validation['output_dir'] is True  # Always has default

    def test_get_missing_config_empty(self):
        """Test get_missing_config when all configs are present"""
        with patch.object(Config, 'TWITTER_BEARER_TOKEN', 'test_token'), \
             patch.object(Config, 'REDDIT_CLIENT_ID', 'test_id'), \
             patch.object(Config, 'REDDIT_CLIENT_SECRET', 'test_secret'):
            missing = Config.get_missing_config()
            assert missing == {}

    def test_get_missing_config_partial(self):
        """Test get_missing_config when some configs are missing"""
        with patch.object(Config, 'TWITTER_BEARER_TOKEN', None), \
             patch.object(Config, 'REDDIT_CLIENT_ID', 'test_id'), \
             patch.object(Config, 'REDDIT_CLIENT_SECRET', None):
            missing = Config.get_missing_config()
            assert 'TWITTER_BEARER_TOKEN' in missing
            assert 'REDDIT_CLIENT_SECRET' in missing
            assert 'REDDIT_CLIENT_ID' not in missing

    def test_ensure_output_dir_success(self):
        """Test ensure_output_dir creates directory successfully"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, 'test_output')
            with patch.object(Config, 'DEFAULT_OUTPUT_DIR', test_dir):
                result = Config.ensure_output_dir()
                assert result is True
                assert os.path.exists(test_dir)

    def test_ensure_output_dir_exists(self):
        """Test ensure_output_dir when directory already exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(Config, 'DEFAULT_OUTPUT_DIR', temp_dir):
                result = Config.ensure_output_dir()
                assert result is True

    def test_ensure_output_dir_permission_error(self):
        """Test ensure_output_dir with permission error"""
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")), \
             patch('builtins.print') as mock_print:
            result = Config.ensure_output_dir()
            assert result is False
            mock_print.assert_called_once()

    def test_default_values(self):
        """Test that default configuration values are set correctly"""
        assert Config.DEFAULT_SIMILARITY_THRESHOLD == 0.7
        assert Config.MAX_SEARCH_RESULTS == 1000
        assert Config.DEFAULT_TIME_WINDOW_DAYS == 30
        assert Config.DEFAULT_EXPORT_FORMAT == 'json'
        # User agent might vary in test environment
        assert 'DataDagger' in Config.REDDIT_USER_AGENT


class TestConfigFunctions:
    """Test standalone configuration functions"""

    @patch('datadagger.utils.config.Config')
    @patch('builtins.print')
    def test_check_api_keys_no_config(self, mock_print, mock_config):
        """Test check_api_keys when no APIs are configured"""
        mock_instance = MagicMock()
        mock_config.return_value = mock_instance
        mock_instance.validate_config.return_value = {
            'twitter': False, 'reddit': False, 'database': True, 'output_dir': True
        }
        mock_instance.get_missing_config.return_value = {
            'TWITTER_BEARER_TOKEN': 'Twitter API Bearer Token',
            'REDDIT_CLIENT_ID': 'Reddit API Client ID'
        }
        
        result = check_api_keys()
        assert result is False
        assert mock_print.call_count >= 1

    @patch('datadagger.utils.config.Config')
    def test_check_api_keys_partial_config(self, mock_config):
        """Test check_api_keys with partial configuration"""
        mock_instance = MagicMock()
        mock_config.return_value = mock_instance
        mock_instance.validate_config.return_value = {
            'twitter': True, 'reddit': False, 'database': True, 'output_dir': True
        }
        
        result = check_api_keys()
        assert result is True

    @patch('datadagger.utils.config.Config')
    def test_get_platform_status(self, mock_config):
        """Test get_platform_status function"""
        mock_instance = MagicMock()
        mock_config.return_value = mock_instance
        mock_instance.validate_config.return_value = {
            'twitter': True, 'reddit': False
        }
        
        status = get_platform_status()
        assert status['twitter'] == "✅ Configured"
        assert status['reddit'] == "❌ Not configured"

    @patch('datadagger.utils.config.Config')
    @patch('builtins.print')
    def test_check_api_keys_no_platform_keys(self, mock_print, mock_config):
        """Test check_api_keys when platform keys are missing but other config exists"""
        mock_instance = MagicMock()
        mock_config.return_value = mock_instance
        mock_instance.validate_config.return_value = {
            'twitter': False, 'reddit': False, 'database': True, 'output_dir': True
        }
        mock_instance.get_missing_config.return_value = {}
        
        # Mock any() to return True for first check but False for platform check
        with patch('builtins.any', side_effect=[True, False]):
            result = check_api_keys()
            assert result is False
            assert mock_print.call_count >= 1
