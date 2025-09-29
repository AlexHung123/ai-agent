from typing import Dict, Any, Optional, List, Callable, Awaitable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.config import settings
import httpx
import asyncio
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChatModel:
    display_name: str
    model: BaseChatModel

@dataclass
class EmbeddingModel:
    display_name: str
    model: Embeddings

@dataclass
class ProviderInfo:
    key: str
    display_name: str

# Provider Info
OPENAI_PROVIDER = ProviderInfo(key="openai", display_name="OpenAI")
ANTHROPIC_PROVIDER = ProviderInfo(key="anthropic", display_name="Anthropic")
GEMINI_PROVIDER = ProviderInfo(key="gemini", display_name="Google Gemini")
GROQ_PROVIDER = ProviderInfo(key="groq", display_name="Groq")
OLLAMA_PROVIDER = ProviderInfo(key="ollama", display_name="Ollama")
CUSTOM_OPENAI_PROVIDER = ProviderInfo(key="custom_openai", display_name="Custom OpenAI")

PROVIDER_METADATA = {
    "openai": OPENAI_PROVIDER,
    "anthropic": ANTHROPIC_PROVIDER,
    "gemini": GEMINI_PROVIDER,
    "groq": GROQ_PROVIDER,
    "ollama": OLLAMA_PROVIDER,
    "custom_openai": CUSTOM_OPENAI_PROVIDER,
}

# Model definitions matching TypeScript implementation
OPENAI_CHAT_MODELS = [
    {"display_name": "GPT-3.5 Turbo", "key": "gpt-3.5-turbo"},
    {"display_name": "GPT-4", "key": "gpt-4"},
    {"display_name": "GPT-4 turbo", "key": "gpt-4-turbo"},
    {"display_name": "GPT-4 omni", "key": "gpt-4o"},
    {"display_name": "GPT-4o (2024-05-13)", "key": "gpt-4o-2024-05-13"},
    {"display_name": "GPT-4 omni mini", "key": "gpt-4o-mini"},
    {"display_name": "o1", "key": "o1"},
    {"display_name": "o3", "key": "o3"},
    {"display_name": "o3 Mini", "key": "o3-mini"},
]

OPENAI_EMBEDDING_MODELS = [
    {"display_name": "Text Embedding 3 Small", "key": "text-embedding-3-small"},
    {"display_name": "Text Embedding 3 Large", "key": "text-embedding-3-large"},
]

ANTHROPIC_CHAT_MODELS = [
    {"display_name": "Claude 3.5 Haiku", "key": "claude-3-5-haiku-20241022"},
    {"display_name": "Claude 3.5 Sonnet v2", "key": "claude-3-5-sonnet-20241022"},
    {"display_name": "Claude 3.5 Sonnet", "key": "claude-3-5-sonnet-20240620"},
    {"display_name": "Claude 3 Opus", "key": "claude-3-opus-20240229"},
    {"display_name": "Claude 3 Sonnet", "key": "claude-3-sonnet-20240229"},
    {"display_name": "Claude 3 Haiku", "key": "claude-3-haiku-20240307"},
]

GEMINI_CHAT_MODELS = [
    {"display_name": "Gemini 2.0 Flash", "key": "gemini-2.0-flash"},
    {"display_name": "Gemini 1.5 Flash", "key": "gemini-1.5-flash"},
    {"display_name": "Gemini 1.5 Flash-8B", "key": "gemini-1.5-flash-8b"},
    {"display_name": "Gemini 1.5 Pro", "key": "gemini-1.5-pro"},
]

GEMINI_EMBEDDING_MODELS = [
    {"display_name": "Text Embedding 004", "key": "models/text-embedding-004"},
    {"display_name": "Embedding 001", "key": "models/embedding-001"},
]

GROQ_CHAT_MODELS = [
    {"display_name": "Llama 3.1 8B Instant", "key": "llama-3.1-8b-instant"},
    {"display_name": "Llama 3.1 70B Versatile", "key": "llama-3.1-70b-versatile"},
    {"display_name": "Llama 3.2 1B Preview", "key": "llama-3.2-1b-preview"},
    {"display_name": "Llama 3.2 3B Preview", "key": "llama-3.2-3b-preview"},
]
# Provider loading functions
async def load_openai_chat_models() -> Dict[str, ChatModel]:
    """Load OpenAI chat models."""
    if not settings.openai_api_key:
        return {}
    
    try:
        chat_models = {}
        for model in OPENAI_CHAT_MODELS:
            # Temperature-restricted models
            temperature_restricted = ['o1', 'o3', 'o3-mini']
            is_restricted = any(restricted in model["key"] for restricted in temperature_restricted)
            
            model_config = {
                "api_key": settings.openai_api_key,
                "model": model["key"],
            }
            
            if not is_restricted:
                model_config["temperature"] = 0.7
            
            chat_models[model["key"]] = ChatModel(
                display_name=model["display_name"],
                model=ChatOpenAI(**model_config)
            )
        
        return chat_models
    except Exception as e:
        logger.error(f"Error loading OpenAI models: {e}")
        return {}

