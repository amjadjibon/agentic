import os

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from debateai.tools import get_tools_for_agents
from debateai.config import get_model_config


def create_model_instance(model_name: str, with_tools: bool = False):
    """Create a model instance from configuration"""
    config = get_model_config(model_name)
    if not config:
        raise ValueError(f"Unknown model: {model_name}")
    
    # Check API key availability
    if config.api_key_env and not os.getenv(config.api_key_env):
        raise ValueError(f"Missing API key for {model_name}: {config.api_key_env}")
    
    tools = get_tools_for_agents() if with_tools else None
    
    if config.provider == "openai":
        model = ChatOpenAI(
            model=config.model_id,
            temperature=config.temperature,
            api_key=os.getenv(config.api_key_env) if config.api_key_env else None,
            streaming=True,
        )
    elif config.provider == "gemini":
        model = ChatGoogleGenerativeAI(
            model=config.model_id,
            temperature=config.temperature,
            google_api_key=os.getenv(config.api_key_env) if config.api_key_env else None,
            streaming=True,
        )
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")
    
    if with_tools and tools and config.supports_tools:
        model = model.bind_tools(tools)
    
    return model


def initialize_models(with_tools: bool = False):
    """Initialize default OpenAI and Google Gemini models (legacy compatibility)"""
    openai_model = create_model_instance("openai-gpt4o-mini", with_tools)
    gemini_model = create_model_instance("gemini-flash", with_tools)
    return openai_model, gemini_model
