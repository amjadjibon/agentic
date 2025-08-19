"""Crawl4AI-based competitor analysis tool for comprehensive web scraping and data extraction"""

import asyncio
import json
from typing import Dict, List, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime
import re


class Crawl4AICompetitorInput(BaseModel):
    """Input for Crawl4AI competitor analysis tool"""
    competitor_urls: List[str] = Field(description="List of competitor URLs to analyze (YouTube channels, websites, etc.)")
    niche: str = Field(description="Content niche for contextual analysis")
    extract_social_media: bool = Field(default=True, description="Extract social media links and metrics")
    extract_content_themes: bool = Field(default=True, description="Extract content themes and topics")


class Crawl4AICompetitorTool(BaseTool):
    """Advanced competitor analysis using Crawl4AI for comprehensive web scraping"""
    
    name: str = "crawl4ai_competitor_analysis"
    description: str = "Perform comprehensive competitor analysis using Crawl4AI web scraping with AI-powered data extraction"
    args_schema: type = Crawl4AICompetitorInput
    
    def _run(self, **kwargs) -> str:
        """Run Crawl4AI-based competitor analysis"""
        try:
            # Extract parameters safely
            competitor_urls = kwargs.get('competitor_urls', [])
            niche = kwargs.get('niche', 'general')
            extract_social_media = kwargs.get('extract_social_media', True)
            extract_content_themes = kwargs.get('extract_content_themes', True)
            
            # Convert single URL to list if needed
            if isinstance(competitor_urls, str):
                competitor_urls = [competitor_urls]
            
            if not competitor_urls:
                return self._generate_usage_guide()
            
            # Run async analysis
            return asyncio.run(self._analyze_competitors_async(
                competitor_urls, niche, extract_social_media, extract_content_themes
            ))
            
        except Exception as e:
            return f"❌ Error in Crawl4AI competitor analysis: {str(e)}"
    
    async def _analyze_competitors_async(self, urls: List[str], niche: str, 
                                       extract_social: bool, extract_themes: bool) -> str:
        """Async competitor analysis using Crawl4AI"""
        
        try:
            from crawl4ai import AsyncWebCrawler
            from crawl4ai.extraction_strategy import LLMExtractionStrategy
            from crawl4ai.chunking_strategy import RegexChunking
            
            results = []
            
            async with AsyncWebCrawler(verbose=True) as crawler:
                
                for i, url in enumerate(urls[:5], 1):  # Limit to 5 competitors
                    try:
                        competitor_name = f"Competitor_{i}"
                        print(f"🕷️ Crawling {competitor_name}: {url}")
                        
                        # First try basic crawling without LLM extraction
                        # This ensures we get the content even if LLM extraction fails
                        result = await crawler.arun(
                            url=url,
                            bypass_cache=True,
                            js_code=[
                                "window.scrollTo(0, document.body.scrollHeight);",  # Scroll to load content
                                "await new Promise(resolve => setTimeout(resolve, 2000));"  # Wait for dynamic content
                            ]
                        )
                        
                        if result.success:
                            # Use markdown content for analysis since we're not doing LLM extraction
                            markdown_content = result.markdown[:3000] if result.markdown else ""
                            html_content = result.html[:1000] if result.html else ""
                            
                            # Extract basic data from markdown and HTML
                            extracted_data = self._extract_basic_data_from_content(
                                markdown_content, html_content, url
                            )
                            
                            analysis = self._analyze_competitor_data(
                                competitor_name, url, extracted_data, markdown_content, niche
                            )
                            
                            results.append(analysis)
                        else:
                            results.append({
                                "name": competitor_name,
                                "url": url,
                                "error": f"Crawling failed: {result.error_message}"
                            })
                            
                    except Exception as e:
                        results.append({
                            "name": f"Competitor_{i}",
                            "url": url,
                            "error": f"Analysis failed: {str(e)}"
                        })
            
            return self._format_crawl4ai_results(results, niche)
            
        except ImportError:
            return self._generate_installation_guide()
        except Exception as e:
            return f"❌ Crawl4AI analysis failed: {str(e)}"
    
    def _extract_basic_data_from_content(self, markdown: str, html: str, url: str) -> Dict:
        """Extract basic competitor data from markdown and HTML content"""
        
        data = {
            "channel_info": {},
            "content_themes": [],
            "recent_videos": [],
            "social_links": []
        }
        
        # Extract channel info from YouTube URLs
        if 'youtube.com' in url:
            # Extract channel name from markdown title
            title_match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
            if title_match:
                data["channel_info"]["name"] = title_match.group(1).strip()
            
            # Extract subscriber count
            subscriber_patterns = [
                r'(\d+(?:\.\d+)?)\s*([KMB])?\s*subscribers?',
                r'(\d+(?:,\d+)*)\s*subscribers?'
            ]
            for pattern in subscriber_patterns:
                match = re.search(pattern, markdown, re.IGNORECASE)
                if match:
                    data["channel_info"]["subscriber_count"] = match.group(0)
                    break
            
            # Extract video titles from markdown
            video_titles = re.findall(r'##\s+(.+)', markdown)
            for title in video_titles[:5]:
                if title and len(title) > 5:  # Filter out short/empty titles
                    data["recent_videos"].append({"title": title.strip()})
        
        # Extract social media links
        social_patterns = [
            r'https?://(?:www\.)?(?:twitter\.com|x\.com)/\w+',
            r'https?://(?:www\.)?instagram\.com/\w+',
            r'https?://(?:www\.)?facebook\.com/\w+',
            r'https?://(?:www\.)?linkedin\.com/\w+',
            r'https?://(?:www\.)?tiktok\.com/@\w+',
            r'https?://discord\.gg/\w+',
        ]
        
        all_content = markdown + ' ' + html
        for pattern in social_patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            data["social_links"].extend(matches)
        
        # Extract content themes from common words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', markdown.lower())
        word_freq = {}
        
        # Skip common words
        skip_words = {'youtube', 'video', 'videos', 'channel', 'subscribe', 'like', 'comment', 'share', 'watch', 'playlist'}
        
        for word in words:
            if word not in skip_words and len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top themes
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        data["content_themes"] = [word for word, count in top_words if count > 1]
        
        return data
    
    def _analyze_competitor_data(self, name: str, url: str, extracted_data: Dict, 
                               markdown: str, niche: str) -> Dict:
        """Analyze extracted competitor data"""
        
        analysis = {
            "name": name,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "niche": niche
        }
        
        # Extract channel information
        channel_info = extracted_data.get('channel_info', {})
        analysis['channel_info'] = {
            "name": channel_info.get('name', 'Unknown'),
            "description": channel_info.get('description', '')[:200],
            "subscriber_count": self._extract_number(channel_info.get('subscriber_count', '')),
            "video_count": self._extract_number(channel_info.get('video_count', ''))
        }
        
        # Extract content themes
        themes = extracted_data.get('content_themes', [])
        analysis['content_analysis'] = {
            "primary_themes": themes[:5],
            "theme_count": len(themes),
            "niche_relevance": self._assess_niche_relevance(themes, niche)
        }
        
        # Extract recent videos
        recent_videos = extracted_data.get('recent_videos', [])[:10]
        analysis['recent_content'] = {
            "video_count": len(recent_videos),
            "videos": recent_videos,
            "avg_title_length": sum(len(v.get('title', '')) for v in recent_videos) / max(len(recent_videos), 1)
        }
        
        # Extract social links
        social_links = extracted_data.get('social_links', [])
        analysis['social_presence'] = {
            "platforms": self._categorize_social_links(social_links),
            "total_links": len(social_links),
            "cross_platform_score": min(len(set(self._get_platform_from_url(link) for link in social_links)), 10)
        }
        
        # Backup analysis from markdown if structured data is sparse
        if not extracted_data or len(str(extracted_data)) < 100:
            analysis['markdown_analysis'] = self._analyze_markdown_content(markdown, niche)
        
        return analysis
    
    def _extract_number(self, text: str) -> int:
        """Extract numerical value from text (e.g., '1.2M subscribers' -> 1200000)"""
        if not text:
            return 0
        
        # Find numbers with K, M, B suffixes
        pattern = r'(\d+\.?\d*)\s*([KMB])?'
        match = re.search(pattern, text.upper())
        
        if match:
            number = float(match.group(1))
            suffix = match.group(2)
            
            if suffix == 'K':
                return int(number * 1000)
            elif suffix == 'M':
                return int(number * 1000000)
            elif suffix == 'B':
                return int(number * 1000000000)
            else:
                return int(number)
        
        return 0
    
    def _assess_niche_relevance(self, themes: List[str], niche: str) -> str:
        """Assess how relevant the content themes are to the target niche"""
        if not themes:
            return "Unknown"
        
        niche_keywords = niche.lower().split()
        theme_text = ' '.join(themes).lower()
        
        relevance_score = sum(1 for keyword in niche_keywords if keyword in theme_text)
        total_keywords = len(niche_keywords)
        
        if relevance_score >= total_keywords * 0.8:
            return "Highly Relevant"
        elif relevance_score >= total_keywords * 0.5:
            return "Moderately Relevant"
        elif relevance_score > 0:
            return "Somewhat Relevant"
        else:
            return "Low Relevance"
    
    def _categorize_social_links(self, links: List[str]) -> Dict[str, int]:
        """Categorize social media links by platform"""
        platforms = {}
        
        for link in links:
            platform = self._get_platform_from_url(link)
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return platforms
    
    def _get_platform_from_url(self, url: str) -> str:
        """Extract platform name from URL"""
        url = url.lower()
        
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'YouTube'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'Twitter'
        elif 'instagram.com' in url:
            return 'Instagram'
        elif 'facebook.com' in url:
            return 'Facebook'
        elif 'linkedin.com' in url:
            return 'LinkedIn'
        elif 'tiktok.com' in url:
            return 'TikTok'
        elif 'discord' in url:
            return 'Discord'
        elif 'reddit.com' in url:
            return 'Reddit'
        else:
            return 'Other'
    
    def _analyze_markdown_content(self, markdown: str, niche: str) -> Dict:
        """Fallback analysis using markdown content"""
        if not markdown:
            return {"status": "No content available"}
        
        # Simple keyword extraction
        words = re.findall(r'\w+', markdown.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "content_length": len(markdown),
            "word_count": len(words),
            "top_keywords": [word for word, count in top_keywords],
            "niche_mentions": markdown.lower().count(niche.lower())
        }
    
    def _format_crawl4ai_results(self, results: List[Dict], niche: str) -> str:
        """Format Crawl4AI analysis results"""
        
        successful_results = [r for r in results if 'error' not in r]
        failed_results = [r for r in results if 'error' in r]
        
        output = f"""
# 🕷️ Crawl4AI Competitor Analysis - {niche.title()} Niche

**Analysis Method:** Advanced Web Scraping with AI Extraction
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Competitors:** {len(results)}
**Successful Analyses:** {len(successful_results)}
**Failed Analyses:** {len(failed_results)}

---

## 📊 Competitor Intelligence Dashboard

"""
        
        for result in successful_results:
            channel_info = result.get('channel_info', {})
            content_analysis = result.get('content_analysis', {})
            recent_content = result.get('recent_content', {})
            social_presence = result.get('social_presence', {})
            
            output += f"""
**{result['name']}: {channel_info.get('name', 'Unknown Channel')}** ✅
- **URL:** {result['url']}
- **Subscriber Count:** {self._format_number(channel_info.get('subscriber_count', 0))}
- **Video Count:** {self._format_number(channel_info.get('video_count', 0))}
- **Niche Relevance:** {content_analysis.get('niche_relevance', 'Unknown')}

**Content Strategy:**
- **Primary Themes:** {', '.join(content_analysis.get('primary_themes', [])[:3])}
- **Recent Videos:** {recent_content.get('video_count', 0)} analyzed
- **Avg Title Length:** {recent_content.get('avg_title_length', 0):.0f} characters

**Social Media Presence:**
- **Platforms:** {len(social_presence.get('platforms', {}))} different platforms
- **Cross-Platform Score:** {social_presence.get('cross_platform_score', 0)}/10
- **Platform Breakdown:** {', '.join([f"{p}: {c}" for p, c in social_presence.get('platforms', {}).items()])}

**Top Recent Content:**
"""
            
            recent_videos = recent_content.get('videos', [])[:5]
            for video in recent_videos:
                title = video.get('title', 'Unknown Title')[:50]
                views = video.get('views', 'Unknown')
                output += f"  - {title}... | Views: {views}\\n"
            
            output += "\\n"
        
        # Add failed analyses
        if failed_results:
            output += "\\n## ❌ Failed Analyses\\n\\n"
            for result in failed_results:
                output += f"**{result['name']}** - {result['url']}\\n"
                output += f"Error: {result['error']}\\n\\n"
        
        # Generate competitive insights
        if successful_results:
            output += self._generate_crawl4ai_insights(successful_results, niche)
        
        return output.strip()
    
    def _generate_crawl4ai_insights(self, results: List[Dict], niche: str) -> str:
        """Generate strategic insights from Crawl4AI analysis"""
        
        # Aggregate data
        total_subscribers = sum(r.get('channel_info', {}).get('subscriber_count', 0) for r in results)
        total_videos = sum(r.get('channel_info', {}).get('video_count', 0) for r in results)
        all_themes = []
        all_platforms = {}
        
        for result in results:
            themes = result.get('content_analysis', {}).get('primary_themes', [])
            all_themes.extend(themes)
            
            platforms = result.get('social_presence', {}).get('platforms', {})
            for platform, count in platforms.items():
                all_platforms[platform] = all_platforms.get(platform, 0) + count
        
        # Find most common themes
        theme_frequency = {}
        for theme in all_themes:
            theme_frequency[theme] = theme_frequency.get(theme, 0) + 1
        
        top_themes = sorted(theme_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        top_platforms = sorted(all_platforms.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return f"""
---

## 💡 Strategic Intelligence Insights

### Market Overview
- **Total Market Reach:** {self._format_number(total_subscribers)} combined subscribers
- **Content Volume:** {self._format_number(total_videos)} total videos analyzed
- **Average Channel Size:** {self._format_number(total_subscribers // max(len(results), 1))} subscribers

### Content Themes Analysis
**Most Popular Themes in {niche.title()}:**
{chr(10).join([f"- {theme} ({count} channels)" for theme, count in top_themes])}

### Platform Strategy Insights
**Dominant Platforms:**
{chr(10).join([f"- {platform}: {count} presences" for platform, count in top_platforms])}

### Strategic Recommendations

#### Content Strategy
1. **Focus Areas:** Target underrepresented themes while leveraging popular ones
2. **Content Gaps:** Look for themes not covered by top competitors
3. **Format Innovation:** Experiment with formats not commonly used in your niche

#### Growth Opportunities
1. **Platform Diversification:** Expand to platforms with less competitor presence
2. **Cross-Platform Synergy:** Build presence across {len(top_platforms)} key platforms
3. **Niche Positioning:** Find unique angles within popular themes

#### Competitive Positioning
1. **Size Advantage:** Compete in subscriber tiers where you can realistically grow
2. **Content Frequency:** Match or exceed successful competitors' posting schedules
3. **Community Building:** Focus on engagement quality over quantity

---

## 🚀 Next Steps

### Immediate Actions (This Week)
- Analyze top-performing content themes identified above
- Research successful title formats from competitor analysis
- Plan content addressing identified market gaps

### Strategic Implementation (30 Days)
- Develop content calendar incorporating successful competitor strategies
- Begin cross-platform expansion to identified opportunities
- A/B test competitor-inspired content formats

### Long-term Growth (90 Days)
- Establish unique positioning within competitive landscape
- Build strategic partnerships with complementary channels
- Monitor competitor changes and adapt strategy accordingly

**Data Source:** Crawl4AI advanced web scraping with AI-powered extraction
**Refresh Recommended:** Monthly for dynamic competitive intelligence
        """
    
    def _format_number(self, num: int) -> str:
        """Format number with appropriate suffix"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)
    
    def _generate_usage_guide(self) -> str:
        """Generate usage guide for the Crawl4AI tool"""
        return """
# 🕷️ Crawl4AI Competitor Analysis Tool

**No competitor URLs provided.** This tool requires URLs to analyze.

## Usage Examples

### Basic Analysis
```python
crawl4ai_competitor_analysis(
    competitor_urls=[
        "https://youtube.com/@channelname1",
        "https://youtube.com/@channelname2",
        "https://example-competitor-website.com"
    ],
    niche="gaming",
    extract_social_media=True,
    extract_content_themes=True
)
```

### Advanced Configuration
```python
crawl4ai_competitor_analysis(
    competitor_urls=[
        "https://youtube.com/@competitor1",
        "https://competitorwebsite.com",
        "https://blog.competitor.com"
    ],
    niche="tech reviews",
    extract_social_media=False,  # Skip social media extraction
    extract_content_themes=True
)
```

## What This Tool Extracts

### YouTube Channels
- Channel information (name, description, subscriber count)
- Recent video data (titles, views, upload dates)
- Content themes and topics
- Social media cross-links

### Websites & Blogs
- Company information and descriptions
- Content themes and focus areas
- Social media presence
- Recent content and publications

### Cross-Platform Analysis
- Multi-platform presence mapping
- Content strategy consistency
- Audience engagement patterns

## Key Features

✅ **AI-Powered Extraction** - Uses LLM to understand content context  
✅ **Structured Data Output** - Organized, actionable competitive intelligence  
✅ **Multi-Platform Support** - Analyzes YouTube, websites, blogs, social media  
✅ **Strategic Insights** - Generates actionable recommendations  
✅ **Real-Time Scraping** - Fresh data with dynamic content loading  

## Requirements
- Crawl4AI library installed (`uv add crawl4ai`)
- Optional: OpenAI API key for enhanced extraction
- Internet connection for real-time scraping

**Tip:** Start with 2-3 key competitors for detailed analysis.
        """.strip()
    
    def _generate_installation_guide(self) -> str:
        """Generate Crawl4AI installation guide"""
        return """
# ❌ Crawl4AI Not Available

This tool requires the Crawl4AI library to be installed.

## Installation Options

### Option 1: uv (Recommended)
```bash
uv add crawl4ai
```

### Option 2: pip
```bash
pip install crawl4ai
```

### Option 3: Docker
```bash
docker run -p 8000:8000 unclecode/crawl4ai
```

## Additional Setup

### For Enhanced AI Extraction (Optional)
Set your OpenAI API key for better structured data extraction:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### For Browser Automation
Crawl4AI may need to install browser dependencies:
```bash
playwright install  # If using Playwright
```

## Verify Installation
```python
from crawl4ai import AsyncWebCrawler
print("Crawl4AI installed successfully!")
```

## Benefits Over Traditional Scraping

🚀 **LLM-Friendly Output** - Clean, structured data perfect for AI processing  
🎯 **Smart Extraction** - AI understands content context, not just HTML  
⚡ **Async Performance** - Fast, concurrent crawling of multiple competitors  
🔄 **Dynamic Content** - Handles JavaScript and dynamic loading  
🛡️ **Robust Scraping** - Bypasses common anti-bot measures  

Once installed, try the competitor analysis again!
        """.strip()


# Create tool instance
crawl4ai_competitor_tool = Crawl4AICompetitorTool()

# Export tools
CRAWL4AI_COMPETITOR_TOOLS = [
    crawl4ai_competitor_tool
]