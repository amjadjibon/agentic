from typing import Dict, List, Optional
from agentic.llm.models import (
    get_available_models,
    get_models_list,
    check_api_key_available,
    LLMModel
)


def get_model_config(model_name: str) -> Optional[LLMModel]:
    """Get configuration for a specific model"""
    # Try direct lookup by model name
    models = get_available_models()
    for model in models:
        if model.model_name == model_name:
            return model
    
    # Try by display name
    for model in models:
        if model.display_name == model_name:
            return model
    
    return None


def get_models_by_provider(provider: str) -> List[LLMModel]:
    """Get models filtered by provider"""
    models = get_available_models()
    return [model for model in models if model.provider.value == provider]


def validate_model_availability() -> Dict[str, bool]:
    """Check which models are available based on API keys"""
    availability = {}
    models = get_available_models()
    
    for model in models:
        key = f"{model.provider.value}-{model.model_name}"
        availability[key] = check_api_key_available(model.provider)
        
        # Also add model name as key
        availability[model.model_name] = check_api_key_available(model.provider)
    
    return availability


def get_available_models_list() -> List[Dict[str, str]]:
    """Get a formatted list of available models for UI display"""
    models_data = get_models_list()
    availability = validate_model_availability()
    
    result = []
    for model_data in models_data:
        available = availability.get(model_data["model_name"], False)
        
        result.append({
            "name": model_data["model_name"],
            "display_name": model_data["display_name"],
            "provider": model_data["provider"],
            "available": available,
            "status": "✅ Available" if available else "❌ API Key Missing"
        })
    
    return result
