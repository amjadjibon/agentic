import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from .tools_registry import get_tools_for_agents


def initialize_models(with_tools: bool = False):
    """Initialize OpenAI and Google Gemini models"""
    tools = get_tools_for_agents() if with_tools else None
    
    openai_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True,
    )
    
    if with_tools and tools:
        openai_model = openai_model.bind_tools(tools)

    gemini_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        streaming=True,
    )
    
    if with_tools and tools:
        gemini_model = gemini_model.bind_tools(tools)

    return openai_model, gemini_model


def initialize_non_streaming_models(with_tools: bool = False):
    """Initialize OpenAI and Google Gemini models without streaming"""
    tools = get_tools_for_agents() if with_tools else None
    
    openai_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=False,
    )
    
    if with_tools and tools:
        openai_model = openai_model.bind_tools(tools)

    gemini_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        streaming=False,
    )
    
    if with_tools and tools:
        gemini_model = gemini_model.bind_tools(tools)

    return openai_model, gemini_model
