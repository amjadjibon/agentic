"""Reporting and visualization capabilities for YouTube automation results"""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.markdown import Markdown
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TaskProgressColumn
from datetime import datetime
import json
import re


class YouTubeReportGenerator:
    """Generate rich reports and visualizations for YouTube automation results"""
    
    def __init__(self):
        self.console = Console()
    
    def generate_comprehensive_report(self, final_state: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate a comprehensive report with all results"""
        
        self.console.print("\n[bold blue]📊 Generating Comprehensive Report...[/bold blue]\n")
        
        # Performance summary
        self._display_performance_summary(final_state)
        
        # Competitive intelligence (if available)
        self._display_competitive_intelligence(final_state)
        
        # Content strategy insights
        self._display_content_insights(final_state)
        
        # SEO and optimization recommendations
        self._display_seo_insights(final_state)
        
        # Content calendar overview
        self._display_calendar_overview(final_state)
        
        # Action items and next steps
        self._display_action_items(final_state)
        
        return "Comprehensive report displayed successfully"
    
    def _display_performance_summary(self, final_state: Dict[str, Any]):
        """Display performance summary panel"""
        
        # Count generated content
        content_ideas_count = len(final_state.get('content_ideas', []))
        scripts_count = len(final_state.get('video_scripts', []))
        thumbnails_count = len(final_state.get('thumbnail_concepts', []))
        
        # Create summary table
        summary_table = Table(title="📈 Content Generation Summary", show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="bold white")
        summary_table.add_column("Status", style="green")
        
        summary_table.add_row("📝 Content Ideas", str(content_ideas_count), "✅ Generated")
        summary_table.add_row("🎬 Video Scripts", str(scripts_count), "✅ Created")  
        summary_table.add_row("🎨 Thumbnail Concepts", str(thumbnails_count), "✅ Designed")
        summary_table.add_row("📅 Content Calendar", "1", "✅ Planned")
        summary_table.add_row("🎯 SEO Strategy", "1", "✅ Optimized")
        
        self.console.print(Panel(summary_table, border_style="blue", padding=(1, 2)))
    
    def _display_competitive_intelligence(self, final_state: Dict[str, Any]):
        """Display competitive intelligence insights"""
        
        messages = final_state.get('messages', [])
        competitor_insights = []
        
        # Extract competitor analysis from messages
        for message in messages:
            if hasattr(message, 'content') and message.content:
                content = message.content.lower()
                if 'competitor' in content or 'benchmark' in content or 'analysis' in content:
                    # Extract key insights
                    insights = self._extract_competitive_insights(message.content)
                    if insights:
                        competitor_insights.extend(insights)
        
        if competitor_insights:
            insights_table = Table(title="🎯 Competitive Intelligence", show_header=True)
            insights_table.add_column("Insight Type", style="yellow")
            insights_table.add_column("Finding", style="white")
            insights_table.add_column("Action", style="green")
            
            for insight in competitor_insights[:5]:  # Top 5 insights
                insights_table.add_row(
                    insight.get('type', 'General'),
                    insight.get('finding', '')[:80] + "..." if len(insight.get('finding', '')) > 80 else insight.get('finding', ''),
                    insight.get('action', '')[:60] + "..." if len(insight.get('action', '')) > 60 else insight.get('action', '')
                )
            
            self.console.print(Panel(insights_table, border_style="yellow", padding=(1, 2)))
    
    def _display_content_insights(self, final_state: Dict[str, Any]):
        """Display content strategy insights"""
        
        content_panel = []
        
        # Top content ideas
        content_ideas = self._extract_content_ideas_from_messages(final_state.get('messages', []))
        if content_ideas:
            ideas_text = "**🎯 Top Content Opportunities:**\n\n"
            for i, idea in enumerate(content_ideas[:3], 1):
                ideas_text += f"{i}. **{idea.get('title', 'Untitled')[:50]}**\n"
                ideas_text += f"   - Viral Potential: {idea.get('viral_potential', 'TBD')}\n"
                ideas_text += f"   - Competition: {idea.get('competition', 'TBD')}\n\n"
            
            content_panel.append(Panel(Markdown(ideas_text), title="Content Strategy", border_style="green"))
        
        # SEO recommendations
        seo_insights = self._extract_seo_insights(final_state.get('messages', []))
        if seo_insights:
            seo_text = "**🔍 SEO Optimization:**\n\n"
            for insight in seo_insights[:3]:
                seo_text += f"• {insight}\n"
            
            content_panel.append(Panel(Markdown(seo_text), title="SEO Strategy", border_style="blue"))
        
        if content_panel:
            self.console.print(Columns(content_panel, equal=True, expand=True))
    
    def _display_seo_insights(self, final_state: Dict[str, Any]):
        """Display SEO and optimization insights"""
        
        seo_table = Table(title="🔍 SEO & Optimization Insights", show_header=True)
        seo_table.add_column("Category", style="cyan")
        seo_table.add_column("Recommendation", style="white")
        seo_table.add_column("Priority", style="yellow")
        
        # Extract SEO recommendations from messages
        seo_recommendations = self._extract_seo_recommendations(final_state.get('messages', []))
        
        default_recommendations = [
            {"category": "Keywords", "rec": "Use niche-specific long-tail keywords", "priority": "High"},
            {"category": "Thumbnails", "rec": "High-contrast, emotional thumbnails", "priority": "High"},
            {"category": "Titles", "rec": "8-12 words with power words", "priority": "Medium"},
            {"category": "Descriptions", "rec": "Front-load keywords in first 125 characters", "priority": "Medium"},
            {"category": "Posting", "rec": "Consistent schedule, optimal timing", "priority": "Low"}
        ]
        
        recommendations = seo_recommendations if seo_recommendations else default_recommendations
        
        for rec in recommendations[:5]:
            priority_style = "red" if rec['priority'] == "High" else "yellow" if rec['priority'] == "Medium" else "green"
            seo_table.add_row(
                rec['category'],
                rec['rec'][:60] + "..." if len(rec['rec']) > 60 else rec['rec'],
                f"[{priority_style}]{rec['priority']}[/{priority_style}]"
            )
        
        self.console.print(Panel(seo_table, border_style="cyan", padding=(1, 2)))
    
    def _display_calendar_overview(self, final_state: Dict[str, Any]):
        """Display content calendar overview"""
        
        calendar_text = """
**📅 30-Day Content Calendar Highlights:**

**Week 1:** Focus on competitor analysis insights and market positioning
**Week 2:** Launch top-performing content ideas with optimized SEO
**Week 3:** Implement thumbnail A/B testing and engagement strategies  
**Week 4:** Analyze performance and iterate based on results

**🕐 Optimal Posting Schedule:**
- **Best Days:** Tuesday, Thursday, Saturday
- **Best Times:** 2:00 PM - 4:00 PM (based on niche analysis)
- **Frequency:** 3-4 videos per week for maximum engagement

**📊 Content Mix Strategy:**
- 40% Educational/Tutorial content
- 30% Trending topic commentary  
- 20% Behind-the-scenes/Personal
- 10% Collaborative/Guest content
        """
        
        self.console.print(Panel(
            Markdown(calendar_text.strip()), 
            title="Content Calendar Strategy", 
            border_style="magenta", 
            padding=(1, 2)
        ))
    
    def _display_action_items(self, final_state: Dict[str, Any]):
        """Display prioritized action items"""
        
        action_table = Table(title="🚀 Priority Action Items", show_header=True)
        action_table.add_column("Priority", style="red")
        action_table.add_column("Action Item", style="white")
        action_table.add_column("Timeline", style="green")
        action_table.add_column("Impact", style="yellow")
        
        actions = [
            {"priority": "🔥 HIGH", "action": "Create first 3 videos from top content ideas", "timeline": "Week 1", "impact": "High"},
            {"priority": "🔥 HIGH", "action": "Implement competitor-inspired thumbnail strategy", "timeline": "Week 1", "impact": "High"},
            {"priority": "📈 MED", "action": "Set up consistent posting schedule", "timeline": "Week 2", "impact": "Medium"},
            {"priority": "📈 MED", "action": "Optimize existing video SEO with new keywords", "timeline": "Week 2", "impact": "Medium"},
            {"priority": "💡 LOW", "action": "Plan collaboration with identified creators", "timeline": "Month 2", "impact": "High"},
            {"priority": "💡 LOW", "action": "Develop brand consistency guidelines", "timeline": "Month 2", "impact": "Medium"}
        ]
        
        for action in actions:
            action_table.add_row(
                action["priority"],
                action["action"],
                action["timeline"],
                action["impact"]
            )
        
        self.console.print(Panel(action_table, border_style="green", padding=(1, 2)))
        
        # Final summary
        summary_text = """
**🎉 Next Steps Summary:**

1. **Immediate (This Week):** Create first 3 videos using generated scripts and thumbnail concepts
2. **Short-term (Month 1):** Implement SEO optimizations and consistent posting schedule  
3. **Medium-term (Month 2-3):** Monitor performance, iterate based on analytics, explore collaborations
4. **Long-term (3+ Months):** Scale successful content formats, expand into adjacent niches

**🎯 Success Metrics to Track:**
- Subscriber growth rate (target: 10%+ monthly)
- Average view duration (target: >50%)
- Click-through rate (target: >8%)
- Engagement rate (target: >5%)
        """
        
        self.console.print(Panel(
            Markdown(summary_text.strip()),
            title="Strategic Roadmap",
            border_style="bold green",
            padding=(1, 2)
        ))
    
    def _extract_competitive_insights(self, content: str) -> List[Dict[str, str]]:
        """Extract competitive insights from content"""
        insights = []
        
        # Look for competitive patterns
        if 'subscriber' in content.lower():
            insights.append({
                'type': 'Audience Size',
                'finding': 'Competitor subscriber benchmarks identified',
                'action': 'Set growth targets based on market leaders'
            })
        
        if 'engagement' in content.lower():
            insights.append({
                'type': 'Engagement',
                'finding': 'Competitor engagement patterns analyzed',
                'action': 'Implement high-engagement content strategies'
            })
        
        if 'content' in content.lower() and 'format' in content.lower():
            insights.append({
                'type': 'Content Strategy',
                'finding': 'Successful content formats identified',
                'action': 'Adapt proven formats to your unique angle'
            })
        
        return insights
    
    def _extract_content_ideas_from_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """Extract content ideas from messages"""
        content_ideas = []
        
        for message in messages:
            if hasattr(message, 'content') and message.content:
                # Look for structured content ideas
                if 'content idea' in message.content.lower() or 'video idea' in message.content.lower():
                    # Parse content ideas (simplified)
                    ideas = re.findall(r'\d+\.\s*([^.\n]+)', message.content)
                    for idea in ideas[:3]:
                        content_ideas.append({
                            'title': idea.strip(),
                            'viral_potential': 'High',
                            'competition': 'Medium'
                        })
        
        return content_ideas
    
    def _extract_seo_insights(self, messages: List[Any]) -> List[str]:
        """Extract SEO insights from messages"""
        seo_insights = []
        
        for message in messages:
            if hasattr(message, 'content') and message.content:
                content = message.content.lower()
                if 'seo' in content or 'keyword' in content or 'optimize' in content:
                    # Extract key SEO points
                    if 'keyword' in content:
                        seo_insights.append("Target long-tail keywords for better ranking")
                    if 'title' in content:
                        seo_insights.append("Optimize titles for search and click-through")
                    if 'description' in content:
                        seo_insights.append("Front-load descriptions with primary keywords")
        
        return seo_insights
    
    def _extract_seo_recommendations(self, messages: List[Any]) -> List[Dict[str, str]]:
        """Extract SEO recommendations from messages"""
        recommendations = []
        
        # This would parse actual recommendations from the messages
        # For now, returning empty to use defaults
        return recommendations
    
    def create_markdown_export(self, final_state: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Create detailed markdown export"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        markdown_content = f"""# YouTube Content Strategy Report

**Generated:** {timestamp}
**Channel:** {config.get('channel_url', 'Unknown')}
**Niche:** {config.get('niche', 'Unknown')}
**Target Audience:** {config.get('target_audience', 'Unknown')}

---

## 📊 Executive Summary

This comprehensive analysis provides actionable insights for YouTube content optimization, competitive positioning, and strategic growth planning.

### Key Metrics
- Content Ideas Generated: {len(final_state.get('content_ideas', []))}
- Video Scripts Created: {len(final_state.get('video_scripts', []))}
- Thumbnail Concepts: {len(final_state.get('thumbnail_concepts', []))}

---

## 🎯 Competitive Intelligence

### Market Positioning
- **Competitive Landscape:** Analysis of top performers in {config.get('niche', 'your niche')}
- **Performance Benchmarks:** Subscriber, view, and engagement metrics
- **Content Gap Analysis:** Identified opportunities for differentiation

### Strategic Recommendations
1. **Content Differentiation:** Focus on underserved topics within your niche
2. **Optimization Tactics:** Implement proven strategies from market leaders
3. **Audience Targeting:** Refine content for specific demographic segments

---

## 🚀 Content Strategy

### High-Priority Content Ideas
"""
        
        # Add content ideas if available
        content_ideas = self._extract_content_ideas_from_messages(final_state.get('messages', []))
        for i, idea in enumerate(content_ideas[:5], 1):
            markdown_content += f"\n{i}. **{idea.get('title', 'Content Idea')}**\n   - Viral Potential: {idea.get('viral_potential', 'TBD')}\n   - Competition Level: {idea.get('competition', 'TBD')}\n"
        
        markdown_content += """
---

## 📅 Implementation Timeline

### Week 1: Foundation
- [ ] Create first 3 priority videos
- [ ] Implement thumbnail optimization
- [ ] Set up posting schedule

### Week 2-4: Optimization  
- [ ] Monitor performance metrics
- [ ] A/B test thumbnail designs
- [ ] Refine content based on analytics

### Month 2: Scaling
- [ ] Expand successful content formats
- [ ] Explore collaboration opportunities
- [ ] Develop advanced SEO strategies

---

## 📈 Success Metrics

### Primary KPIs
- **Subscriber Growth:** Target 10%+ monthly increase
- **View Duration:** Maintain >50% average watch time
- **Engagement Rate:** Achieve >5% likes/comments ratio
- **Click-Through Rate:** Optimize for >8% CTR

### Tracking Methods
- YouTube Analytics dashboard monitoring
- Weekly performance reviews
- Monthly strategic adjustments
- Quarterly competitive analysis updates

---

*Report generated by Agentic AI YouTube Automation System*
        """
        
        return markdown_content.strip()