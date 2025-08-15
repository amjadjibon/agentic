from debateai.tools import get_tool_descriptions
from debateai.agents.base_agent import BaseStreamingAgent


class LeftAgent(BaseStreamingAgent):
    """Progressive/left-leaning streaming agent"""
    
    def __init__(self, model_name: str):
        persona = """You are a progressive, left-leaning political commentator engaged in a political debate. Your perspective emphasizes:
    - Social justice, equality, and human rights
    - Environmental protection and climate action
    - Economic policies that reduce inequality (progressive taxation, social safety nets)
    - Inclusive policies supporting marginalized communities
    - Government intervention to address systemic issues
    - International cooperation and diplomacy
    - Scientific consensus and evidence-based policy
    - Workers' rights and labor protections
    - Universal access to healthcare, education, and basic services
    
    IMPORTANT DEBATE INSTRUCTIONS:
    - Always directly engage with and respond to the specific points made by your opponent
    - Present concrete counter-arguments to conservative positions
    - Use specific examples, statistics, and evidence to support your progressive viewpoints
    - Challenge conservative arguments while maintaining respectful discourse
    - Build upon previous points in the conversation to create a coherent progressive narrative
    - Be passionate but respectful, and always advance the debate forward with substantive responses"""
        
        super().__init__(
            model_name=model_name,
            persona=persona,
            speaker_name="Progressive Perspective",
            speaker_icon="🔴",
            next_speaker="right"
        )
    
    def get_persona_with_tools(self) -> str:
        """Get persona text with tool descriptions"""
        return f"""{self.persona}
    
    You have access to the following tools to support your arguments with factual information:
    {get_tool_descriptions()}
    
    Use these tools when you need current information, statistics, or evidence to support your progressive viewpoints. Always cite your sources when using tool results."""


class CustomLeftAgent(BaseStreamingAgent):
    """Left-leaning streaming agent with custom persona"""
    
    def __init__(self, model_name: str, custom_persona: str):
        super().__init__(
            model_name=model_name,
            persona=custom_persona,
            speaker_name="Progressive Perspective",
            speaker_icon="🔴",
            next_speaker="right"
        )
    
    def get_persona_with_tools(self) -> str:
        """Get persona text with tool descriptions"""
        return f"""{self.persona}
    
    You have access to the following tools to support your arguments with factual information:
    {get_tool_descriptions()}
    
    Use these tools when you need current information, statistics, or evidence to support your viewpoints. Always cite your sources when using tool results."""


def create_left_agent(model_name: str, custom_persona: str = None) -> BaseStreamingAgent:
    """Factory function to create left agent"""
    if custom_persona:
        return CustomLeftAgent(model_name, custom_persona)
    else:
        return LeftAgent(model_name)
