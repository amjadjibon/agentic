import asyncio
from typing import Iterator, Dict, Any, Optional, TYPE_CHECKING
from langchain_core.messages import HumanMessage, AIMessage

from ..agents.youtube import (
    ContentResearcherAgent,
    ScriptWriterAgent, 
    ThumbnailCreatorAgent,
    AnalyticsProcessorAgent,
    CompetitorAnalystAgent
)
from ..states.youtube_state import YouTubeAutomationState

if TYPE_CHECKING:
    from ..tui.rich_ui import DebateUI


def run_youtube_automation(
    channel_url: str,
    niche: str,
    target_audience: str,
    content_goals: list,
    competitor_urls: list,
    selected_agents: Dict[str, bool],
    models: Dict[str, str],
    tools_enabled: bool = True,
    max_steps: int = 8,
    ui: Optional['DebateUI'] = None
) -> Iterator[YouTubeAutomationState]:
    """
    Run YouTube content automation workflow with streaming agents
    
    Args:
        channel_url: URL of the YouTube channel to analyze
        niche: Content niche/topic area
        target_audience: Target audience description
        content_goals: List of content goals (e.g., "increase subscribers", "viral content")
        selected_agents: Dictionary indicating which agents to use
        models: Dictionary mapping agent names to model names
        tools_enabled: Whether to enable web search tools
        max_steps: Maximum number of workflow steps
        ui: Optional UI for rich display
    """
    
    # Initialize only selected agents
    agents = {}
    if selected_agents.get("competitor_analyst", False):
        agents["competitor_analyst"] = CompetitorAnalystAgent(models.get("competitor_analyst", "gpt-4o"))
    if selected_agents.get("researcher", False):
        agents["researcher"] = ContentResearcherAgent(models.get("researcher", "gpt-4o"))
    if selected_agents.get("writer", False):
        agents["writer"] = ScriptWriterAgent(models.get("writer", "gpt-4o"))
    if selected_agents.get("designer", False):
        agents["designer"] = ThumbnailCreatorAgent(models.get("designer", "gpt-4o"))
    if selected_agents.get("analyst", False):
        agents["analyst"] = AnalyticsProcessorAgent(models.get("analyst", "gpt-4o"))
    
    # Initialize state
    initial_state: YouTubeAutomationState = {
        "channel_url": channel_url,
        "niche": niche,
        "target_audience": target_audience,
        "content_goals": content_goals,
        "competitor_urls": competitor_urls,
        "messages": [],
        "current_agent": "researcher",
        "step_count": 0,
        "max_steps": max_steps,
        "competitor_analysis": {},
        "trend_analysis": {},
        "content_opportunities": [],
        "content_ideas": [],
        "video_scripts": [],
        "thumbnail_concepts": [],
        "seo_recommendations": {},
        "posting_schedule": {},
        "analytics_insights": {},
        "content_calendar": {},
        "final_recommendations": {},
        "tools_enabled": tools_enabled,
        "selected_models": models,
        "workflow_status": "running",
        "error_messages": []
    }
    
    if ui:
        ui.console.print(f"\n🎬 [bold blue]Starting YouTube Automation Workflow[/bold blue]")
        ui.console.print(f"📺 Channel: {channel_url}")
        ui.console.print(f"🎯 Niche: {niche}")
        ui.console.print(f"👥 Target Audience: {target_audience}")
        ui.console.print(f"🎯 Goals: {', '.join(content_goals)}")
        ui.console.print(f"🛠️  Tools Enabled: {'✅' if tools_enabled else '❌'}")
        ui.console.print("-" * 60)
    else:
        print(f"\n🎬 Starting YouTube Automation Workflow")
        print(f"📺 Channel: {channel_url}")
        print(f"🎯 Niche: {niche}")
        print(f"👥 Target Audience: {target_audience}")
        print(f"🎯 Goals: {', '.join(content_goals)}")
        print(f"🛠️  Tools: {'Enabled' if tools_enabled else 'Disabled'}")
        print("-" * 50)
    
    current_state = initial_state.copy()
    
    # Build dynamic workflow based on selected agents
    workflow_steps = []
    
    # Phase 1: Competitor analysis (if selected)
    if "competitor_analyst" in agents:
        workflow_steps.append(("competitor_analyst", _competitor_analysis_phase))
    
    # Phase 2: Content research (if selected)  
    if "researcher" in agents:
        workflow_steps.append(("researcher", _research_phase))
    
    # Phase 3: Market analysis (if analyst available)
    if "analyst" in agents:
        workflow_steps.append(("analyst", _analysis_phase))
    
    # Phase 4: Content creation (if writer available)
    if "writer" in agents:
        workflow_steps.append(("writer", _content_creation_phase))
    
    # Phase 5: Thumbnail design (if designer available)
    if "designer" in agents:
        workflow_steps.append(("designer", _thumbnail_phase))
    
    # Phase 6: Optimization (if researcher available)
    if "researcher" in agents:
        workflow_steps.append(("researcher", _optimization_phase))
    
    # Phase 7: Calendar planning (if analyst available)
    if "analyst" in agents:
        workflow_steps.append(("analyst", _calendar_phase))
    
    # Phase 8: Final recommendations (use any available agent)
    if agents:
        final_agent = list(agents.keys())[0]  # Use first available agent
        workflow_steps.append((final_agent, _final_recommendations_phase))
    
    try:
        for step_idx, (agent_name, phase_func) in enumerate(workflow_steps):
            if current_state["step_count"] >= max_steps:
                break
                
            current_state["current_agent"] = agent_name
            current_state["step_count"] = step_idx + 1
            
            # Run the phase
            agent = agents[agent_name]
            phase_state = phase_func(current_state, agent, tools_enabled, ui)
            
            # Stream the agent response
            for updated_state in agent.stream_response(phase_state, tools_enabled, ui):
                current_state.update(updated_state)
                yield current_state
        
        current_state["workflow_status"] = "completed"
        
    except Exception as e:
        current_state["workflow_status"] = "error"
        current_state["error_messages"].append(str(e))
        if ui:
            ui.console.print(f"\n[red]❌ Workflow error: {str(e)}[/red]")
        else:
            print(f"\n❌ Workflow error: {str(e)}")
    
    # Final summary
    if ui:
        ui.console.print(f"\n✅ [bold green]YouTube Automation Workflow Complete[/bold green]")
        ui.console.print(f"📊 Steps Completed: {current_state['step_count']}")
        ui.console.print(f"📝 Content Ideas Generated: {len(current_state.get('content_ideas', []))}")
        ui.console.print(f"🎬 Scripts Created: {len(current_state.get('video_scripts', []))}")
        ui.console.print(f"🎨 Thumbnail Concepts: {len(current_state.get('thumbnail_concepts', []))}")
    else:
        print(f"\n✅ YouTube Automation Workflow Complete")
        print(f"📊 Steps: {current_state['step_count']}")
        print(f"📝 Content Ideas: {len(current_state.get('content_ideas', []))}")
        print(f"🎬 Scripts: {len(current_state.get('video_scripts', []))}")
        print(f"🎨 Thumbnails: {len(current_state.get('thumbnail_concepts', []))}")
    
    yield current_state