async def load_openai_embedding_models() -> Dict[str, EmbeddingModel]:
    """Load OpenAI embedding models."""
    if not settings.openai_api_key:
        return {}
    
    try:
        embedding_models = {}
        for model in OPENAI_EMBEDDING_MODELS:
            embedding_models[model["key"]] = EmbeddingModel(
                display_name=model["display_name"],
                model=OpenAIEmbeddings(
                    api_key=settings.openai_api_key,
                    model=model["key"]
                )
            )
        
        return embedding_models
    except Exception as e:
        logger.error(f"Error loading OpenAI embedding models: {e}")
        return {}

async def load_anthropic_chat_models() -> Dict[str, ChatModel]:
    """Load Anthropic chat models."""
    if not settings.anthropic_api_key:
        return {}
    
    try:
        chat_models = {}
        for model in ANTHROPIC_CHAT_MODELS:
            chat_models[model["key"]] = ChatModel(
                display_name=model["display_name"],
                model=ChatAnthropic(
                    api_key=settings.anthropic_api_key,
                    model=model["key"],
                    temperature=0.7
                )
            )
        
        return chat_models
    except Exception as e:
        logger.error(f"Error loading Anthropic models: {e}")
        return {}

async def load_gemini_chat_models() -> Dict[str, ChatModel]:
    """Load Gemini chat models."""
    if not settings.google_api_key:
        return {}
    
    try:
        chat_models = {}
        for model in GEMINI_CHAT_MODELS:
            chat_models[model["key"]] = ChatModel(
                display_name=model["display_name"],
                model=ChatGoogleGenerativeAI(
                    google_api_key=settings.google_api_key,
                    model=model["key"],
                    temperature=0.7
                )
            )
        
        return chat_models
    except Exception as e:
        logger.error(f"Error loading Gemini models: {e}")
        return {}

async def load_gemini_embedding_models() -> Dict[str, EmbeddingModel]:
    """Load Gemini embedding models."""
    if not settings.google_api_key:
        return {}
    
    try:
        embedding_models = {}
        for model in GEMINI_EMBEDDING_MODELS:
            embedding_models[model["key"]] = EmbeddingModel(
                display_name=model["display_name"],
                model=GoogleGenerativeAIEmbeddings(
                    google_api_key=settings.google_api_key,
                    model=model["key"]
                )
            )
        
        return embedding_models
    except Exception as e:
        logger.error(f"Error loading Gemini embedding models: {e}")
        return {}

async def load_groq_chat_models() -> Dict[str, ChatModel]:
    """Load Groq chat models."""
    if not settings.groq_api_key:
        return {}
    
    try:
        chat_models = {}
        for model in GROQ_CHAT_MODELS:
            chat_models[model["key"]] = ChatModel(
                display_name=model["display_name"],
                model=ChatGroq(
                    groq_api_key=settings.groq_api_key,
                    model=model["key"],
                    temperature=0.7
                )
            )
        
        return chat_models
    except Exception as e:
        logger.error(f"Error loading Groq models: {e}")
        return {}

async def load_ollama_chat_models() -> Dict[str, ChatModel]:
    """Load Ollama chat models."""
    ollama_url = getattr(settings, 'ollama_api_url', None)
    if not ollama_url:
        return {}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags")
            if response.status_code != 200:
                return {}
            
            data = response.json()
            models = data.get("models", [])
            
            chat_models = {}
            for model in models:
                model_name = model.get("model", model.get("name", ""))
                display_name = model.get("name", model_name)
                
                model_config = {
                    "base_url": ollama_url,
                    "model": model_name,
                    "temperature": 0.7,
                }
                
                # Add API key if configured
                ollama_api_key = getattr(settings, 'ollama_api_key', None)
                if ollama_api_key:
                    model_config["headers"] = {"Authorization": f"Bearer {ollama_api_key}"}
                
                chat_models[model_name] = ChatModel(
                    display_name=display_name,
                    model=ChatOllama(**model_config)
                )
            
            return chat_models
    except Exception as e:
        logger.error(f"Error loading Ollama models: {e}")
        return {}

async def load_ollama_embedding_models() -> Dict[str, EmbeddingModel]:
    """Load Ollama embedding models."""
    ollama_url = getattr(settings, 'ollama_api_url', None)
    if not ollama_url:
        return {}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags")
            if response.status_code != 200:
                return {}
            
            data = response.json()
            models = data.get("models", [])
            
            embedding_models = {}
            for model in models:
                model_name = model.get("model", model.get("name", ""))
                display_name = model.get("name", model_name)
                
                model_config = {
                    "base_url": ollama_url,
                    "model": model_name,
                }
                
                # Add API key if configured
                ollama_api_key = getattr(settings, 'ollama_api_key', None)
                if ollama_api_key:
                    model_config["headers"] = {"Authorization": f"Bearer {ollama_api_key}"}
                
                embedding_models[model_name] = EmbeddingModel(
                    display_name=display_name,
                    model=OllamaEmbeddings(**model_config)
                )
            
            return embedding_models
    except Exception as e:
        logger.error(f"Error loading Ollama embedding models: {e}")
        return {}

