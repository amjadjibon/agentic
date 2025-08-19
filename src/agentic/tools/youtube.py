"""YouTube-specific tools for content automation"""

import os
import re
import requests
from typing import Dict, List, Optional, Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class YouTubeChannelAnalyzerInput(BaseModel):
    """Input for YouTube channel analyzer tool"""
    channel_url: str = Field(description="YouTube channel URL to analyze")


class YouTubeChannelAnalyzer(BaseTool):
    """Tool to analyze YouTube channel data and extract insights"""
    
    name: str = "youtube_channel_analyzer"
    description: str = "Analyze YouTube channel data including subscriber count, video performance, and content patterns"
    args_schema = YouTubeChannelAnalyzerInput
    
    def _run(self, channel_url: str) -> str:
        """Analyze YouTube channel and return insights"""
        try:
            # Extract channel ID from URL
            channel_id = self._extract_channel_id(channel_url)
            if not channel_id:
                return f"Error: Could not extract channel ID from {channel_url}"
            
            # Get YouTube API key
            api_key = os.getenv("YOUTUBE_API_KEY")
            if not api_key:
                return "Note: YouTube API key not found. Providing general analysis structure instead of real data.\n\nChannel analysis would include:\n- Subscriber count and growth rate\n- Recent video performance metrics\n- Upload frequency and consistency\n- Content themes and popular video types\n- Audience engagement patterns\n- SEO optimization opportunities\n\nTo get real data, set YOUTUBE_API_KEY environment variable."
            
            # Fetch channel data
            channel_data = self._fetch_channel_data(channel_id, api_key)
            recent_videos = self._fetch_recent_videos(channel_id, api_key)
            
            # Analyze and format results
            analysis = self._analyze_channel_data(channel_data, recent_videos)
            return analysis
            
        except Exception as e:
            return f"Error analyzing channel: {str(e)}"
    
    def _extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel ID from YouTube URL"""
        patterns = [
            r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
            r"youtube\.com/c/([a-zA-Z0-9_-]+)",
            r"youtube\.com/@([a-zA-Z0-9_-]+)",
            r"youtube\.com/user/([a-zA-Z0-9_-]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _fetch_channel_data(self, channel_id: str, api_key: str) -> Dict[str, Any]:
        """Fetch channel data from YouTube API"""
        url = f"https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "snippet,statistics,brandingSettings",
            "id": channel_id,
            "key": api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("items"):
            raise ValueError(f"Channel not found: {channel_id}")
        
        return data["items"][0]
    
    def _fetch_recent_videos(self, channel_id: str, api_key: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent videos from the channel"""
        # Get recent video IDs
        url = f"https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": max_results,
            "key": api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data.get("items"):
            return []
        
        # Get detailed video statistics
        video_ids = [item["id"]["videoId"] for item in search_data["items"]]
        video_ids_str = ",".join(video_ids)
        
        stats_url = f"https://www.googleapis.com/youtube/v3/videos"
        stats_params = {
            "part": "statistics,snippet,contentDetails",
            "id": video_ids_str,
            "key": api_key
        }
        
        stats_response = requests.get(stats_url, params=stats_params)
        stats_response.raise_for_status()
        stats_data = stats_response.json()
        
        return stats_data.get("items", [])
    
    def _analyze_channel_data(self, channel_data: Dict[str, Any], recent_videos: List[Dict[str, Any]]) -> str:
        """Analyze channel data and create insights"""
        snippet = channel_data.get("snippet", {})
        stats = channel_data.get("statistics", {})
        
        # Basic channel info
        analysis = f"""
YouTube Channel Analysis:

📊 CHANNEL OVERVIEW:
- Channel Name: {snippet.get('title', 'Unknown')}
- Subscribers: {self._format_number(int(stats.get('subscriberCount', 0)))}
- Total Videos: {stats.get('videoCount', 'Unknown')}
- Total Views: {self._format_number(int(stats.get('viewCount', 0)))}
- Created: {snippet.get('publishedAt', 'Unknown')[:10]}

📈 RECENT VIDEO PERFORMANCE:
"""
        
        if recent_videos:
            total_views = 0
            total_likes = 0
            total_comments = 0
            
            for i, video in enumerate(recent_videos[:5], 1):
                video_snippet = video.get("snippet", {})
                video_stats = video.get("statistics", {})
                
                views = int(video_stats.get("viewCount", 0))
                likes = int(video_stats.get("likeCount", 0))
                comments = int(video_stats.get("commentCount", 0))
                
                total_views += views
                total_likes += likes
                total_comments += comments
                
                analysis += f"""
Video {i}: {video_snippet.get('title', 'Unknown')[:50]}...
  - Views: {self._format_number(views)}
  - Likes: {self._format_number(likes)}
  - Comments: {self._format_number(comments)}
  - Published: {video_snippet.get('publishedAt', 'Unknown')[:10]}
"""
            
            # Calculate averages
            avg_views = total_views // len(recent_videos)
            avg_likes = total_likes // len(recent_videos)
            avg_comments = total_comments // len(recent_videos)
            
            analysis += f"""
📊 AVERAGE PERFORMANCE (Last {len(recent_videos)} videos):
- Average Views: {self._format_number(avg_views)}
- Average Likes: {self._format_number(avg_likes)}
- Average Comments: {self._format_number(avg_comments)}
- Engagement Rate: {((avg_likes + avg_comments) / avg_views * 100):.2f}%
"""
        
        # Content analysis
        if recent_videos:
            titles = [v.get("snippet", {}).get("title", "") for v in recent_videos]
            analysis += f"""
🎯 CONTENT PATTERNS:
- Common keywords in titles: {self._extract_keywords(titles)}
- Upload consistency: {self._analyze_upload_pattern(recent_videos)}
"""
        
        analysis += """
💡 OPTIMIZATION OPPORTUNITIES:
- Analyze top-performing video formats and replicate
- Optimize titles for SEO with trending keywords
- Improve thumbnail click-through rates
- Increase community engagement through comments
- Consider trending topics in your niche
- Maintain consistent upload schedule
"""
        
        return analysis.strip()
    
    def _format_number(self, num: int) -> str:
        """Format number with appropriate suffix"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)
    
    def _extract_keywords(self, titles: List[str]) -> str:
        """Extract common keywords from video titles"""
        # Simple keyword extraction
        words = {}
        for title in titles:
            for word in title.lower().split():
                word = re.sub(r'[^\w]', '', word)
                if len(word) > 3:
                    words[word] = words.get(word, 0) + 1
        
        # Get top keywords
        top_words = sorted(words.items(), key=lambda x: x[1], reverse=True)[:5]
        return ", ".join([word for word, count in top_words if count > 1])
    
    def _analyze_upload_pattern(self, videos: List[Dict[str, Any]]) -> str:
        """Analyze upload consistency"""
        if len(videos) < 2:
            return "Insufficient data"
        
        # Get upload dates
        dates = []
        for video in videos:
            published = video.get("snippet", {}).get("publishedAt", "")
            if published:
                dates.append(published[:10])
        
        if len(dates) < 2:
            return "Insufficient data"
        
        # Simple analysis
        return f"Recent uploads span {len(set(dates))} unique dates in last {len(videos)} videos"


class YouTubeTrendAnalyzerInput(BaseModel):
    """Input for YouTube trend analyzer tool"""
    niche: str = Field(description="Content niche or topic to analyze trends for")
    region: str = Field(default="US", description="Region code for trend analysis")


class YouTubeTrendAnalyzer(BaseTool):
    """Tool to analyze YouTube trending topics and content"""
    
    name: str = "youtube_trend_analyzer"
    description: str = "Analyze trending YouTube topics and content patterns for a specific niche"
    args_schema = YouTubeTrendAnalyzerInput
    
    def _run(self, niche: str, region: str = "US") -> str:
        """Analyze trending topics for the specified niche"""
        try:
            api_key = os.getenv("YOUTUBE_API_KEY")
            if not api_key:
                return f"""Trend analysis for "{niche}" niche:

Note: YouTube API key not found. Providing general trend analysis structure instead of real data.

📈 TRENDING ANALYSIS WOULD INCLUDE:
1. Popular video formats in the {niche} space
2. Trending keywords and topics
3. Viral content patterns and characteristics
4. Seasonal trends and timing opportunities
5. Competitor content analysis
6. Audience engagement patterns

🎯 RECOMMENDED RESEARCH APPROACH:
- Use search tools to find trending {niche} content
- Analyze competitor channels manually
- Monitor social media for trending topics
- Check Google Trends for keyword popularity
- Look for seasonal content opportunities

To get real YouTube trending data, set YOUTUBE_API_KEY environment variable."""
            
            # Fetch trending videos
            trending_videos = self._fetch_trending_videos(api_key, region)
            niche_relevant = self._filter_by_niche(trending_videos, niche)
            
            # Analyze trends
            analysis = self._analyze_trends(niche_relevant, niche)
            return analysis
            
        except Exception as e:
            return f"Error analyzing trends: {str(e)}"
    
    def _fetch_trending_videos(self, api_key: str, region: str) -> List[Dict[str, Any]]:
        """Fetch trending videos from YouTube API"""
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": 50,
            "key": api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get("items", [])
    
    def _filter_by_niche(self, videos: List[Dict[str, Any]], niche: str) -> List[Dict[str, Any]]:
        """Filter videos relevant to the specified niche"""
        niche_keywords = niche.lower().split()
        relevant_videos = []
        
        for video in videos:
            snippet = video.get("snippet", {})
            title = snippet.get("title", "").lower()
            description = snippet.get("description", "").lower()
            tags = snippet.get("tags", [])
            
            # Check if any niche keywords appear in title, description, or tags
            for keyword in niche_keywords:
                if (keyword in title or 
                    keyword in description or 
                    any(keyword in tag.lower() for tag in tags)):
                    relevant_videos.append(video)
                    break
        
        return relevant_videos
    
    def _analyze_trends(self, videos: List[Dict[str, Any]], niche: str) -> str:
        """Analyze trending videos and extract insights"""
        if not videos:
            return f"No trending videos found specifically for '{niche}' niche. Consider broadening search terms or checking general trends."
        
        analysis = f"""
