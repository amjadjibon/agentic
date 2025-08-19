"""yt-dlp based competitor analysis tool for comprehensive YouTube data extraction"""

from typing import Dict, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime
import json
import subprocess
import os
import tempfile
import shutil
from pathlib import Path


class YtDlpCompetitorInput(BaseModel):
    """Input for yt-dlp competitor analysis tool"""
    competitor_urls: List[str] = Field(description="List of competitor YouTube channel URLs to analyze")
    niche: str = Field(description="Content niche for contextual analysis")
    max_videos: int = Field(default=20, description="Maximum number of videos to analyze per channel")


class YtDlpCompetitorTool(BaseTool):
    """Comprehensive competitor analysis using yt-dlp for data extraction"""
    
    name: str = "ytdlp_competitor_analysis"
    description: str = "Extract comprehensive YouTube competitor data using yt-dlp (requires yt-dlp installation)"
    args_schema: type = YtDlpCompetitorInput
    
    def _run(self, **kwargs) -> str:
        """Run yt-dlp based competitor analysis"""
        try:
            # Extract parameters safely
            competitor_urls = kwargs.get('competitor_urls', [])
            niche = kwargs.get('niche', 'general')
            max_videos = kwargs.get('max_videos', 20)
            
            # Convert single URL to list if needed
            if isinstance(competitor_urls, str):
                competitor_urls = [competitor_urls]
            
            # Validate inputs
            if not competitor_urls:
                return self._generate_usage_guide()
            
            # Check if yt-dlp is available
            if not self._check_ytdlp_available():
                return self._generate_installation_guide()
            
            return self._analyze_competitors_with_ytdlp(competitor_urls, niche, max_videos)
            
        except Exception as e:
            return f"❌ Error in yt-dlp competitor analysis: {str(e)}\\n\\nPlease ensure yt-dlp is properly installed."
    
    def _check_ytdlp_available(self) -> bool:
        """Check if yt-dlp is available in the system"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _analyze_competitors_with_ytdlp(self, urls: List[str], niche: str, max_videos: int) -> str:
        """Analyze competitors using yt-dlp data extraction"""
        
        results = []
        successful_analyses = 0
        
        # Create temporary directory for analysis
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, url in enumerate(urls[:5], 1):  # Limit to 5 competitors
                try:
                    competitor_name = f"Competitor_{i}"
                    print(f"Analyzing {competitor_name} with yt-dlp...")
                    
                    analysis = self._extract_channel_data(url, temp_dir, max_videos)
                    if analysis:
                        results.append({
                            "name": competitor_name,
                            "url": url,
                            "analysis": analysis
                        })
                        successful_analyses += 1
                    else:
                        results.append({
                            "name": competitor_name,
                            "url": url,
                            "error": "Failed to extract data"
                        })
                        
                except Exception as e:
                    results.append({
                        "name": f"Competitor_{i}",
                        "url": url,
                        "error": str(e)
                    })
        
        return self._format_ytdlp_results(results, niche, successful_analyses)
    
    def _extract_channel_data(self, channel_url: str, temp_dir: str, max_videos: int) -> Dict:
        """Extract comprehensive channel data using yt-dlp"""
        try:
            # Step 1: Get channel metadata and video list
            videos_file = os.path.join(temp_dir, "videos.json")
            
            # Extract video metadata with flat playlist
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--flat-playlist',
                '--playlist-end', str(max_videos),
                f'{channel_url}/videos'
            ]
            
            with open(videos_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, 
                                      text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"yt-dlp error: {result.stderr}")
                return None
            
            # Parse video data
            videos_data = []
            try:
                with open(videos_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            video_data = json.loads(line)
                            videos_data.append(video_data)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return None
            
            if not videos_data:
                return None
            
            # Step 2: Get detailed metadata for top videos
            detailed_videos = self._get_detailed_video_data(videos_data[:10], temp_dir)
            
            # Step 3: Analyze the data
            analysis = self._analyze_channel_performance(videos_data, detailed_videos)
            
            return analysis
            
        except subprocess.TimeoutExpired:
            print("yt-dlp command timed out")
            return None
        except Exception as e:
            print(f"Data extraction error: {e}")
            return None
    
    def _get_detailed_video_data(self, videos: List[Dict], temp_dir: str) -> List[Dict]:
        """Get detailed metadata for specific videos"""
        detailed_videos = []
        
        for i, video in enumerate(videos[:5]):  # Limit detailed analysis
            try:
                video_id = video.get('id', '')
                if not video_id:
                    continue
                
                # Get detailed video info
                cmd = [
                    'yt-dlp',
                    '--dump-json',
                    '--no-download',
                    f'https://youtube.com/watch?v={video_id}'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        detailed_data = json.loads(result.stdout.strip())
                        detailed_videos.append(detailed_data)
                    except json.JSONDecodeError:
                        continue
                        
            except subprocess.TimeoutExpired:
                continue
            except Exception as e:
                print(f"Detailed video error: {e}")
                continue
        
        return detailed_videos
    
    def _analyze_channel_performance(self, videos: List[Dict], detailed_videos: List[Dict]) -> Dict:
        """Analyze channel performance from extracted data"""
        
        # Basic channel info from first video
        channel_info = {}
        if videos:
            first_video = videos[0]
            channel_info = {
                "channel_name": first_video.get('uploader', 'Unknown Channel'),
                "channel_id": first_video.get('uploader_id', ''),
                "total_videos_found": len(videos)
            }
        
        # Video performance analysis
        video_views = []
        video_titles = []
        upload_dates = []
        
        for video in videos:
            view_count = video.get('view_count', 0)
            if view_count and view_count > 0:
                video_views.append(view_count)
            
            title = video.get('title', '')
            if title:
                video_titles.append(title)
            
            upload_date = video.get('upload_date', '')
            if upload_date:
                upload_dates.append(upload_date)
        
        # Performance metrics
        performance_metrics = {}
        if video_views:
            performance_metrics = {
                "total_videos_with_views": len(video_views),
                "average_views": sum(video_views) / len(video_views),
                "median_views": sorted(video_views)[len(video_views)//2],
                "highest_views": max(video_views),
                "lowest_views": min(video_views),
                "total_channel_views": sum(video_views)
            }
        
        # Detailed video analysis
        detailed_analysis = {}
        if detailed_videos:
            tags_list = []
            like_counts = []
            comment_counts = []
            durations = []
            
            for video in detailed_videos:
                # Extract tags
                tags = video.get('tags', [])
                if tags:
                    tags_list.extend(tags[:10])  # Limit tags per video
                
                # Extract engagement metrics
                like_count = video.get('like_count', 0)
                if like_count:
                    like_counts.append(like_count)
                
                comment_count = video.get('comment_count', 0)
                if comment_count:
                    comment_counts.append(comment_count)
                
                # Extract duration
                duration = video.get('duration', 0)
                if duration:
                    durations.append(duration)
            
            # Tag analysis
            from collections import Counter
            tag_counter = Counter(tags_list)
            top_tags = [{"tag": tag, "count": count} for tag, count in tag_counter.most_common(15)]
            
            detailed_analysis = {
                "detailed_videos_analyzed": len(detailed_videos),
                "top_tags": top_tags,
                "engagement_metrics": {
                    "average_likes": sum(like_counts) / len(like_counts) if like_counts else 0,
                    "average_comments": sum(comment_counts) / len(comment_counts) if comment_counts else 0,
                    "total_likes": sum(like_counts),
                    "total_comments": sum(comment_counts)
                },
                "content_analysis": {
                    "average_duration_seconds": sum(durations) / len(durations) if durations else 0,
                    "average_title_length": sum(len(title) for title in video_titles) / len(video_titles) if video_titles else 0
                }
            }
        
        # Upload frequency analysis
        frequency_analysis = {}
        if upload_dates and len(upload_dates) > 1:
            # Simple frequency calculation
            date_range = len(set(upload_dates))
            frequency_analysis = {
                "unique_upload_dates": date_range,
                "posting_consistency": "Regular" if date_range > len(upload_dates) * 0.7 else "Irregular",
                "analysis_period": f"{len(upload_dates)} videos analyzed"
            }
        
        return {
            "channel_info": channel_info,
            "performance_metrics": performance_metrics,
            "detailed_analysis": detailed_analysis,
            "frequency_analysis": frequency_analysis,
            "data_source": "yt-dlp extraction",
            "analysis_date": datetime.now().isoformat()
        }
    
    def _format_ytdlp_results(self, results: List[Dict], niche: str, successful_count: int) -> str:
        """Format yt-dlp analysis results"""
        
        output = f"""
