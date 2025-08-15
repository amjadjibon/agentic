import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def initialize_models():
    """Initialize OpenAI and Google Gemini models"""
    openai_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True,
    )

    gemini_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        streaming=True,
    )

    return openai_model, gemini_model


def initialize_non_streaming_models():
    """Initialize OpenAI and Google Gemini models without streaming"""
    openai_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=False,
    )

    gemini_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        streaming=False,
    )

    return openai_model, gemini_model
