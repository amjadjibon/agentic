from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class YouTubeAutomationState(TypedDict):
    """State for YouTube content automation workflow"""
    
    # Input parameters
    channel_url: str
    niche: str
    target_audience: str
    content_goals: List[str]
    competitor_urls: Optional[List[str]]
    
    # Workflow state
    messages: List[BaseMessage]
    current_agent: str
    step_count: int
    max_steps: int
    
    # Research results
    competitor_analysis: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    content_opportunities: List[Dict[str, Any]]
    
    # Content creation results
    content_ideas: List[Dict[str, Any]]
    video_scripts: List[Dict[str, Any]]
    thumbnail_concepts: List[Dict[str, Any]]
    
    # Optimization results
    seo_recommendations: Dict[str, Any]
    posting_schedule: Dict[str, Any]
    analytics_insights: Dict[str, Any]
    
    # Final outputs
    content_calendar: Dict[str, Any]
    final_recommendations: Dict[str, Any]
    
    # Workflow metadata
    tools_enabled: bool
    selected_models: Dict[str, str]  # agent_name -> model_name
    workflow_status: str  # "running", "completed", "error"
    error_messages: List[str]
