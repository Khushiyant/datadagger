"""
Text analysis utilities for content similarity and clustering
"""

import re
import string
from typing import List, Dict, Any
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextAnalyzer:
    """Text analysis and similarity detection for social media content"""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text content
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags for similarity comparison
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove punctuation and numbers
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Tokenize and remove stop words
        tokens = word_tokenize(text)
        tokens = [self.stemmer.stem(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        try:
            processed_texts = [
                self.preprocess_text(text1),
                self.preprocess_text(text2)
            ]
            
            if not processed_texts[0] or not processed_texts[1]:
                return 0.0
            
            # Vectorize texts
            tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def group_similar_content(self, posts: List[Dict], threshold: float = 0.7) -> List[Dict]:
        """
        Group posts by content similarity
        
        Args:
            posts: List of post dictionaries
            threshold: Similarity threshold for grouping
            
        Returns:
            List of grouped posts
        """
        if not posts:
            return []
        
        # Preprocess all texts
        processed_texts = [self.preprocess_text(post.get('content', '')) for post in posts]
        
        # Filter out empty texts
        valid_indices = [i for i, text in enumerate(processed_texts) if text.strip()]
        if not valid_indices:
            return [{'posts': posts, 'similarity_score': 1.0}]
        
        valid_texts = [processed_texts[i] for i in valid_indices]
        valid_posts = [posts[i] for i in valid_indices]
        
        try:
            # Vectorize texts
            tfidf_matrix = self.vectorizer.fit_transform(valid_texts)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Use DBSCAN clustering
            clustering = DBSCAN(
                metric='precomputed', 
                eps=1-threshold,  # Convert similarity to distance
                min_samples=1
            )
            
            # Convert similarity to distance matrix
            distance_matrix = 1 - similarity_matrix
            labels = clustering.fit_predict(distance_matrix)
            
            # Group posts by cluster
            groups = {}
            for i, label in enumerate(labels):
                if label not in groups:
                    groups[label] = []
                groups[label].append(valid_posts[i])
            
            # Format results
            grouped_results = []
            for label, group_posts in groups.items():
                if len(group_posts) > 0:
                    # Calculate average similarity within group
                    group_indices = [valid_indices[valid_posts.index(post)] for post in group_posts]
                    group_similarities = []
                    
                    for i in range(len(group_indices)):
                        for j in range(i+1, len(group_indices)):
                            idx1, idx2 = group_indices[i], group_indices[j]
                            if idx1 < len(similarity_matrix) and idx2 < len(similarity_matrix):
                                group_similarities.append(similarity_matrix[idx1][idx2])
                    
                    avg_similarity = np.mean(group_similarities) if group_similarities else 1.0
                    
                    grouped_results.append({
                        'posts': group_posts,
                        'similarity_score': float(avg_similarity),
                        'cluster_id': int(label) if label != -1 else 'noise'
                    })
            
            # Sort by group size (largest first)
            grouped_results.sort(key=lambda x: len(x['posts']), reverse=True)
            
            return grouped_results
            
        except Exception as e:
            print(f"Error grouping content: {str(e)}")
            # Return each post as its own group
            return [{'posts': [post], 'similarity_score': 1.0} for post in posts]
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract key terms from text using TF-IDF
        
        Args:
            text: Input text
            top_k: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        try:
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return []
            
            # Fit vectorizer on single text
            tfidf_matrix = self.vectorizer.fit_transform([processed_text])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            top_indices = np.argsort(tfidf_scores)[::-1][:top_k]
            keywords = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            return []
    
    def detect_narrative_evolution(self, posts: List[Dict]) -> Dict[str, Any]:
        """
        Analyze how a narrative evolves over time
        
        Args:
            posts: List of posts sorted by time
            
        Returns:
            Evolution analysis
        """
        if len(posts) < 2:
            return {'evolution_detected': False, 'stages': []}
        
        # Sort posts by creation time
        sorted_posts = sorted(posts, key=lambda x: x.get('created_at', datetime.now()))
        
        # Analyze content changes over time
        stages = []
        window_size = max(5, len(sorted_posts) // 10)  # Adaptive window size
        
        for i in range(0, len(sorted_posts) - window_size + 1, window_size):
            window_posts = sorted_posts[i:i + window_size]
            
            # Extract common keywords for this time window
            combined_text = ' '.join([post.get('content', '') for post in window_posts])
            keywords = self.extract_keywords(combined_text, 5)
            
            stage = {
                'time_period': {
                    'start': window_posts[0].get('created_at'),
                    'end': window_posts[-1].get('created_at')
                },
                'post_count': len(window_posts),
                'dominant_keywords': keywords,
                'sample_posts': window_posts[:3]  # First 3 posts as samples
            }
            stages.append(stage)
        
        return {
            'evolution_detected': len(stages) > 1,
            'stages': stages,
            'total_timeline_days': (sorted_posts[-1].get('created_at') - sorted_posts[0].get('created_at')).days if len(sorted_posts) > 1 else 0
        }
