from dataclasses import dataclass
from typing import Dict, List, Optional
import os


@dataclass
class ModelConfig:
    """Configuration for a language model"""
    name: str
    display_name: str
    provider: str
    model_id: str
    temperature: float = 0.7
    api_key_env: str = None
    supports_tools: bool = True


# Available models configuration
AVAILABLE_MODELS: Dict[str, ModelConfig] = {
    "openai-gpt4o": ModelConfig(
        name="openai-gpt4o",
        display_name="OpenAI GPT-4o",
        provider="openai",
        model_id="gpt-4o",
        api_key_env="OPENAI_API_KEY"
    ),
    "openai-gpt4o-mini": ModelConfig(
        name="openai-gpt4o-mini",
        display_name="OpenAI GPT-4o Mini",
        provider="openai",
        model_id="gpt-4o-mini",
        api_key_env="OPENAI_API_KEY"
    ),
    "gemini-pro": ModelConfig(
        name="gemini-pro",
        display_name="Google Gemini 1.5 Pro",
        provider="gemini",
        model_id="gemini-1.5-pro",
        api_key_env="GOOGLE_API_KEY"
    ),
    "gemini-flash": ModelConfig(
        name="gemini-flash",
        display_name="Google Gemini 1.5 Flash",
        provider="gemini", 
        model_id="gemini-1.5-flash",
        api_key_env="GOOGLE_API_KEY"
    )
}


def get_available_models() -> Dict[str, ModelConfig]:
    """Get list of available models"""
    return AVAILABLE_MODELS.copy()


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """Get configuration for a specific model"""
    return AVAILABLE_MODELS.get(model_name)


def get_models_by_provider(provider: str) -> Dict[str, ModelConfig]:
    """Get models filtered by provider"""
    return {name: config for name, config in AVAILABLE_MODELS.items() 
            if config.provider == provider}


def validate_model_availability() -> Dict[str, bool]:
    """Check which models are available based on API keys"""
    availability = {}
    
    for name, config in AVAILABLE_MODELS.items():
        if config.api_key_env:
            availability[name] = bool(os.getenv(config.api_key_env))
        else:
            availability[name] = True
    
    return availability


def get_available_models_list() -> List[Dict[str, str]]:
    """Get a formatted list of available models for UI display"""
    models = []
    availability = validate_model_availability()
    
    for name, config in AVAILABLE_MODELS.items():
        models.append({
            "name": name,
            "display_name": config.display_name,
            "provider": config.provider,
            "available": availability[name],
            "status": "✅ Available" if availability[name] else "❌ API Key Missing"
        })
    
    return models
