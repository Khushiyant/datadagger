"""
Data storage and management utilities
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

class DataStore:
    """Handle data persistence and retrieval"""
    
    def __init__(self, db_path: str = None):
        """Initialize data store with SQLite database"""
        if db_path is None:
            db_path = os.getenv('DATABASE_URL', 'sqlite:///datadagger.db')
            if db_path.startswith('sqlite:///'):
                db_path = db_path[10:]  # Remove sqlite:/// prefix
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Posts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    created_at TIMESTAMP,
                    engagement_score INTEGER DEFAULT 0,
                    metadata TEXT,
                    query TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Narratives table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS narratives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    platforms TEXT,
                    total_posts INTEGER DEFAULT 0,
                    analysis_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT NOT NULL,
                    query TEXT,
                    results TEXT,
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def store_posts(self, posts: List[Dict], query: str = None) -> int:
        """
        Store posts in database
        
        Args:
            posts: List of post dictionaries
            query: Associated search query
            
        Returns:
            Number of posts stored
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            stored_count = 0
            
            for post in posts:
                try:
                    # Calculate engagement score
                    engagement = 0
                    if post.get('platform') == 'reddit':
                        engagement = post.get('score', 0) + post.get('num_comments', 0)
                    elif post.get('platform') == 'twitter':
                        engagement = (post.get('like_count', 0) + 
                                    post.get('retweet_count', 0) + 
                                    post.get('reply_count', 0))
                    
                    # Store metadata as JSON
                    metadata = {k: v for k, v in post.items() 
                              if k not in ['id', 'platform', 'content', 'author', 'created_at']}
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO posts 
                        (id, platform, content, author, created_at, engagement_score, metadata, query)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post.get('id'),
                        post.get('platform'),
                        post.get('content'),
                        post.get('author'),
                        post.get('created_at'),
                        engagement,
                        json.dumps(metadata),
                        query
                    ))
                    stored_count += 1
                    
                except Exception as e:
                    print(f"Error storing post {post.get('id', 'unknown')}: {str(e)}")
            
            conn.commit()
            return stored_count
    
    def get_posts(self, query: str = None, platform: str = None, 
                  start_date: datetime = None, end_date: datetime = None,
                  limit: int = 1000) -> List[Dict]:
        """
        Retrieve posts from database
        
        Args:
            query: Filter by search query
            platform: Filter by platform
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            
        Returns:
            List of post dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build WHERE clause
            conditions = []
            params = []
            
            if query:
                conditions.append("query = ?")
                params.append(query)
            
            if platform:
                conditions.append("platform = ?")
                params.append(platform)
            
            if start_date:
                conditions.append("created_at >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("created_at <= ?")
                params.append(end_date)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            
            sql = f'''
                SELECT id, platform, content, author, created_at, 
                       engagement_score, metadata, query
                FROM posts
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            '''
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            posts = []
            for row in rows:
                post = {
                    'id': row[0],
                    'platform': row[1],
                    'content': row[2],
                    'author': row[3],
                    'created_at': row[4],
                    'engagement_score': row[5],
                    'query': row[7]
                }
                
                # Add metadata
                if row[6]:
                    try:
                        metadata = json.loads(row[6])
                        post.update(metadata)
                    except json.JSONDecodeError:
                        pass
                
                posts.append(post)
            
            return posts
    
    def store_analysis(self, analysis_type: str, query: str, results: Dict, 
                      parameters: Dict = None) -> int:
        """
        Store analysis results
        
        Args:
            analysis_type: Type of analysis performed
            query: Search query analyzed
            results: Analysis results
            parameters: Analysis parameters
            
        Returns:
            Analysis ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results 
                (analysis_type, query, results, parameters)
                VALUES (?, ?, ?, ?)
            ''', (
                analysis_type,
                query,
                json.dumps(results, default=str),
                json.dumps(parameters or {})
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_analysis_history(self, analysis_type: str = None, 
                           query: str = None, limit: int = 100) -> List[Dict]:
        """
        Get analysis history
        
        Args:
            analysis_type: Filter by analysis type
            query: Filter by query
            limit: Maximum results
            
        Returns:
            List of analysis records
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if analysis_type:
                conditions.append("analysis_type = ?")
                params.append(analysis_type)
            
            if query:
                conditions.append("query = ?")
                params.append(query)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            
            sql = f'''
                SELECT id, analysis_type, query, results, parameters, created_at
                FROM analysis_results
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            '''
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            analyses = []
            for row in rows:
                analysis = {
                    'id': row[0],
                    'analysis_type': row[1],
                    'query': row[2],
                    'created_at': row[5]
                }
                
                # Parse JSON fields
                try:
                    analysis['results'] = json.loads(row[3])
                    analysis['parameters'] = json.loads(row[4]) if row[4] else {}
                except json.JSONDecodeError:
                    analysis['results'] = {}
                    analysis['parameters'] = {}
                
                analyses.append(analysis)
            
            return analyses
    
    def export_to_csv(self, query: str, output_path: str) -> bool:
        """
        Export posts to CSV file
        
        Args:
            query: Query to export
            output_path: Output file path
            
        Returns:
            Success status
        """
        try:
            posts = self.get_posts(query=query)
            
            if not posts:
                print(f"No posts found for query: {query}")
                return False
            
            df = pd.DataFrame(posts)
            df.to_csv(output_path, index=False)
            print(f"Exported {len(posts)} posts to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get post counts by platform
            cursor.execute('''
                SELECT platform, COUNT(*) as count
                FROM posts
                GROUP BY platform
            ''')
            platform_counts = dict(cursor.fetchall())
            
            # Get total posts
            cursor.execute('SELECT COUNT(*) FROM posts')
            total_posts = cursor.fetchone()[0]
            
            # Get unique queries
            cursor.execute('SELECT COUNT(DISTINCT query) FROM posts WHERE query IS NOT NULL')
            unique_queries = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM posts')
            date_range = cursor.fetchone()
            
            return {
                'total_posts': total_posts,
                'unique_queries': unique_queries,
                'platform_distribution': platform_counts,
                'date_range': {
                    'earliest': date_range[0],
                    'latest': date_range[1]
                }
            }
