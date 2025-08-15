import os
from enum import Enum
from typing import List, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_gigachat import GigaChat
from langchain_ollama import ChatOllama
from pydantic import BaseModel


class ModelProvider(str, Enum):
    """Enum for supported LLM providers"""

    ALIBABA = "alibaba"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GOOGLE = "google"
    GROQ = "groq"
    META = "meta"
    MISTRAL = "mistral"
    OPENAI = "openai"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    GIGACHAT = "gigachat"


class LLMModel(BaseModel):
    """Represents an LLM model configuration"""

    display_name: str
    model_name: str
    provider: ModelProvider

    def to_choice_tuple(self) -> Tuple[str, str, str]:
        """Convert to format needed for questionary choices"""
        return (self.display_name, self.model_name, self.provider.value)

    def is_custom(self) -> bool:
        """Check if the model is a custom model"""
        return self.model_name == "-"

    def has_json_mode(self) -> bool:
        """Check if the model supports JSON mode"""
        if self.is_deepseek() or self.is_gemini():
            return False
        # Only certain Ollama models support JSON mode
        if self.is_ollama():
            return "llama3" in self.model_name or "neural-chat" in self.model_name
        # OpenRouter models generally support JSON mode
        if self.provider == ModelProvider.OPENROUTER:
            return True
        return True

    def is_deepseek(self) -> bool:
        """Check if the model is a DeepSeek model"""
        return self.model_name.startswith("deepseek")

    def is_gemini(self) -> bool:
        """Check if the model is a Gemini model"""
        return self.model_name.startswith("gemini")

    def is_ollama(self) -> bool:
        """Check if the model is an Ollama model"""
        return self.provider == ModelProvider.OLLAMA


AVAILABLE_MODELS_DATA = [
    {
        "display_name": "GPT-5",
        "model_name": "gpt-5",
        "provider": "openai"
    },
    {
        "display_name": "GPT-5 mini",
        "model_name": "gpt-5-mini",
        "provider": "openai"
    },
    {
        "display_name": "GPT-5 nano",
        "model_name": "gpt-5-nano",
        "provider": "openai"
    },
    {
        "display_name": "GPT-4o",
        "model_name": "gpt-4o",
        "provider": "openai"
    },
    {
        "display_name": "GPT-4.5",
        "model_name": "gpt-4.5-preview",
        "provider": "openai"
    },
    {
        "display_name": "o3",
        "model_name": "o3",
        "provider": "openai"
    },
    {
        "display_name": "o4 Mini",
        "model_name": "gpt-4o-mini",
        "provider": "openai"
    },
    {
        "display_name": "Claude Haiku 3.5",
        "model_name": "claude-3-5-haiku-latest",
        "provider": "anthropic"
    },
    {
        "display_name": "Claude Sonnet 4",
        "model_name": "claude-sonnet-4-20250514",
        "provider": "anthropic"
    },
    {
        "display_name": "Claude Opus 4.1",
        "model_name": "claude-opus-4-1-20250805",
        "provider": "anthropic"
    },
    {
        "display_name": "DeepSeek R1",
        "model_name": "deepseek-reasoner",
        "provider": "deepseek"
    },
    {
        "display_name": "DeepSeek V3",
        "model_name": "deepseek-chat",
        "provider": "deepseek"
    },
    {
        "display_name": "Gemini 2.5 Flash",
        "model_name": "gemini-2.5-flash-preview-05-20",
        "provider": "google"
    },
    {
        "display_name": "Gemini 2.5 Pro",
        "model_name": "gemini-2.5-pro-preview-06-05",
        "provider": "google"
    },
    {
        "display_name": "Llama 4 Scout (17b)",
        "model_name": "meta-llama/llama-4-scout-17b-16e-instruct",
        "provider": "groq"
    },
    {
        "display_name": "Llama 4 Maverick (17b)",
        "model_name": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "provider": "groq"
    },
    {
        "display_name": "GLM-4.5 Air",
        "model_name": "z-ai/glm-4.5-air",
        "provider": "openrouter"
    },
    {
        "display_name": "GLM-4.5",
        "model_name": "z-ai/glm-4.5",
        "provider": "openrouter"
    },
    {
        "display_name": "Qwen 3 (235B) Thinking",
        "model_name": "qwen/qwen3-235b-a22b-thinking-2507",
        "provider": "openrouter"
    },
    {
        "display_name": "GigaChat-2-Max",
        "model_name": "GigaChat-2-Max",
        "provider": "gigachat"
    }
]