# 🎯 Comprehensive Competitor Analysis - {niche.title()} Niche

**Analysis Method:** yt-dlp Data Extraction
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Successful Analyses:** {successful_count}/{len(results)}

---

## 📊 Channel Performance Overview

"""
        
        for result in results:
            if "error" in result:
                output += f"""
**{result['name']}** ❌
- URL: {result['url']}
- Status: Failed - {result['error']}

"""
                continue
            
            analysis = result['analysis']
            channel_info = analysis.get('channel_info', {})
            performance = analysis.get('performance_metrics', {})
            detailed = analysis.get('detailed_analysis', {})
            
            output += f"""
**{result['name']}: {channel_info.get('channel_name', 'Unknown')}** ✅
- URL: {result['url']}
- Channel ID: {channel_info.get('channel_id', 'N/A')}
- Videos Analyzed: {channel_info.get('total_videos_found', 0)}

**Performance Metrics:**
- Total Views (analyzed videos): {self._format_number(performance.get('total_channel_views', 0))}
- Average Views per Video: {self._format_number(performance.get('average_views', 0))}
- Highest Performing Video: {self._format_number(performance.get('highest_views', 0))} views
- View Range: {self._format_number(performance.get('lowest_views', 0))} - {self._format_number(performance.get('highest_views', 0))}