# Chat model providers registry
chat_model_providers: Dict[str, Callable[[], Awaitable[Dict[str, ChatModel]]]] = {
    "openai": load_openai_chat_models,
    "anthropic": load_anthropic_chat_models,
    "gemini": load_gemini_chat_models,
    "groq": load_groq_chat_models,
    "ollama": load_ollama_chat_models,
}

# Embedding model providers registry
embedding_model_providers: Dict[str, Callable[[], Awaitable[Dict[str, EmbeddingModel]]]] = {
    "openai": load_openai_embedding_models,
    "gemini": load_gemini_embedding_models,
    "ollama": load_ollama_embedding_models,
}

async def get_available_chat_model_providers() -> Dict[str, Dict[str, ChatModel]]:
    """Get all available chat model providers."""
    models = {}
    
    for provider, loader in chat_model_providers.items():
        provider_models = await loader()
        if provider_models:
            models[provider] = provider_models
    
    # Add custom OpenAI if configured
    if (settings.custom_openai_api_key and 
        settings.custom_openai_api_url and 
        settings.custom_openai_model_name):
        
        temperature_restricted = ['o1', 'o3', 'o3-mini']
        is_restricted = any(restricted in settings.custom_openai_model_name 
                          for restricted in temperature_restricted)
        
        model_config = {
            "api_key": settings.custom_openai_api_key,
            "model": settings.custom_openai_model_name,
            "base_url": settings.custom_openai_api_url,
        }
        
        if not is_restricted:
            model_config["temperature"] = 0.7
        
        models["custom_openai"] = {
            settings.custom_openai_model_name: ChatModel(
                display_name=settings.custom_openai_model_name,
                model=ChatOpenAI(**model_config)
            )
        }
    
    return models

async def get_available_embedding_model_providers() -> Dict[str, Dict[str, EmbeddingModel]]:
    """Get all available embedding model providers."""
    models = {}
    
    for provider, loader in embedding_model_providers.items():
        provider_models = await loader()
        if provider_models:
            models[provider] = provider_models
    
    return models

def get_chat_model(provider: str, model: str, **kwargs) -> BaseChatModel:
    """Get a chat model instance based on provider and model name."""
    
    if provider == "openai":
        temperature_restricted = ['o1', 'o3', 'o3-mini']
        is_restricted = any(restricted in model for restricted in temperature_restricted)
        
        model_config = {
            "model": model,
            "api_key": settings.openai_api_key,
            **kwargs
        }
        
        if not is_restricted:
            model_config["temperature"] = 0.7
        
        return ChatOpenAI(**model_config)
    
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model,
            api_key=settings.anthropic_api_key,
            temperature=0.7,
            **kwargs
        )
    
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.google_api_key,
            temperature=0.7,
            **kwargs
        )
    
    elif provider == "groq":
        return ChatGroq(
            model=model,
            groq_api_key=settings.groq_api_key,
            temperature=0.7,
            **kwargs
        )
    
    elif provider == "custom_openai":
        custom_model = kwargs.get("name") or settings.custom_openai_model_name or model
        temperature_restricted = ['o1', 'o3', 'o3-mini']
        is_restricted = any(restricted in custom_model for restricted in temperature_restricted)
        
        model_config = {
            "model": custom_model,
            "api_key": kwargs.get("customOpenAIKey") or settings.custom_openai_api_key,
            "base_url": kwargs.get("customOpenAIBaseURL") or settings.custom_openai_api_url,
        }
        
        if not is_restricted:
            model_config["temperature"] = 0.7
        
        return ChatOpenAI(**model_config)
    
    else:
        raise ValueError(f"Unsupported chat model provider: {provider}")

def get_embedding_model(provider: str, model: str, **kwargs) -> Embeddings:
    """Get an embedding model instance based on provider and model name."""
    
    if provider == "openai":
        return OpenAIEmbeddings(
            model=model,
            api_key=settings.openai_api_key,
            **kwargs
        )
    
    elif provider == "gemini":
        return GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=settings.google_api_key,
            **kwargs
        )
    
    else:
        raise ValueError(f"Unsupported embedding model provider: {provider}")

async def get_available_models() -> Dict[str, Any]:
    """Get available models for both chat and embedding - formatted for API response."""
    
    chat_providers = await get_available_chat_model_providers()
    embedding_providers = await get_available_embedding_model_providers()
    
    # Format for API response
    formatted_chat = {}
    for provider, models in chat_providers.items():
        formatted_chat[provider] = [
            {
                "name": model_key,
                "displayName": model_obj.display_name
            }
            for model_key, model_obj in models.items()
        ]
    
    formatted_embedding = {}
    for provider, models in embedding_providers.items():
        formatted_embedding[provider] = [
            {
                "name": model_key,
                "displayName": model_obj.display_name
            }
            for model_key, model_obj in models.items()
        ]
    
    return {
        "chatModelProviders": formatted_chat,
        "embeddingModelProviders": formatted_embedding
    }