"""
Timeline visualization using Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class TimelineVisualizer:
    """Create interactive timeline visualizations"""
    
    def __init__(self):
        self.colors = {
            'reddit': '#FF4500',
            'twitter': '#1DA1F2',
            'default': '#636EFA'
        }
    
    def create_timeline(self, timeline_data: List[Dict], output_file: str):
        """
        Create interactive timeline visualization
        
        Args:
            timeline_data: Timeline data from NarrativeTracker
            output_file: Output HTML file path
        """
        if not timeline_data:
            print("No timeline data to visualize")
            return
        
        # Convert to DataFrame for easier handling
        df_data = []
        for period_data in timeline_data:
            row = {
                'period': period_data['period'],
                'start_time': period_data['start_time'],
                'total_volume': period_data['total_volume'],
                'cross_platform_similarity': period_data['cross_platform_similarity'],
                'dominant_keywords': ', '.join(period_data['dominant_keywords'][:3])
            }
            
            # Add platform-specific data
            for platform, stats in period_data['platforms'].items():
                row[f'{platform}_posts'] = stats['post_count']
                row[f'{platform}_engagement'] = stats['avg_engagement']
                row[f'{platform}_authors'] = stats['unique_authors']
            
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                'Post Volume Over Time',
                'Platform Activity Distribution',
                'Cross-Platform Similarity'
            ),
            vertical_spacing=0.1,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Plot 1: Total volume over time
        fig.add_trace(
            go.Scatter(
                x=df['start_time'],
                y=df['total_volume'],
                mode='lines+markers',
                name='Total Posts',
                line=dict(color='#636EFA', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Posts: %{y}<br>Keywords: %{customdata}<extra></extra>',
                customdata=df['dominant_keywords']
            ),
            row=1, col=1
        )
        
        # Plot 2: Platform-specific activity
        platforms = [col.replace('_posts', '') for col in df.columns if col.endswith('_posts')]
        
        for platform in platforms:
            if f'{platform}_posts' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['start_time'],
                        y=df[f'{platform}_posts'],
                        mode='lines+markers',
                        name=f'{platform.title()} Posts',
                        line=dict(color=self.colors.get(platform, self.colors['default'])),
                        marker=dict(size=6)
                    ),
                    row=2, col=1
                )
        
        # Plot 3: Cross-platform similarity
        fig.add_trace(
            go.Scatter(
                x=df['start_time'],
                y=df['cross_platform_similarity'],
                mode='lines+markers',
                name='Cross-Platform Similarity',
                line=dict(color='#FF6692', width=2),
                marker=dict(size=6),
                yaxis='y3'
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="Narrative Evolution Timeline",
                x=0.5,
                font=dict(size=20)
            ),
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_yaxes(title_text="Post Count", row=1, col=1)
        fig.update_yaxes(title_text="Platform Posts", row=2, col=1)
        fig.update_yaxes(title_text="Similarity Score", row=3, col=1, range=[0, 1])
        
        # Save to HTML
        fig.write_html(output_file)
        print(f"Timeline visualization saved to: {output_file}")
    
    def create_platform_comparison(self, timeline_data: List[Dict], output_file: str):
        """Create platform comparison visualization"""
        
        # Prepare data for platform comparison
        platform_data = []
        
        for period_data in timeline_data:
            for platform, stats in period_data['platforms'].items():
                if stats['post_count'] > 0:
                    platform_data.append({
                        'period': period_data['period'],
                        'start_time': period_data['start_time'],
                        'platform': platform,
                        'post_count': stats['post_count'],
                        'avg_engagement': stats['avg_engagement'],
                        'unique_authors': stats['unique_authors'],
                        'keywords': ', '.join(stats['keywords'][:3])
                    })
        
        if not platform_data:
            print("No platform data to visualize")
            return
        
        df = pd.DataFrame(platform_data)
        
        # Create stacked area chart
        fig = px.area(
            df, 
            x='start_time', 
            y='post_count',
            color='platform',
            title='Platform Activity Over Time',
            labels={'post_count': 'Number of Posts', 'start_time': 'Time'},
            color_discrete_map=self.colors
        )
        
        fig.update_layout(
            height=500,
            hovermode='x unified'
        )
        
        fig.write_html(output_file)
        print(f"Platform comparison saved to: {output_file}")
    
    def create_keyword_evolution(self, timeline_data: List[Dict], output_file: str):
        """Create keyword evolution heatmap"""
        
        # Extract all keywords and their frequencies over time
        all_keywords = set()
        for period_data in timeline_data:
            all_keywords.update(period_data['dominant_keywords'])
        
        # Create matrix of keyword frequencies
        keyword_matrix = []
        periods = []
        
        for period_data in timeline_data:
            periods.append(period_data['period'])
            keyword_counts = {kw: 0 for kw in all_keywords}
            
            for keyword in period_data['dominant_keywords']:
                keyword_counts[keyword] += 1
            
            keyword_matrix.append(list(keyword_counts.values()))
        
        if not keyword_matrix:
            print("No keyword data to visualize")
            return
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=list(zip(*keyword_matrix)),  # Transpose for correct orientation
            x=periods,
            y=list(all_keywords),
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Keyword Evolution Heatmap',
            xaxis_title='Time Period',
            yaxis_title='Keywords',
            height=600
        )
        
        fig.write_html(output_file)
        print(f"Keyword evolution heatmap saved to: {output_file}")
    
    def create_network_graph(self, network_data: Dict, output_file: str):
        """Create network visualization (placeholder for future implementation)"""
        print("Network visualization coming soon...")
        # This would use plotly or networkx to create influence network graphs
