"""Simple competitor analysis tool without Google API dependencies"""

from typing import Dict, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


class SimpleCompetitorInput(BaseModel):
    """Input for simple competitor analysis tool"""
    competitor_urls: List[str] = Field(description="List of competitor YouTube channel URLs to analyze")
    niche: str = Field(description="Content niche for contextual analysis")


class SimpleCompetitorTool(BaseTool):
    """Simple competitor analysis tool that works without API keys"""
    
    name: str = "simple_competitor_analysis"
    description: str = "Analyze competitor YouTube channels using web scraping (no API key required)"
    args_schema: type = SimpleCompetitorInput
    
    def _run(self, **kwargs) -> str:
        """Run simple competitor analysis with flexible argument handling"""
        try:
            # Extract parameters safely
            competitor_urls = kwargs.get('competitor_urls', [])
            niche = kwargs.get('niche', 'general')
            
            # Convert single URL to list if needed
            if isinstance(competitor_urls, str):
                competitor_urls = [competitor_urls]
            
            # Validate inputs
            if not competitor_urls:
                return """
# Simple Competitor Analysis

❌ **No competitor URLs provided**

To analyze competitors, please provide YouTube channel URLs. You can:
1. Search for competitors manually
2. Provide specific channel URLs you want to analyze
3. Use general market research to identify key players in your niche

**Example competitor URLs format:**
- https://youtube.com/@channelname
- https://youtube.com/c/channelname
- https://youtube.com/channel/CHANNEL_ID
"""
            
            results = self._analyze_competitors_simple(competitor_urls, niche)
            return results
            
        except Exception as e:
            return f"❌ Error in competitor analysis: {str(e)}\n\nThis tool provides basic competitor analysis without requiring API keys."
    
    def _analyze_competitors_simple(self, urls: List[str], niche: str) -> str:
        """Simple competitor analysis using web scraping"""
        
        analysis_results = []
        successful_analyses = 0
        
        for i, url in enumerate(urls[:5], 1):  # Limit to 5 competitors
            try:
                result = self._scrape_channel_info(url)
                if result:
                    analysis_results.append(f"""
**Competitor {i}: {result['name']}**
- Channel URL: {url}
- Estimated Subscribers: {result['subscribers']}
- Description: {result['description'][:100]}...
- Analysis Method: Web scraping
- Status: ✅ Basic info extracted
""")
                    successful_analyses += 1
                else:
                    analysis_results.append(f"""
**Competitor {i}: Analysis Failed**
- Channel URL: {url}
- Status: ❌ Unable to extract information
""")
            except Exception as e:
                analysis_results.append(f"""
**Competitor {i}: Error**
- Channel URL: {url}
- Error: {str(e)}
- Status: ❌ Analysis failed
""")
        
        # Generate insights based on available data
        insights = self._generate_simple_insights(niche, successful_analyses)
        
        return f"""
# 🎯 Simple Competitor Analysis Report

**Niche:** {niche}
**Competitors Analyzed:** {len(urls)}
**Successful Extractions:** {successful_analyses}
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Competitor Overview

{''.join(analysis_results)}

---

## 💡 Strategic Insights

{insights}

---

## 🚀 Next Steps

1. **Deep Dive**: For detailed analytics, consider setting up YouTube API access
2. **Content Analysis**: Manually review successful competitors' recent videos
3. **Engagement Study**: Check their community tab and comment engagement
4. **Posting Schedule**: Monitor their upload patterns over time
5. **Collaboration**: Consider reaching out for potential partnerships

**Note:** This analysis uses web scraping and provides basic information. For comprehensive analytics including view counts, engagement rates, and detailed performance metrics, YouTube API access is recommended.
        """.strip()
    
    def _scrape_channel_info(self, url: str) -> Dict[str, str]:
        """Scrape basic channel information"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract channel name
            name = None
            title_tag = soup.find('title')
            if title_tag:
                name = title_tag.get_text().replace(' - YouTube', '').strip()
            
            # Try to extract from meta tags
            if not name:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    name = meta_title.get('content', '').replace(' - YouTube', '').strip()
            
            # Extract description
            description = ""
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Try to find subscriber count (this is tricky with scraping)
            subscribers = self._extract_subscriber_count(soup)
            
            return {
                'name': name or 'Unknown Channel',
                'description': description or 'No description available',
                'subscribers': subscribers
            }
            
        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return None
    
    def _extract_subscriber_count(self, soup: BeautifulSoup) -> str:
        """Try to extract subscriber count from page"""
        try:
            text = soup.get_text().lower()
            
            # Look for subscriber patterns
            patterns = [
                r'(\d+(?:\.\d+)?[kmb]?)\s*subscriber',
                r'(\d+(?:\.\d+)?[kmb]?)\s*subs',
                r'(\d+(?:,\d{3})*)\s*subscriber'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
            
            return "Unknown"
            
        except Exception:
            return "Unknown"
    
    def _generate_simple_insights(self, niche: str, successful_count: int) -> str:
        """Generate basic insights based on analysis"""
        
        if successful_count == 0:
            return f"""
❌ **Limited Analysis Available**

Unable to extract competitor data. This could be due to:
- YouTube's anti-scraping measures
- Channel privacy settings
- Network connectivity issues

**Recommendations:**
- Try again with different competitor URLs
- Consider using YouTube API for reliable data access
- Manually research competitors by visiting their channels
- Look for public analytics tools or social media insights
"""
        
        insights = f"""
✅ **Analysis Summary**

Successfully analyzed {successful_count} competitor(s) in the {niche} niche.

**Key Observations:**
- Basic channel information extracted via web scraping
- Competitor landscape identified for {niche} content
- Foundation established for competitive intelligence

**Strategic Recommendations:**

1. **Content Gap Analysis**: Manually review competitor videos to identify:
   - Underserved topics in {niche}
   - Popular content formats
   - Engagement patterns in comments

2. **Differentiation Strategy**: 
   - Find unique angles not covered by competitors
   - Develop distinctive content style
   - Target underserved audience segments

3. **Performance Benchmarking**:
   - Set realistic growth targets based on competitor success
   - Monitor competitor upload schedules
   - Track their viral content for inspiration

4. **Collaboration Opportunities**:
   - Identify potential collaboration partners
   - Look for cross-promotion possibilities
   - Build relationships in the {niche} community
"""
        
        return insights


# Create tool instance
simple_competitor_tool = SimpleCompetitorTool()

# Export tools
SIMPLE_COMPETITOR_TOOLS = [
    simple_competitor_tool
]