YouTube Trend Analysis for "{niche}" Niche:

📊 TRENDING CONTENT ({len(videos)} relevant videos found):
"""
        
        total_views = 0
        total_likes = 0
        total_comments = 0
        
        for i, video in enumerate(videos[:10], 1):
            snippet = video.get("snippet", {})
            stats = video.get("statistics", {})
            
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            
            total_views += views
            total_likes += likes
            total_comments += comments
            
            analysis += f"""
{i}. {snippet.get('title', 'Unknown')[:60]}...
   Channel: {snippet.get('channelTitle', 'Unknown')}
   Views: {self._format_number(views)} | Likes: {self._format_number(likes)} | Comments: {self._format_number(comments)}
"""
        
        # Calculate performance metrics
        if videos:
            avg_views = total_views // len(videos)
            avg_engagement = (total_likes + total_comments) // len(videos)
            
            analysis += f"""
📈 PERFORMANCE METRICS:
- Average Views: {self._format_number(avg_views)}
- Average Engagement: {self._format_number(avg_engagement)}
- Top Performing Format: {self._identify_top_format(videos)}

🎯 TREND INSIGHTS:
- Popular Keywords: {self._extract_trending_keywords(videos)}
- Common Video Lengths: {self._analyze_video_lengths(videos)}
- Upload Timing Patterns: {self._analyze_upload_times(videos)}

💡 CONTENT OPPORTUNITIES:
- Create content around trending keywords
- Adopt successful video formats from top performers
- Time uploads based on trending patterns
- Engage with current viral topics in your niche
"""
        
        return analysis.strip()
    
    def _format_number(self, num: int) -> str:
        """Format number with appropriate suffix"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)
    
    def _identify_top_format(self, videos: List[Dict[str, Any]]) -> str:
        """Identify the most common video format from titles"""
        formats = {}
        for video in videos:
            title = video.get("snippet", {}).get("title", "").lower()
            
            if "review" in title:
                formats["Review"] = formats.get("Review", 0) + 1
            elif "tutorial" in title or "how to" in title:
                formats["Tutorial"] = formats.get("Tutorial", 0) + 1
            elif "reaction" in title:
                formats["Reaction"] = formats.get("Reaction", 0) + 1
            elif "vs" in title or "versus" in title:
                formats["Comparison"] = formats.get("Comparison", 0) + 1
            else:
                formats["General"] = formats.get("General", 0) + 1
        
        if not formats:
            return "Mixed formats"
        
        top_format = max(formats.items(), key=lambda x: x[1])
        return f"{top_format[0]} ({top_format[1]} videos)"
    
    def _extract_trending_keywords(self, videos: List[Dict[str, Any]]) -> str:
        """Extract trending keywords from video titles"""
        words = {}
        for video in videos:
            title = video.get("snippet", {}).get("title", "").lower()
            for word in title.split():
                word = re.sub(r'[^\w]', '', word)
                if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were', 'said', 'each', 'which', 'their']:
                    words[word] = words.get(word, 0) + 1
        
        top_words = sorted(words.items(), key=lambda x: x[1], reverse=True)[:8]
        return ", ".join([word for word, count in top_words if count > 1])
    
    def _analyze_video_lengths(self, videos: List[Dict[str, Any]]) -> str:
        """Analyze common video lengths (would need contentDetails in real implementation)"""
        return "Mixed lengths (requires content details API call for accurate analysis)"
    
    def _analyze_upload_times(self, videos: List[Dict[str, Any]]) -> str:
        """Analyze upload timing patterns"""
        upload_hours = {}
        for video in videos:
            published = video.get("snippet", {}).get("publishedAt", "")
            if published and "T" in published:
                time_part = published.split("T")[1]
                hour = int(time_part.split(":")[0])
                upload_hours[hour] = upload_hours.get(hour, 0) + 1
        
        if not upload_hours:
            return "Upload timing data not available"
        
        peak_hour = max(upload_hours.items(), key=lambda x: x[1])
        return f"Peak upload time: {peak_hour[0]}:00 UTC ({peak_hour[1]} videos)"


# Create tool instances
youtube_channel_analyzer = YouTubeChannelAnalyzer()
youtube_trend_analyzer = YouTubeTrendAnalyzer()

# Export tools
YOUTUBE_TOOLS = [
    youtube_channel_analyzer,
    youtube_trend_analyzer
]