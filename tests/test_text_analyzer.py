"""
Tests for DataDagger text analysis functionality
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from datadagger.analyzers.text_analyzer import TextAnalyzer


class TestTextAnalyzer:
    """Test TextAnalyzer functionality"""

    def test_initialization(self, text_analyzer):
        """Test TextAnalyzer initializes correctly"""
        assert text_analyzer is not None
        assert hasattr(text_analyzer, 'calculate_similarity')
        assert hasattr(text_analyzer, 'extract_keywords')

    def test_calculate_similarity_identical_text(self, text_analyzer):
        """Test similarity calculation for identical text"""
        text1 = "Birds aren't real - they're government surveillance drones!"
        text2 = "Birds aren't real - they're government surveillance drones!"
        
        similarity = text_analyzer.calculate_similarity(text1, text2)
        assert similarity >= 0.99  # Allow for floating point precision

    def test_calculate_similarity_different_text(self, text_analyzer):
        """Test similarity calculation for completely different text"""
        text1 = "Birds aren't real - they're government surveillance drones!"
        text2 = "I love eating pizza and watching movies on weekends"
        
        similarity = text_analyzer.calculate_similarity(text1, text2)
        assert similarity < 0.3  # Should be low similarity

    def test_calculate_similarity_similar_text(self, text_analyzer):
        """Test similarity calculation for similar text"""
        text1 = "Birds aren't real - they're government surveillance drones!"
        text2 = "Birds are not real - they are government surveillance devices!"
        
        similarity = text_analyzer.calculate_similarity(text1, text2)
        assert similarity > 0.25  # Lower threshold for this test case

    def test_extract_keywords_basic(self, text_analyzer):
        """Test keyword extraction from text"""
        text = "Birds aren't real conspiracy theory government surveillance drones secret agenda"
        
        keywords = text_analyzer.extract_keywords(text, top_k=5)
        assert len(keywords) <= 5
        assert all(isinstance(keyword, str) for keyword in keywords)
        # Should extract meaningful words, not stopwords
        assert 'the' not in keywords
        assert 'and' not in keywords

    def test_extract_keywords_empty_text(self, text_analyzer):
        """Test keyword extraction from empty text"""
        keywords = text_analyzer.extract_keywords("", top_k=5)
        assert keywords == []

    def test_group_similar_content(self, text_analyzer, sample_posts):
        """Test grouping similar content"""
        grouped = text_analyzer.group_similar_content(sample_posts, threshold=0.5)
        
        assert isinstance(grouped, list)
        assert len(grouped) > 0
        
        # Each group should have required structure
        for group in grouped:
            assert 'posts' in group
            assert 'similarity_score' in group
            assert isinstance(group['posts'], list)
            assert len(group['posts']) > 0

    def test_group_similar_content_empty_list(self, text_analyzer):
        """Test grouping with empty post list"""
        grouped = text_analyzer.group_similar_content([], threshold=0.5)
        assert grouped == []

    def test_group_similar_content_single_post(self, text_analyzer):
        """Test grouping with single post"""
        single_post = [{
            'id': 'test_1',
            'content': 'Test content',
            'author': 'test_user',
            'platform': 'reddit',
            'created_at': datetime.now()
        }]
        
        grouped = text_analyzer.group_similar_content(single_post, threshold=0.5)
        assert len(grouped) == 1
        assert len(grouped[0]['posts']) == 1

    @patch('datadagger.analyzers.text_analyzer.nltk')
    def test_handles_missing_nltk_data(self, mock_nltk, text_analyzer):
        """Test graceful handling when NLTK data is missing"""
        mock_nltk.download.side_effect = Exception("NLTK data not available")
        
        # Should not raise exception
        keywords = text_analyzer.extract_keywords("test content")
        assert isinstance(keywords, list)

    def test_detect_narrative_evolution_basic(self, text_analyzer):
        """Test narrative evolution detection"""
        posts = [
            {
                'id': 'post1',
                'content': 'Initial conspiracy theory about birds',
                'created_at': datetime.now() - timedelta(days=10),
                'platform': 'twitter'
            },
            {
                'id': 'post2', 
                'content': 'Birds surveillance drones government',
                'created_at': datetime.now() - timedelta(days=5),
                'platform': 'reddit'
            },
            {
                'id': 'post3',
                'content': 'Complete proof birds are not real',
                'created_at': datetime.now(),
                'platform': 'twitter'
            }
        ]
        
        evolution = text_analyzer.detect_narrative_evolution(posts)
        assert isinstance(evolution, dict)
        assert 'evolution_detected' in evolution
        assert 'stages' in evolution

    def test_preprocess_text_functionality(self, text_analyzer):
        """Test text preprocessing functionality"""
        dirty_text = "Check out this #amazing @user https://example.com content 123!"
        clean_text = text_analyzer.preprocess_text(dirty_text)
        
        # Should be lowercase
        assert clean_text.islower()
        # Should not contain URLs, mentions, hashtags, or numbers
        assert 'https://' not in clean_text
        assert '@' not in clean_text
        assert '#' not in clean_text
        assert '123' not in clean_text