"""
            
            if detailed:
                engagement = detailed.get('engagement_metrics', {})
                content = detailed.get('content_analysis', {})
                tags = detailed.get('top_tags', [])
                
                output += f"""**Engagement Analysis:**
- Average Likes: {self._format_number(engagement.get('average_likes', 0))}
- Average Comments: {self._format_number(engagement.get('average_comments', 0))}
- Total Engagement: {self._format_number(engagement.get('total_likes', 0) + engagement.get('total_comments', 0))}

**Content Insights:**
- Average Video Duration: {content.get('average_duration_seconds', 0)//60}:{content.get('average_duration_seconds', 0)%60:02d}
- Average Title Length: {content.get('average_title_length', 0):.0f} characters

"""
                
                if tags[:5]:
                    tag_list = ", ".join([tag['tag'] for tag in tags[:5]])
                    output += f"**Top Tags:** {tag_list}\\n\\n"
        
        # Generate competitive insights
        output += self._generate_competitive_insights_ytdlp(results, niche)
        
        return output.strip()
    
    def _generate_competitive_insights_ytdlp(self, results: List[Dict], niche: str) -> str:
        """Generate strategic insights from yt-dlp analysis"""
        
        successful_results = [r for r in results if 'analysis' in r]
        if not successful_results:
            return "\\n## ❌ No successful analyses to generate insights from\\n"
        
        # Aggregate performance data
        all_views = []
        all_tags = []
        all_engagement_rates = []
        
        for result in successful_results:
            analysis = result['analysis']
            perf = analysis.get('performance_metrics', {})
            detailed = analysis.get('detailed_analysis', {})
            
            avg_views = perf.get('average_views', 0)
            if avg_views > 0:
                all_views.append(avg_views)
            
            tags = detailed.get('top_tags', [])
            all_tags.extend([tag['tag'] for tag in tags])
            
            # Calculate simple engagement rate
            engagement = detailed.get('engagement_metrics', {})
            likes = engagement.get('average_likes', 0)
            comments = engagement.get('average_comments', 0)
            if avg_views > 0 and (likes > 0 or comments > 0):
                eng_rate = ((likes + comments) / avg_views) * 100
                all_engagement_rates.append(eng_rate)
        
        insights = f"""
---

## 💡 Competitive Intelligence Insights

### Performance Benchmarks
"""
        
        if all_views:
            min_views = min(all_views)
            max_views = max(all_views)
            avg_views = sum(all_views) / len(all_views)
            
            insights += f"""
**View Performance in {niche.title()}:**
- Market Range: {self._format_number(min_views)} - {self._format_number(max_views)} avg views
- Market Average: {self._format_number(avg_views)} views per video
- Performance Tier: {'High' if avg_views > 100000 else 'Medium' if avg_views > 10000 else 'Growing'}

"""
        
        if all_engagement_rates:
            avg_engagement = sum(all_engagement_rates) / len(all_engagement_rates)
            insights += f"""
**Engagement Benchmarks:**
- Average Engagement Rate: {avg_engagement:.2f}%
- Market Standard: {'High' if avg_engagement > 5 else 'Medium' if avg_engagement > 2 else 'Developing'} engagement

"""
        
        # Tag analysis
        if all_tags:
            from collections import Counter
            tag_counter = Counter(all_tags)
            common_tags = [tag for tag, count in tag_counter.most_common(10)]
            
            insights += f"""
### Content Strategy Insights

**Popular Tags in {niche.title()}:**
- Primary Keywords: {', '.join(common_tags[:5])}
- Secondary Keywords: {', '.join(common_tags[5:10]) if len(common_tags) > 5 else 'Additional research needed'}

**Strategic Recommendations:**
1. **Content Optimization**: Target the popular tags identified above
2. **Performance Goals**: Aim for {self._format_number(sum(all_views) / len(all_views)) if all_views else 0} views per video
3. **Engagement Strategy**: Focus on improving engagement beyond {sum(all_engagement_rates) / len(all_engagement_rates):.1f if all_engagement_rates else 0}%
4. **Content Gaps**: Look for underutilized tags and topics in competitor content
5. **Posting Strategy**: Analyze competitor upload patterns for optimal timing

"""
        
        insights += f"""
---

## 🚀 Action Plan

### Immediate Actions
1. **Keyword Strategy**: Implement top competitor tags in your content
2. **Performance Baseline**: Set goals based on competitor benchmarks above
3. **Content Planning**: Create content addressing gaps in competitor coverage
4. **Engagement Optimization**: Focus on formats that drive comments and likes

### Monitoring Strategy
1. **Monthly Reviews**: Re-run this analysis monthly to track competitor changes
2. **Performance Tracking**: Compare your metrics against these benchmarks
3. **Trend Identification**: Monitor tag trends and content themes
4. **Opportunity Spotting**: Look for declining competitor performance to capitalize on

**Next Steps:**
- Use the yt-dlp commands provided to gather more detailed data
- Implement A/B testing based on competitor successful formats  
- Build content calendar incorporating competitor insights
- Track your progress against these performance benchmarks
        """
        
        return insights
    
    def _format_number(self, num: float) -> str:
        """Format number with appropriate suffix"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.0f}"
    
    def _generate_usage_guide(self) -> str:
        """Generate usage guide for the tool"""
        return """
# 🎯 yt-dlp Competitor Analysis Tool

**No competitor URLs provided.** This tool requires YouTube channel URLs to analyze.

## Usage Examples

### Basic Analysis
```python
ytdlp_competitor_analysis(
    competitor_urls=[
        "https://youtube.com/@channelname1",
        "https://youtube.com/@channelname2"
    ],
    niche="gaming",
    max_videos=20
)
```

### Channel URL Formats Supported
- `https://youtube.com/@channelhandle`
- `https://youtube.com/c/channelname`
- `https://youtube.com/channel/CHANNEL_ID`
- `https://youtube.com/user/username`

## What This Tool Extracts

### Channel Overview
- Channel name and ID
- Total video count (up to specified limit)
- Upload frequency patterns

### Performance Metrics  
- View counts per video
- Average, median, and range of views
- Total channel views (from analyzed videos)

### Content Analysis
- Video titles and lengths
- Tags used by competitors
- Upload dates and patterns

### Engagement Data
- Like counts and ratios
- Comment counts and engagement rates
- Video duration analysis

## Requirements
- yt-dlp must be installed: `pip install yt-dlp`
- Internet connection for data extraction
- Valid YouTube channel URLs

**Tip:** Start with 2-3 key competitors and max_videos=10 for faster analysis.
        """.strip()
    
    def _generate_installation_guide(self) -> str:
        """Generate yt-dlp installation guide"""
        return """
# ❌ yt-dlp Not Available

This tool requires `yt-dlp` to be installed for YouTube data extraction.

## Installation Options

### Option 1: pip install
```bash
pip install yt-dlp
```

### Option 2: uv add (if using uv)
```bash
uv add yt-dlp
```

### Option 3: System package manager
```bash
# macOS with Homebrew
brew install yt-dlp

# Ubuntu/Debian
sudo apt install yt-dlp

# Windows with Chocolatey
choco install yt-dlp
```

## Verify Installation
```bash
yt-dlp --version
```

## Alternative: Manual Commands

If you prefer to run yt-dlp commands manually, here are the key commands:

### Get Channel Video List
```bash
yt-dlp --dump-json --flat-playlist "https://youtube.com/@channelname/videos" > videos.json
```

### Get Detailed Video Data
```bash
yt-dlp --write-info-json --skip-download "https://youtube.com/@channelname/videos" -o "%(uploader)s/%(title)s"
```

### Get Channel with Comments
```bash
yt-dlp --get-comments --write-info-json --skip-download "https://youtube.com/@channelname/videos"
```

**Benefits of using this tool:**
- Automated analysis across multiple competitors
- Structured performance comparison
- Strategic insights generation
- Comprehensive reporting

Once yt-dlp is installed, try the analysis again!
        """.strip()


# Create tool instance
ytdlp_competitor_tool = YtDlpCompetitorTool()

# Export tools
YTDLP_COMPETITOR_TOOLS = [
    ytdlp_competitor_tool
]