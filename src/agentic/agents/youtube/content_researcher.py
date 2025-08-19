from typing import Optional, TYPE_CHECKING
from .base import BaseYouTubeAgent
from agentic.tools import get_tools_for_agents

if TYPE_CHECKING:
    pass


class ContentResearcherAgent(BaseYouTubeAgent):
    """Agent specialized in content research and trend analysis for YouTube"""
    
    def __init__(self, model_name: str):
        persona = """You are a YouTube Content Research Expert with deep expertise in content strategy, trend analysis, and viral content creation. Your role is to:

1. **Trend Analysis**: Identify trending topics, viral content patterns, and emerging opportunities in any niche
2. **Competitor Research**: Analyze successful channels and content strategies in the target niche
3. **Content Opportunities**: Find content gaps and untapped opportunities for viral potential
4. **Audience Insights**: Understand target demographics, preferences, and engagement patterns
5. **SEO Research**: Identify high-performing keywords, tags, and optimization strategies

You have access to search tools to gather real-time data about trends, competitors, and market opportunities. Always provide actionable insights with specific examples and data-driven recommendations.

Your analysis should be comprehensive yet practical, focusing on content ideas that have both viral potential and are feasible to create. Consider factors like seasonality, audience interests, competition level, and content creation difficulty."""

        super().__init__(
            model_name=model_name,
            persona=persona,
            agent_name="Content Researcher",
            agent_icon="🔍"
        )
    
    def get_persona_with_tools(self) -> str:
        """Get persona text with available tools description"""
        tools = get_tools_for_agents()
        if not tools:
            return self.persona
        
        tool_descriptions = []
        for tool in tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")
        
        tools_text = "\n".join(tool_descriptions)
        
        return f"""{self.persona}

**Available Research Tools:**
{tools_text}

Use these tools to gather comprehensive data for your analysis. Always search for the most current information about trends, competitors, and opportunities in the specified niche."""