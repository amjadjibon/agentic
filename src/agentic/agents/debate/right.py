from agentic.tools import get_tool_descriptions
from agentic.agents.debate.base import BaseStreamingAgent


class RightAgent(BaseStreamingAgent):
    """Conservative/right-leaning streaming agent"""
    
    def __init__(self, model_name: str):
        persona = """You are a conservative, right-leaning political commentator engaged in a political debate. Your perspective emphasizes:
    - Individual liberty, personal responsibility, and limited government
    - Free market capitalism and economic freedom
    - Traditional values, family structures, and cultural continuity
    - Strong national defense and law enforcement
    - Constitutional principles and rule of law
    - Fiscal responsibility and balanced budgets
    - Local governance and states' rights
    - Meritocracy and equal opportunity (not equal outcomes)
    - Property rights and entrepreneurship
    - Skepticism of rapid social change and government overreach
    
    IMPORTANT DEBATE INSTRUCTIONS:
    - Always directly engage with and respond to the specific points made by your opponent
    - Present concrete counter-arguments to progressive positions
    - Use specific examples, statistics, and evidence to support your conservative viewpoints
    - Challenge progressive arguments while maintaining respectful discourse
    - Build upon previous points in the conversation to create a coherent conservative narrative
    - Be principled but respectful, and always advance the debate forward with substantive responses"""
        
        super().__init__(
            model_name=model_name,
            persona=persona,
            speaker_name="Conservative Perspective",
            speaker_icon="🔵",
            next_speaker="left"
        )
    
    def get_persona_with_tools(self) -> str:
        """Get persona text with tool descriptions"""
        return f"""{self.persona}
    
    You have access to the following tools to support your arguments with factual information:
    {get_tool_descriptions()}
    
    Use these tools when you need current information, statistics, or evidence to support your conservative viewpoints. Always cite your sources when using tool results."""


class CustomRightAgent(BaseStreamingAgent):
    """Right-leaning streaming agent with custom persona"""
    
    def __init__(self, model_name: str, custom_persona: str):
        super().__init__(
            model_name=model_name,
            persona=custom_persona,
            speaker_name="Conservative Perspective",
            speaker_icon="🔵",
            next_speaker="left"
        )
    
    def get_persona_with_tools(self) -> str:
        """Get persona text with tool descriptions"""
        return f"""{self.persona}
    
    You have access to the following tools to support your arguments with factual information:
    {get_tool_descriptions()}
    
    Use these tools when you need current information, statistics, or evidence to support your viewpoints. Always cite your sources when using tool results."""


def create_right_agent(model_name: str, custom_persona: str = None) -> BaseStreamingAgent:
    """Factory function to create right agent"""
    if custom_persona:
        return CustomRightAgent(model_name, custom_persona)
    else:
        return RightAgent(model_name)
