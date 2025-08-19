"""Comprehensive competitor analytics system for YouTube content optimization"""

import asyncio
import json
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import os
from collections import Counter, defaultdict

# Web scraping tools
from bs4 import BeautifulSoup
import numpy as np

# LangChain for AI analysis
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


@dataclass
class CompetitorChannel:
    name: str
    url: str
    platform: str
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    total_views: Optional[int] = None
    avg_views_per_video: Optional[float] = None
    engagement_rate: Optional[float] = None
    posting_frequency: Optional[str] = None
    top_performing_content: List[Dict] = None


class YouTubeCompetitorAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        
    async def get_channel_analytics(self, channel_url: str) -> Dict:
        """Extract comprehensive YouTube channel analytics"""
        try:
            # Extract channel ID from URL
            channel_id = self._extract_channel_id(channel_url)
            if not channel_id:
                return await self._fallback_scraping_method(channel_url)
            
            if self.api_key:
                # Use YouTube API if available
                try:
                    import googleapiclient.discovery
                    import googleapiclient.errors
                    
                    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=self.api_key)
                    
                    # Get channel statistics
                    channel_stats = await self._get_channel_stats(youtube, channel_id)
                    
                    # If API fails, fall back to scraping
                    if "error" in channel_stats:
                        print(f"API failed for {channel_url}, using fallback method")
                        return await self._fallback_scraping_method(channel_url)
                    
                    # Get recent videos analytics
                    recent_videos = await self._get_recent_videos(youtube, channel_id, max_results=20)
                    
                    # Analyze video performance patterns
                    performance_analysis = await self._analyze_video_performance(recent_videos)
                    
                    # Get posting patterns
                    posting_patterns = await self._analyze_posting_patterns(recent_videos)
                    
                    # Analyze content themes
                    content_analysis = await self._analyze_content_themes(recent_videos)
                    
                    return {
                        "channel_stats": channel_stats,
                        "recent_videos": recent_videos[:5],  # Further limit for response size
                        "performance_analysis": performance_analysis,
                        "posting_patterns": posting_patterns,
                        "content_analysis": content_analysis,
                        "analysis_date": datetime.now().isoformat(),
                        "data_source": "YouTube API"
                    }
                    
                except ImportError as e:
                    print(f"Google API client not available: {e}")
                    return await self._fallback_scraping_method(channel_url)
                except Exception as e:
                    print(f"YouTube API error: {e}")
                    return await self._fallback_scraping_method(channel_url)
            else:
                return await self._fallback_scraping_method(channel_url)
                
        except Exception as e:
            print(f"YouTube analysis error: {e}")
            return await self._fallback_scraping_method(channel_url)
    
    def _extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel ID from various YouTube URL formats"""
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def _get_channel_stats(self, youtube, channel_id: str) -> Dict:
        """Get basic channel statistics"""
        try:
            response = youtube.channels().list(
                part='statistics,snippet,brandingSettings',
                id=channel_id
            ).execute()
            
            if not response['items']:
                return {"error": "Channel not found"}
            
            channel = response['items'][0]
            stats = channel['statistics']
            snippet = channel['snippet']
            
            return {
                "subscriber_count": int(stats.get('subscriberCount', 0)),
                "video_count": int(stats.get('videoCount', 0)),
                "view_count": int(stats.get('viewCount', 0)),
                "channel_name": snippet.get('title', ''),
                "description": snippet.get('description', '')[:500],
                "published_at": snippet.get('publishedAt', ''),
                "country": snippet.get('country', 'Unknown')
            }
            
        except Exception as e:
            print(f"Channel stats error: {e}")
            return {"error": f"Failed to get channel stats: {str(e)}"}
    
    async def _get_recent_videos(self, youtube, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Get recent videos with detailed analytics"""
        try:
            # Get video IDs
            search_response = youtube.search().list(
                channelId=channel_id,
                type='video',
                order='date',
                part='id',
                maxResults=max_results
            ).execute()
            
            if not search_response['items']:
                return []
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get detailed video statistics
            videos_response = youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for video in videos_response['items']:
                stats = video['statistics']
                snippet = video['snippet']
                content = video['contentDetails']
                
                # Calculate engagement rate
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                engagement_rate = ((likes + comments) / max(views, 1)) * 100 if views > 0 else 0
                
                videos.append({
                    "video_id": video['id'],
                    "title": snippet['title'],
                    "description": snippet['description'][:300],
                    "published_at": snippet['publishedAt'],
                    "duration": content['duration'],
                    "view_count": views,
                    "like_count": likes,
                    "comment_count": comments,
                    "engagement_rate": engagement_rate,
                    "tags": snippet.get('tags', [])[:10],  # Limit tags
                    "category_id": snippet.get('categoryId', ''),
                    "thumbnail_url": snippet['thumbnails']['high']['url']
                })
            
            return videos
            
        except Exception as e:
            print(f"Recent videos error: {e}")
            return []
    
    async def _analyze_video_performance(self, videos: List[Dict]) -> Dict:
        """Analyze video performance patterns"""
        if not videos:
            return {}
        
        views = [v['view_count'] for v in videos]
        engagement_rates = [v['engagement_rate'] for v in videos]
        
        # Performance metrics
        avg_views = sum(views) / len(views) if views else 0
        median_views = sorted(views)[len(views)//2] if views else 0
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        # Top performing videos (top 20%)
        sorted_videos = sorted(videos, key=lambda x: x['view_count'], reverse=True)
        top_20_percent = sorted_videos[:max(1, len(sorted_videos) // 5)]
        
        # High performers analysis
        high_performers = [v for v in videos if v['view_count'] > avg_views * 1.5]
        
        high_performer_tags = []
        for video in high_performers:
            high_performer_tags.extend(video.get('tags', []))
        
        return {
            "total_videos_analyzed": len(videos),
            "average_views": avg_views,
            "median_views": median_views,
            "average_engagement_rate": avg_engagement,
            "top_performing_videos": [
                {
                    "title": v['title'],
                    "view_count": v['view_count'],
                    "engagement_rate": v['engagement_rate']
                } for v in top_20_percent[:5]
            ],
            "high_performer_characteristics": {
                "count": len(high_performers),
                "avg_title_length": sum(len(v['title']) for v in high_performers) / max(len(high_performers), 1),
                "common_tags": [tag for tag, count in Counter(high_performer_tags).most_common(10)],
                "performance_threshold": avg_views * 1.5
            },
            "performance_trends": {
                "consistency_score": 1 - (np.std(views) / max(np.mean(views), 1)) if len(views) > 1 else 1
            }
        }
    
    async def _analyze_posting_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze when and how often the channel posts"""
        if not videos:
            return {}
        
        # Parse publishing dates
        publish_dates = []
        for video in videos:
            try:
                date_str = video['published_at']
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                publish_dates.append(date)
            except:
                continue
        
        if not publish_dates:
            return {}
        
        # Calculate patterns
        days_of_week = [date.strftime('%A') for date in publish_dates]
        hours = [date.hour for date in publish_dates]
        
        # Posting frequency
        date_range = (max(publish_dates) - min(publish_dates)).days
        avg_posts_per_day = len(videos) / max(date_range, 1)
        
        # Recent activity
        recent_videos = [d for d in publish_dates if d > (datetime.now() - timedelta(days=30))]
        
        return {
            "posting_frequency": {
                "average_posts_per_day": avg_posts_per_day,
                "posts_last_30_days": len(recent_videos),
                "most_active_day": max(set(days_of_week), key=days_of_week.count) if days_of_week else None,
                "most_active_hour": max(set(hours), key=hours.count) if hours else None
            },
            "consistency_analysis": {
                "posts_by_day": {day: days_of_week.count(day) for day in set(days_of_week)},
                "posts_by_hour": {str(hour): hours.count(hour) for hour in set(hours)},
                "posting_consistency": "Regular" if avg_posts_per_day > 0.1 else "Irregular"
            }
        }
    
    async def _analyze_content_themes(self, videos: List[Dict]) -> Dict:
        """Analyze content themes and topics"""
        if not videos:
            return {}
        
        # Combine titles and descriptions for analysis
        all_text = " ".join([f"{v['title']} {v.get('description', '')}" for v in videos])
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_freq = Counter([w for w in words if len(w) > 3])
        
        # Extract common tags
        all_tags = []
        for video in videos:
            all_tags.extend(video.get('tags', []))
        
        tag_freq = Counter(all_tags)
        
        # Title analysis
        titles = [v['title'] for v in videos]
        avg_title_length = sum(len(title) for title in titles) / len(titles) if titles else 0
        
        return {
            "top_keywords": [{"term": word, "count": count} for word, count in word_freq.most_common(15)],
            "top_tags": [{"tag": tag, "count": count} for tag, count in tag_freq.most_common(10)],
            "title_analysis": {
                "avg_title_length": avg_title_length,
                "common_title_words": [word for word, count in Counter(' '.join(titles).lower().split()).most_common(10)]
            },
            "content_patterns": {
                "video_count": len(videos),
                "avg_description_length": sum(len(v.get('description', '')) for v in videos) / len(videos) if videos else 0
            }
        }
    
    async def _fallback_scraping_method(self, channel_url: str) -> Dict:
        """Fallback method using web scraping when API fails"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(channel_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info from meta tags
            channel_name = self._extract_meta_content(soup, 'og:title') or "Unknown Channel"
            description = self._extract_meta_content(soup, 'og:description') or ""
            
            # Try to extract subscriber count
            subscriber_info = self._extract_subscriber_count(soup)
            
            # Create a structured response similar to API response
            return {
                "channel_stats": {
                    "channel_name": channel_name,
                    "description": description[:300],
                    "subscriber_count": 0,  # Can't get exact count via scraping
                    "estimated_subscribers": subscriber_info,
                    "note": "Limited data from web scraping - YouTube API recommended for detailed analytics"
                },
                "recent_videos": [],
                "performance_analysis": {
                    "total_videos_analyzed": 0,
                    "note": "Video analysis requires API access"
                },
                "posting_patterns": {
                    "note": "Posting pattern analysis requires API access"
                },
                "content_analysis": {
                    "note": "Content analysis requires API access"
                },
                "data_source": "Web Scraping",
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Fallback scraping error: {e}")
            return {
                "channel_stats": {
                    "channel_name": "Unknown Channel",
                    "description": "Unable to extract channel information",
                    "subscriber_count": 0,
                    "estimated_subscribers": "Unknown",
                    "note": f"Analysis failed: {str(e)}"
                },
                "recent_videos": [],
                "performance_analysis": {"error": "Analysis failed"},
                "posting_patterns": {"error": "Analysis failed"}, 
                "content_analysis": {"error": "Analysis failed"},
                "data_source": "Failed",
                "analysis_date": datetime.now().isoformat(),
                "error": f"Unable to analyze channel: {str(e)}"
            }
    
    def _extract_meta_content(self, soup: BeautifulSoup, property_name: str) -> Optional[str]:
        """Extract content from meta tags"""
        meta_tag = soup.find('meta', property=property_name)
        return meta_tag.get('content') if meta_tag else None
    
    def _extract_subscriber_count(self, soup: BeautifulSoup) -> str:
        """Extract subscriber count from page HTML"""
        # Look for subscriber count patterns
        text = soup.get_text()
        
        # Common patterns for subscriber counts
        patterns = [
            r'(\d+(?:\.\d+)?[KMB]?)\s*subscriber',
            r'(\d+(?:\.\d+)?[KMB]?)\s*subs',
            r'"subscriberCountText"[^}]*"simpleText"\s*:\s*"([^"]*)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Unknown"


class CompetitorAnalyticsInput(BaseModel):
    """Input for competitor analytics tool"""
    competitor_urls: List[str] = Field(description="List of competitor YouTube channel URLs to analyze")
    niche: str = Field(description="Content niche for contextual analysis")


class CompetitorAnalyticsTool(BaseTool):
    """Tool for comprehensive competitor analysis"""
    
    name: str = "competitor_analytics"
    description: str = "Analyze multiple competitor YouTube channels to extract insights, performance metrics, and content strategies"
    args_schema: type = CompetitorAnalyticsInput
    
    def _run(self, **kwargs) -> str:
        """Run competitor analysis with flexible argument handling"""
        try:
            # Extract and validate required parameters, filtering out problematic ones
            competitor_urls = kwargs.get('competitor_urls', [])
            niche = kwargs.get('niche', 'general')
            
            # Convert single URL to list if needed
            if isinstance(competitor_urls, str):
                competitor_urls = [competitor_urls]
            
            # Validate inputs
            if not competitor_urls:
                return "No competitor URLs provided. Please provide at least one YouTube channel URL to analyze."
            
            if not niche:
                niche = "general"
            
            print(f"[DEBUG] competitor_analytics._run called with:")
            print(f"[DEBUG] competitor_urls: {competitor_urls}")
            print(f"[DEBUG] niche: {niche}")
            print(f"[DEBUG] All kwargs: {list(kwargs.keys())}")
            
            analyzer = YouTubeCompetitorAnalyzer()
            results = asyncio.run(self._analyze_competitors(analyzer, competitor_urls, niche))
            return self._format_analysis_results(results, niche)
            
        except Exception as e:
            print(f"[DEBUG] Error in competitor_analytics._run: {str(e)}")
            return f"Error analyzing competitors: {str(e)}"
    
    async def _analyze_competitors(self, analyzer: YouTubeCompetitorAnalyzer, urls: List[str], niche: str) -> Dict:
        """Analyze all competitor channels"""
        results = {}
        
        for i, url in enumerate(urls[:5]):  # Limit to 5 competitors
            try:
                competitor_name = f"Competitor_{i+1}"
                print(f"Analyzing {competitor_name}...")
                
                analysis = await analyzer.get_channel_analytics(url)
                results[competitor_name] = {
                    "url": url,
                    "analysis": analysis
                }
                
            except Exception as e:
                results[f"Competitor_{i+1}"] = {
                    "url": url,
                    "error": str(e)
                }
        
        return {
            "niche": niche,
            "competitor_analyses": results,
            "competitive_insights": self._generate_competitive_insights(results, niche),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _generate_competitive_insights(self, results: Dict, niche: str) -> Dict:
        """Generate competitive insights from analysis results"""
        insights = {
            "performance_benchmarks": {},
            "content_opportunities": [],
            "optimization_recommendations": [],
            "competitive_advantages": []
        }
        
        successful_analyses = []
        for name, data in results.items():
            if 'error' not in data and 'analysis' in data:
                successful_analyses.append(data['analysis'])
        
        if not successful_analyses:
            return {"error": "No successful competitor analyses to generate insights from"}
        
        # Performance benchmarks
        subscriber_counts = []
        avg_views = []
        engagement_rates = []
        
        for analysis in successful_analyses:
            if 'channel_stats' in analysis:
                stats = analysis['channel_stats']
                subscriber_counts.append(stats.get('subscriber_count', 0))
            
            if 'performance_analysis' in analysis:
                perf = analysis['performance_analysis']
                avg_views.append(perf.get('average_views', 0))
                engagement_rates.append(perf.get('average_engagement_rate', 0))
        
        if subscriber_counts:
            insights["performance_benchmarks"]["subscriber_range"] = {
                "min": min(subscriber_counts),
                "max": max(subscriber_counts),
                "average": sum(subscriber_counts) / len(subscriber_counts)
            }
        
        if avg_views:
            insights["performance_benchmarks"]["avg_views_range"] = {
                "min": min(avg_views),
                "max": max(avg_views),
                "average": sum(avg_views) / len(avg_views)
            }
        
        if engagement_rates:
            insights["performance_benchmarks"]["engagement_rate_range"] = {
                "min": min(engagement_rates),
                "max": max(engagement_rates),
                "average": sum(engagement_rates) / len(engagement_rates)
            }
        
        # Content opportunities
        all_tags = []
        all_keywords = []
        top_performing_titles = []
        
        for analysis in successful_analyses:
            if 'content_analysis' in analysis:
                content = analysis['content_analysis']
                all_tags.extend([tag['tag'] for tag in content.get('top_tags', [])])
                all_keywords.extend([kw['term'] for kw in content.get('top_keywords', [])])
            
            if 'performance_analysis' in analysis:
                perf = analysis['performance_analysis']
                for video in perf.get('top_performing_videos', []):
                    top_performing_titles.append(video.get('title', ''))
        
        # Find common successful elements
        common_tags = [tag for tag, count in Counter(all_tags).most_common(10)]
        common_keywords = [kw for kw, count in Counter(all_keywords).most_common(10)]
        
        insights["content_opportunities"] = [
            f"Use trending tags: {', '.join(common_tags[:5])}",
            f"Target keywords: {', '.join(common_keywords[:5])}",
            f"Consider content themes popular in {niche}"
        ]
        
        # Optimization recommendations
        posting_patterns = []
        for analysis in successful_analyses:
            if 'posting_patterns' in analysis:
                patterns = analysis['posting_patterns']
                freq = patterns.get('posting_frequency', {})
                if freq.get('most_active_day'):
                    posting_patterns.append(freq['most_active_day'])
        
        if posting_patterns:
            most_common_day = max(set(posting_patterns), key=posting_patterns.count)
            insights["optimization_recommendations"].append(
                f"Consider posting on {most_common_day} (popular among competitors)"
            )
        
        insights["optimization_recommendations"].extend([
            "Monitor competitor posting schedules for timing opportunities",
            "Analyze competitor thumbnail styles for design inspiration",
            "Study high-performing competitor video formats"
        ])
        
        return insights
    
    def _format_analysis_results(self, results: Dict, niche: str) -> str:
        """Format analysis results for display"""
        output = f"""
# Competitor Analysis Report for {niche.title()} Niche

## 📊 Performance Benchmarks
"""
        
        insights = results.get('competitive_insights', {})
        benchmarks = insights.get('performance_benchmarks', {})
        
        if 'subscriber_range' in benchmarks:
            sub_range = benchmarks['subscriber_range']
            output += f"""
**Subscriber Count Analysis:**
- Range: {self._format_number(sub_range['min'])} - {self._format_number(sub_range['max'])}
- Average: {self._format_number(sub_range['average'])}
"""
        
        if 'avg_views_range' in benchmarks:
            views_range = benchmarks['avg_views_range']
            output += f"""
**Average Views Analysis:**
- Range: {self._format_number(views_range['min'])} - {self._format_number(views_range['max'])}
- Average: {self._format_number(views_range['average'])}
"""
        
        if 'engagement_rate_range' in benchmarks:
            eng_range = benchmarks['engagement_rate_range']
            output += f"""
**Engagement Rate Analysis:**
- Range: {eng_range['min']:.2f}% - {eng_range['max']:.2f}%
- Average: {eng_range['average']:.2f}%
"""
        
        # Content opportunities
        opportunities = insights.get('content_opportunities', [])
        if opportunities:
            output += f"""
## 💡 Content Opportunities

{chr(10).join(f"- {opp}" for opp in opportunities)}
"""
        
        # Optimization recommendations  
        recommendations = insights.get('optimization_recommendations', [])
        if recommendations:
            output += f"""
## 🚀 Optimization Recommendations

{chr(10).join(f"- {rec}" for rec in recommendations)}
"""
        
        # Individual competitor summaries
        output += "\n## 🎯 Individual Competitor Analysis\n"
        
        for name, data in results['competitor_analyses'].items():
            if 'error' in data:
                output += f"\n**{name}**: Analysis failed - {data['error']}\n"
                continue
            
            analysis = data['analysis']
            
            if 'channel_stats' in analysis:
                stats = analysis['channel_stats']
                output += f"""
**{name}** ({data['url']}):
- Channel: {stats.get('channel_name', 'Unknown')}
- Subscribers: {self._format_number(stats.get('subscriber_count', 0))}
- Videos: {stats.get('video_count', 0)}
- Total Views: {self._format_number(stats.get('view_count', 0))}
"""
            
            if 'performance_analysis' in analysis:
                perf = analysis['performance_analysis']
                output += f"- Avg Views/Video: {self._format_number(perf.get('average_views', 0))}\n"
                output += f"- Engagement Rate: {perf.get('average_engagement_rate', 0):.2f}%\n"
                
                # Top performing content
                top_videos = perf.get('top_performing_videos', [])
                if top_videos:
                    output += "- Top Videos:\n"
                    for video in top_videos[:3]:
                        output += f"  * {video.get('title', 'Unknown')[:50]}... ({self._format_number(video.get('view_count', 0))} views)\n"
            
            if 'content_analysis' in analysis:
                content = analysis['content_analysis']
                top_tags = content.get('top_tags', [])[:5]
                if top_tags:
                    tag_names = [tag['tag'] for tag in top_tags]
                    output += f"- Popular Tags: {', '.join(tag_names)}\n"
        
        output += f"""
## 📈 Strategic Insights

Based on the analysis of {len(results['competitor_analyses'])} competitors in the {niche} niche:

1. **Market Position**: Use the benchmark data to understand where you stand
2. **Content Gaps**: Look for topics your competitors aren't covering
3. **Optimization**: Apply the posting patterns and tag strategies that work
4. **Differentiation**: Find unique angles that set you apart from competitors

**Next Steps:**
- Implement the optimization recommendations
- Monitor competitor performance monthly
- Test content ideas inspired by successful competitors
- Track your progress against these benchmarks
"""
        
        return output.strip()
    
    def _format_number(self, num: float) -> str:
        """Format number with appropriate suffix"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.0f}"


# Create tool instance
competitor_analytics_tool = CompetitorAnalyticsTool()

# Export tools
COMPETITOR_ANALYTICS_TOOLS = [
    competitor_analytics_tool
]