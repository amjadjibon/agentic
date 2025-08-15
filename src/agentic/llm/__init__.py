from agentic.tools import get_tools_for_agents
from agentic.llm.models import get_model
from agentic.llm.config import get_model_config


def create_model_instance(model_name: str, with_tools: bool = False):
    """Create a model instance from configuration"""
    config = get_model_config(model_name)
    if not config:
        raise ValueError(f"Unknown model: {model_name}")
    
    tools = get_tools_for_agents() if with_tools else None
    
    # Use the new LLM models system
    model = get_model(config.model_name, config.provider)
    
    # Bind tools if requested
    if tools:
        model = model.bind_tools(tools)
    
    return model