def _competitor_analysis_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 0: Comprehensive competitor analysis"""
    
    # Check if competitor URLs were provided in the configuration
    provided_competitors = []
    if hasattr(state, 'competitor_urls') and state.get('competitor_urls'):
        provided_competitors = state['competitor_urls']
    
    if provided_competitors:
        competitor_prompt = f"""
        Conduct comprehensive competitor analysis for the {state['niche']} YouTube niche using the provided competitor channels.

        **Your Mission:**
        1. **Analyze Provided Competitors**: Use competitor analytics tools to analyze the specific channels provided by the user
        2. **Extract Performance Data**: Get detailed metrics for subscriber counts, views, engagement rates
        3. **Content Strategy Analysis**: Identify successful content formats, topics, and posting patterns
        4. **Competitive Intelligence**: Extract optimization tactics and growth strategies
        5. **Generate Strategic Insights**: Provide actionable recommendations for competitive advantage

        **Target Analysis:**
        - **Your Channel**: {state['channel_url']}
        - **Niche**: {state['niche']}  
        - **Audience**: {state['target_audience']}
        - **Goals**: {', '.join(state['content_goals'])}

        **Provided Competitor Channels to Analyze:**
        {chr(10).join([f"- {url}" for url in provided_competitors])}

        **Analysis Process:**
        1. Use the crawl4ai_competitor_analysis tool with these specific URLs: {provided_competitors}
        2. Analyze each channel's performance metrics, content themes, and success patterns
        3. Compare their strategies against your channel's goals and niche
        4. Identify content gaps and positioning opportunities
        5. Extract actionable insights for competitive advantage

        **Required Deliverables:**
        - Performance benchmarking for each provided competitor
        - Content strategy analysis and successful formats identification
        - SEO and optimization insights from competitors
        - Content gap opportunities and differentiation strategies
        - Specific tactical recommendations for outperforming competitors

        **IMPORTANT**: Use the crawl4ai_competitor_analysis tool with the provided URLs to get detailed analysis data.
        """
    else:
        competitor_prompt = f"""
        Conduct comprehensive competitor analysis for the {state['niche']} YouTube niche.

        **Your Mission:**
        1. **Discover Competitors**: Use search tools to find 3-5 top YouTube channels in the {state['niche']} space
        2. **Analyze Performance**: Use competitor analytics tools to extract detailed performance data
        3. **Extract Intelligence**: Identify successful content strategies, posting patterns, and optimization tactics
        4. **Find Opportunities**: Discover content gaps and underserved market segments
        5. **Generate Insights**: Provide actionable competitive intelligence for strategic advantage

        **Target Analysis:**
        - **Channel**: {state['channel_url']}
        - **Niche**: {state['niche']}  
        - **Audience**: {state['target_audience']}
        - **Goals**: {', '.join(state['content_goals'])}

        **Research Process:**
        1. Search for top YouTube channels in {state['niche']} using terms like "{state['niche']} YouTube channel", "best {state['niche']} creators", etc.
        2. Collect 3-5 competitor channel URLs from search results
        3. Use competitor analytics tools to analyze each channel's performance metrics
        4. Compare and contrast their strategies, content themes, and success factors
        5. Identify opportunities for differentiation and competitive advantage

        **Deliver:**
        - Competitor performance benchmarks (subscribers, views, engagement)
        - Successful content formats and topics analysis
        - Optimal posting strategies and timing insights  
        - Content gap opportunities
        - Strategic recommendations for competitive positioning

        Focus on actionable intelligence that directly informs content strategy and competitive positioning.
        """
    
    messages = [HumanMessage(content=competitor_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "competitor_analyst", 
        "conversation_count": 0,
        "max_turns": 1
    }


def _research_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 1: Research competitors, trends, and opportunities"""
    research_prompt = f"""
    Conduct comprehensive research for YouTube content creation in the {state['niche']} niche.

    **Channel to Analyze:** {state['channel_url']}
    **Target Audience:** {state['target_audience']}
    **Content Goals:** {', '.join(state['content_goals'])}

    **Research Tasks:**
    1. Analyze competitor channels in the {state['niche']} space
    2. Identify trending topics and viral content patterns  
    3. Find content gaps and opportunities
    4. Research audience preferences and engagement patterns
    5. Identify optimal keywords and SEO opportunities

    Provide detailed insights with specific examples and actionable recommendations.
    """
    
    messages = [HumanMessage(content=research_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "researcher", 
        "conversation_count": 0,
        "max_turns": 1
    }


def _analysis_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 2: Analyze research data and identify best opportunities"""
    analysis_prompt = f"""
    Based on the research conducted, analyze the data and identify the best content opportunities.

    **Analysis Focus:**
    1. Rank content opportunities by viral potential vs. competition level
    2. Identify the most promising content formats and styles
    3. Analyze optimal video lengths and posting strategies
    4. Evaluate seasonal trends and timing opportunities
    5. Assess resource requirements vs. expected ROI

    **Target Metrics:**
    - Click-through rate optimization
    - Watch time maximization  
    - Subscriber conversion potential
    - Engagement rate improvement

    Provide prioritized recommendations with specific rationale for each.
    """
    
    # Add previous messages to maintain context
    messages = state["messages"] + [HumanMessage(content=analysis_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "analyst",
        "conversation_count": len(state["messages"]) // 2,
        "max_turns": 1
    }


def _content_creation_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 3: Create content ideas and video scripts"""
    content_prompt = f"""
    Create detailed content ideas and video scripts based on the analysis.

    **Content Brief:**
    - Niche: {state['niche']}
    - Audience: {state['target_audience']}
    - Goals: {', '.join(state['content_goals'])}

    **Deliverables:**
    1. **5 High-Priority Content Ideas** with:
       - Compelling titles (SEO optimized)
       - Video descriptions
       - Target keywords
       - Expected performance metrics
       - Unique angles/hooks

    2. **3 Complete Video Scripts** for top ideas including:
       - Hook (first 15 seconds)
       - Structured content flow
       - Engagement elements
       - Call-to-action placements
       - Estimated runtime

    Focus on content that balances viral potential with creation feasibility.
    """
    
    messages = state["messages"] + [HumanMessage(content=content_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "writer",
        "conversation_count": len(state["messages"]) // 2,
        "max_turns": 1
    }


def _thumbnail_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 4: Create thumbnail concepts"""
    thumbnail_prompt = f"""
    Create compelling thumbnail concepts for the video content ideas.

    **Design Requirements:**
    - Niche: {state['niche']}
    - Target audience: {state['target_audience']}
    - Platform: YouTube (1280x720 pixels)

    **Deliverables:**
    For each of the main content ideas, create:

    1. **Primary Thumbnail Design** with detailed description including:
       - Visual composition and layout
       - Color scheme and contrast
       - Text overlay content and positioning
       - Facial expressions/emotions (if applicable)
       - Background elements and effects
       - Brand consistency elements

    2. **A/B Test Variant** with alternative approach

    3. **AI Image Generator Prompt** ready for DALL-E/Midjourney

    Focus on high click-through rate potential while maintaining authenticity.
    """
    
    messages = state["messages"] + [HumanMessage(content=thumbnail_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "designer",
        "conversation_count": len(state["messages"]) // 2,
        "max_turns": 1
    }


def _optimization_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 5: SEO and optimization recommendations"""
    optimization_prompt = f"""
    Provide comprehensive SEO and optimization strategies for the content.

    **Optimization Areas:**
    1. **YouTube SEO:**
       - Title optimization formulas
       - Description templates
       - Tag strategies  
       - End screen optimization

    2. **Algorithm Optimization:**
       - Upload timing strategies
       - Engagement acceleration tactics
       - Community tab utilization
       - Cross-platform promotion

    3. **Performance Tracking:**
       - Key metrics to monitor
       - A/B testing strategies
       - Optimization iteration plans

    4. **Growth Tactics:**
       - Collaboration opportunities
       - Community building strategies
       - Subscriber conversion optimization

    Provide specific, actionable recommendations with implementation timelines.
    """
    
    messages = state["messages"] + [HumanMessage(content=optimization_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "researcher",
        "conversation_count": len(state["messages"]) // 2,
        "max_turns": 1
    }


def _calendar_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 6: Create content calendar and posting schedule"""
    calendar_prompt = f"""
    Create a strategic content calendar and posting schedule.

    **Calendar Requirements:**
    - Time period: Next 30-60 days
    - Content goals: {', '.join(state['content_goals'])}
    - Target audience: {state['target_audience']}

    **Deliverables:**
    1. **30-Day Content Calendar** including:
       - Specific video topics and titles
       - Optimal posting dates and times
       - Content type variety (tutorials, reviews, etc.)
       - Seasonal/trending topic alignment
       - Cross-promotion opportunities

    2. **Production Schedule** with:
       - Content creation timelines
       - Resource allocation
       - Buffer time for optimization
       - Batch production opportunities

    3. **Performance Milestones:**
       - Weekly/monthly targets
       - Key performance indicators
       - Success metrics and benchmarks

    Consider audience activity patterns, competition analysis, and seasonal trends.
    """
    
    messages = state["messages"] + [HumanMessage(content=calendar_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "analyst",
        "conversation_count": len(state["messages"]) // 2,
        "max_turns": 1
    }


def _final_recommendations_phase(state: YouTubeAutomationState, agent, tools_enabled: bool, ui) -> Dict[str, Any]:
    """Phase 7: Final strategic recommendations and action plan"""
    final_prompt = f"""
    Synthesize all research and analysis into final strategic recommendations.

    **Executive Summary:**
    Create a comprehensive action plan including:

    1. **Immediate Actions (Next 7 Days):**
       - Priority content to create
       - Quick optimization wins
       - Tools/resources to acquire

    2. **Short-term Strategy (Next 30 Days):**
       - Content production pipeline
       - Channel optimization tasks
       - Community engagement plan

    3. **Long-term Growth Plan (3-6 Months):**
       - Scaling strategies
       - Advanced optimization techniques
       - Collaboration and expansion opportunities

    4. **Success Metrics and KPIs:**
       - Specific targets for growth
       - Performance tracking methods
       - Optimization iteration schedule

    5. **Risk Mitigation:**
       - Common pitfalls to avoid
       - Backup content strategies
       - Algorithm change adaptations

    Provide a clear, actionable roadmap for YouTube success in the {state['niche']} niche.
    """
    
    messages = state["messages"] + [HumanMessage(content=final_prompt)]
    
    return {
        "messages": messages,
        "current_speaker": "researcher",
        "conversation_count": len(state["messages"]) // 2,
        "max_turns": 1
    }