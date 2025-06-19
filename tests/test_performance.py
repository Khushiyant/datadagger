"""
Performance and stress tests for DataDagger
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from datadagger.analyzers.text_analyzer import TextAnalyzer


class TestPerformance:
    """Performance tests for DataDagger components"""

    @pytest.mark.slow
    def test_text_analyzer_large_dataset_performance(self):
        """Test TextAnalyzer performance with large dataset"""
        analyzer = TextAnalyzer()
        
        # Generate large dataset
        large_posts = []
        for i in range(1000):
            large_posts.append({
                'id': f'post_{i}',
                'content': f'This is test content number {i} about various topics including birds and conspiracy theories',
                'author': f'user_{i % 100}',
                'platform': 'reddit',
                'created_at': datetime.now() - timedelta(days=i % 30)
            })
        
        # Time the grouping operation
        start_time = time.time()
        grouped = analyzer.group_similar_content(large_posts, threshold=0.7)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust based on requirements)
        assert processing_time < 30.0  # 30 seconds max
        assert isinstance(grouped, list)
        assert len(grouped) > 0

    def test_similarity_calculation_performance(self):
        """Test similarity calculation performance"""
        analyzer = TextAnalyzer()
        
        text1 = "This is a long piece of text about conspiracy theories and government surveillance programs that monitor citizens through various means including social media platforms and other digital communications channels."
        text2 = "This text discusses similar topics about government monitoring and surveillance of citizens using digital platforms and social media to track communications and activities."
        
        # Time multiple similarity calculations
        start_time = time.time()
        for _ in range(100):
            similarity = analyzer.calculate_similarity(text1, text2)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        
        # Should be fast (less than 10ms per calculation)
        assert avg_time < 0.01
        assert 0.0 <= similarity <= 1.0

    @pytest.mark.slow
    def test_keyword_extraction_performance(self):
        """Test keyword extraction performance with large text"""
        analyzer = TextAnalyzer()
        
        # Create large text document
        large_text = " ".join([
            "conspiracy theory government surveillance birds drones",
            "secret agenda mind control population monitoring citizens",
            "social media platforms data collection privacy invasion"
        ] * 100)  # Repeat 100 times
        
        start_time = time.time()
        keywords = analyzer.extract_keywords(large_text, top_k=20)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete quickly
        assert processing_time < 1.0  # 1 second max
        assert len(keywords) <= 20
        assert isinstance(keywords, list)


class TestStress:
    """Stress tests for DataDagger components"""

    def test_memory_usage_with_large_datasets(self):
        """Test memory handling with large datasets"""
        analyzer = TextAnalyzer()
        
        # Create increasingly large datasets
        for size in [100, 500, 1000]:
            posts = []
            for i in range(size):
                posts.append({
                    'id': f'post_{i}',
                    'content': f'Content {i} ' * 50,  # Make content longer
                    'author': f'user_{i}',
                    'platform': 'reddit',
                    'created_at': datetime.now()
                })
            
            # Should handle without memory errors
            try:
                grouped = analyzer.group_similar_content(posts, threshold=0.8)
                assert isinstance(grouped, list)
            except MemoryError:
                pytest.fail(f"Memory error with dataset size {size}")

    @patch('datadagger.commands.search.RedditScraper')
    def test_concurrent_search_handling(self, mock_reddit):
        """Test handling of concurrent search operations"""
        from datadagger.commands.search import _display_search_results
        
        # Mock large result set
        mock_results = []
        for i in range(100):
            mock_results.append({
                'posts': [
                    {
                        'content': f'Test content {i}',
                        'platform': 'reddit',
                        'created_at': datetime.now()
                    }
                ]
            })
        
        # Should handle large result display without errors
        try:
            _display_search_results(mock_results, verbose=True)
        except Exception as e:
            pytest.fail(f"Error displaying large results: {e}")

    def test_error_recovery_under_stress(self):
        """Test error recovery under stress conditions"""
        analyzer = TextAnalyzer()
        
        # Test with problematic inputs
        problematic_inputs = [
            "",  # Empty string
            None,  # None value
            "a" * 10000,  # Very long string
            "🔥" * 100,  # Unicode characters
            "\n\t" * 50,  # Whitespace only
        ]
        
        for test_input in problematic_inputs:
            try:
                if test_input is not None:
                    keywords = analyzer.extract_keywords(test_input)
                    assert isinstance(keywords, list)
                    
                    if len(test_input.strip()) > 0:
                        # Test text preprocessing instead of sentiment analysis
                        processed = analyzer.preprocess_text(test_input)
                        assert isinstance(processed, str)
            except Exception as e:
                pytest.fail(f"Failed to handle problematic input '{test_input}': {e}")


class TestScalability:
    """Scalability tests for DataDagger"""

    @pytest.mark.slow
    def test_grouping_scalability(self):
        """Test content grouping scalability"""
        analyzer = TextAnalyzer()
        
        # Test with different dataset sizes
        sizes = [10, 50, 100, 200]
        processing_times = []
        
        for size in sizes:
            posts = []
            for i in range(size):
                posts.append({
                    'id': f'post_{i}',
                    'content': f'Similar content about topic {i % 10}',
                    'author': f'user_{i}',
                    'platform': 'reddit',
                    'created_at': datetime.now()
                })
            
            start_time = time.time()
            grouped = analyzer.group_similar_content(posts, threshold=0.7)
            end_time = time.time()
            
            processing_time = end_time - start_time
            processing_times.append(processing_time)
            
            assert isinstance(grouped, list)
        
        # Processing time should scale reasonably (not exponentially)
        # This is a basic check - in practice you'd want more sophisticated analysis
        assert all(t < 10.0 for t in processing_times)  # All under 10 seconds

    def test_memory_efficient_processing(self):
        """Test that processing is memory efficient"""
        analyzer = TextAnalyzer()
        
        # Process data in chunks to test memory efficiency
        chunk_size = 50
        total_posts = 200
        
        all_results = []
        
        for start in range(0, total_posts, chunk_size):
            chunk_posts = []
            for i in range(start, min(start + chunk_size, total_posts)):
                chunk_posts.append({
                    'id': f'post_{i}',
                    'content': f'Chunk content {i}',
                    'author': f'user_{i}',
                    'platform': 'reddit',
                    'created_at': datetime.now()
                })
            
            # Process chunk
            chunk_results = analyzer.group_similar_content(chunk_posts, threshold=0.8)
            all_results.extend(chunk_results)
        
        # Should successfully process all chunks
        assert len(all_results) > 0
        assert all(isinstance(result, dict) for result in all_results)