OLLAMA_MODELS_DATA = [
  {
    "display_name": "gpt-oss (20B)",
    "model_name": "gpt-oss:20b",
    "provider": "openai"
  },
  {
    "display_name": "gpt-oss (120B)",
    "model_name": "gpt-oss:120b",
    "provider": "openai"
  },
  {
    "display_name": "Gemma 3 (4B)",
    "model_name": "gemma3:4b",
    "provider": "google"
  },
  {
    "display_name": "Qwen 3 (4B)",
    "model_name": "qwen3:4b",
    "provider": "alibaba"
  },
  {
    "display_name": "Qwen 3 (8B)",
    "model_name": "qwen3:8b",
    "provider": "alibaba"
  },
  {
    "display_name": "Llama 3.1 (8B)",
    "model_name": "llama3.1:latest",
    "provider": "meta"
  },
  {
    "display_name": "Gemma 3 (12B)",
    "model_name": "gemma3:12b",
    "provider": "google"
  },
  {
    "display_name": "Mistral Small 3.1 (24B)",
    "model_name": "mistral-small3.1",
    "provider": "mistral"
  },
  {
    "display_name": "Gemma 3 (27B)",
    "model_name": "gemma3:27b",
    "provider": "google"
  },
  {
    "display_name": "Qwen 3 (30B-a3B)",
    "model_name": "qwen3:30b-a3b",
    "provider": "alibaba"
  },
  {
    "display_name": "Llama 3.3 (70B)",
    "model_name": "llama3.3:70b-instruct-q4_0",
    "provider": "meta"
  }
]

def create_models_from_data(models_data: List[dict]) -> List[LLMModel]:
    """Create LLMModel instances from model data"""
    models = []
    for model_data in models_data:
        provider_enum = ModelProvider(model_data["provider"])
        models.append(
            LLMModel(
                display_name=model_data["display_name"],
                model_name=model_data["model_name"],
                provider=provider_enum
            )
        )
    return models


# Create model instances
AVAILABLE_MODELS = create_models_from_data(AVAILABLE_MODELS_DATA)
OLLAMA_MODELS = create_models_from_data(OLLAMA_MODELS_DATA)

# Create LLM_ORDER in the format expected by the UI (dynamically based on available API keys)
def get_llm_order(api_keys: dict = None) -> List[Tuple[str, str, str]]:
    """Get LLM order based on available API keys"""
    available_models = get_available_models(api_keys)
    return [model.to_choice_tuple() for model in available_models]

# Create Ollama LLM_ORDER separately (dynamically based on availability)
def get_ollama_llm_order(api_keys: dict = None) -> List[Tuple[str, str, str]]:
    """Get Ollama LLM order based on available API keys"""
    available_ollama_models = [model for model in get_available_models(api_keys) if model.provider == ModelProvider.OLLAMA]
    return [model.to_choice_tuple() for model in available_ollama_models]

# Legacy support - static lists (use dynamic functions above for better results)
LLM_ORDER = [model.to_choice_tuple() for model in AVAILABLE_MODELS]
OLLAMA_LLM_ORDER = [model.to_choice_tuple() for model in OLLAMA_MODELS]


def get_model_info(model_name: str, model_provider: str) -> LLMModel | None:
    """Get model information by model_name"""
    all_models = AVAILABLE_MODELS + OLLAMA_MODELS
    return next((model for model in all_models if model.model_name == model_name and model.provider == model_provider), None)


def get_models_list(api_keys: dict = None):
    """Get the list of models for API responses based on available API keys."""
    available_models = get_available_models(api_keys)
    return [
        {
            "display_name": model.display_name,
            "model_name": model.model_name,
            "provider": model.provider.value
        }
        for model in available_models
    ]


def check_api_key_available(provider: ModelProvider, api_keys: dict = None) -> bool:
    """Check if API key is available for a given provider"""
    key_mapping = {
        ModelProvider.OPENAI: ["OPENAI_API_KEY"],
        ModelProvider.GROQ: ["GROQ_API_KEY"],
        ModelProvider.ANTHROPIC: ["ANTHROPIC_API_KEY"],
        ModelProvider.DEEPSEEK: ["DEEPSEEK_API_KEY"],
        ModelProvider.GOOGLE: ["GOOGLE_API_KEY"],
        ModelProvider.OPENROUTER: ["OPENROUTER_API_KEY"],
        ModelProvider.GIGACHAT: ["GIGACHAT_API_KEY", "GIGACHAT_CREDENTIALS", "GIGACHAT_USER"],
        ModelProvider.OLLAMA: []  # Ollama doesn't require API keys
    }
    
    required_keys = key_mapping.get(provider, [])
    
    # Ollama is always available (no API key required)
    if provider == ModelProvider.OLLAMA:
        return True
    
    # GigaChat has multiple auth methods
    if provider == ModelProvider.GIGACHAT:
        # Check if user/password auth is available
        if os.getenv("GIGACHAT_USER") and os.getenv("GIGACHAT_PASSWORD"):
            return True
        # Check if API key auth is available
        for key in required_keys:
            if (api_keys or {}).get(key) or os.getenv(key):
                return True
        return False
    
    # For other providers, check if any required key is available
    for key in required_keys:
        if (api_keys or {}).get(key) or os.getenv(key):
            return True
    
    return False


def get_available_models(api_keys: dict = None) -> List[LLMModel]:
    """Get list of models that can be initialized based on available API keys"""
    available_models = []
    all_models = AVAILABLE_MODELS + OLLAMA_MODELS
    
    for model in all_models:
        if check_api_key_available(model.provider, api_keys):
            available_models.append(model)
    
    return available_models


def get_available_providers(api_keys: dict = None) -> List[ModelProvider]:
    """Get list of providers that have API keys available"""
    available_providers = []
    
    for provider in ModelProvider:
        if check_api_key_available(provider, api_keys):
            available_providers.append(provider)
    
    return available_providers


def get_model(model_name: str, model_provider: ModelProvider, api_keys: dict = None) -> ChatOpenAI | ChatGroq | ChatOllama | GigaChat | None:
    if model_provider == ModelProvider.GROQ:
        api_key = (api_keys or {}).get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if not api_key:
            # Print error to console
            print(f"API Key Error: Please make sure GROQ_API_KEY is set in your .env file or provided via API keys.")
            raise ValueError("Groq API key not found.  Please make sure GROQ_API_KEY is set in your .env file or provided via API keys.")
        return ChatGroq(model=model_name, api_key=api_key)
    elif model_provider == ModelProvider.OPENAI:
        # Get and validate API key
        api_key = (api_keys or {}).get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        if not api_key:
            # Print error to console
            print(f"API Key Error: Please make sure OPENAI_API_KEY is set in your .env file or provided via API keys.")
            raise ValueError("OpenAI API key not found.  Please make sure OPENAI_API_KEY is set in your .env file or provided via API keys.")
        return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
    elif model_provider == ModelProvider.ANTHROPIC:
        api_key = (api_keys or {}).get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure ANTHROPIC_API_KEY is set in your .env file or provided via API keys.")
            raise ValueError("Anthropic API key not found.  Please make sure ANTHROPIC_API_KEY is set in your .env file or provided via API keys.")
        return ChatAnthropic(model=model_name, api_key=api_key)
    elif model_provider == ModelProvider.DEEPSEEK:
        api_key = (api_keys or {}).get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure DEEPSEEK_API_KEY is set in your .env file or provided via API keys.")
            raise ValueError("DeepSeek API key not found.  Please make sure DEEPSEEK_API_KEY is set in your .env file or provided via API keys.")
        return ChatDeepSeek(model=model_name, api_key=api_key)
    elif model_provider == ModelProvider.GOOGLE:
        api_key = (api_keys or {}).get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure GOOGLE_API_KEY is set in your .env file or provided via API keys.")
            raise ValueError("Google API key not found.  Please make sure GOOGLE_API_KEY is set in your .env file or provided via API keys.")
        return ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
    elif model_provider == ModelProvider.OLLAMA:
        # For Ollama, we use a base URL instead of an API key
        # Check if OLLAMA_HOST is set (for Docker on macOS)
        ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        base_url = os.getenv("OLLAMA_BASE_URL", f"http://{ollama_host}:11434")
        return ChatOllama(
            model=model_name,
            base_url=base_url,
        )
    elif model_provider == ModelProvider.OPENROUTER:
        api_key = (api_keys or {}).get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print(f"API Key Error: Please make sure OPENROUTER_API_KEY is set in your .env file or provided via API keys.")
            raise ValueError("OpenRouter API key not found. Please make sure OPENROUTER_API_KEY is set in your .env file or provided via API keys.")
        
        # Get optional site URL and name for headers
        site_url = os.getenv("YOUR_SITE_URL", "https://github.com/virattt/ai-hedge-fund")
        site_name = os.getenv("YOUR_SITE_NAME", "AI Hedge Fund")
        
        return ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_kwargs={
                "extra_headers": {
                    "HTTP-Referer": site_url,
                    "X-Title": site_name,
                }
            }
        )
    elif model_provider == ModelProvider.GIGACHAT:
        if os.getenv("GIGACHAT_USER") or os.getenv("GIGACHAT_PASSWORD"):
            return GigaChat(model=model_name)
        else: 
            api_key = (api_keys or {}).get("GIGACHAT_API_KEY") or os.getenv("GIGACHAT_API_KEY") or os.getenv("GIGACHAT_CREDENTIALS")
            if not api_key:
                print("API Key Error: Please make sure api_keys is set in your .env file or provided via API keys.")
                raise ValueError("GigaChat API key not found. Please make sure GIGACHAT_API_KEY is set in your .env file or provided via API keys.")

            return GigaChat(credentials=api_key, model=model_name)


# Convenience functions for easy usage
def print_available_models(api_keys: dict = None):
    """Print all available models based on API keys"""
    available_models = get_available_models(api_keys)
    providers = get_available_providers(api_keys)
    
    print("Available Providers:")
    for provider in providers:
        print(f"  - {provider.value}")
    
    print(f"\nAvailable Models ({len(available_models)} total):")
    for model in available_models:
        print(f"  - {model.display_name} ({model.provider.value})")
