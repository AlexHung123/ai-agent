from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.llm.providers import get_available_chat_model_providers, get_available_embedding_model_providers, PROVIDER_METADATA

router = APIRouter()

class ConfigResponse(BaseModel):
    openaiApiKey: Optional[str] = None
    ollamaApiUrl: Optional[str] = None
    ollamaApiKey: Optional[str] = None
    anthropicApiKey: Optional[str] = None
    groqApiKey: Optional[str] = None
    geminiApiKey: Optional[str] = None
    deepseekApiKey: Optional[str] = None
    customOpenaiApiKey: Optional[str] = None
    customOpenaiApiUrl: Optional[str] = None
    customOpenaiModelName: Optional[str] = None
    chatModelProviders: Dict[str, Any] = {}
    embeddingModelProviders: Dict[str, Any] = {}

@router.get("/config")
async def get_config():
    try:
        # Get available providers
        chat_providers = await get_available_chat_model_providers()
        embedding_providers = await get_available_embedding_model_providers()
        
        # Format providers for frontend
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
        
        # Return configuration (mask sensitive data)
        return {
            "chatModelProviders": formatted_chat,
            "embeddingModelProviders": formatted_embedding,
            "openaiApiKey": "***" if settings.openai_api_key else "",
            "ollamaApiUrl": settings.ollama_api_url or "",
            "ollamaApiKey": "***" if getattr(settings, 'ollama_api_key', None) else "",
            "anthropicApiKey": "***" if settings.anthropic_api_key else "",
            "groqApiKey": "***" if settings.groq_api_key else "",
            "geminiApiKey": "***" if settings.google_api_key else "",
            "deepseekApiKey": "***" if settings.deepseek_api_key else "",
            "customOpenaiApiKey": "***" if settings.custom_openai_api_key else "",
            "customOpenaiApiUrl": settings.custom_openai_api_url or "",
            "customOpenaiModelName": settings.custom_openai_model_name or "",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
async def update_config(config_data: Dict[str, Any]):
    try:
        # Map the configuration data to settings
        # Note: In a real implementation, you'd want to update the actual config file
        # For now, we'll just acknowledge the update
        
        # Update settings if needed (this is a simplified approach)
        if "openaiApiKey" in config_data and config_data["openaiApiKey"]:
            settings.openai_api_key = config_data["openaiApiKey"]
        
        if "anthropicApiKey" in config_data and config_data["anthropicApiKey"]:
            settings.anthropic_api_key = config_data["anthropicApiKey"]
        
        if "groqApiKey" in config_data and config_data["groqApiKey"]:
            settings.groq_api_key = config_data["groqApiKey"]
        
        if "geminiApiKey" in config_data and config_data["geminiApiKey"]:
            settings.google_api_key = config_data["geminiApiKey"]
        
        if "ollamaApiUrl" in config_data:
            settings.ollama_api_url = config_data["ollamaApiUrl"]
        
        if "customOpenaiApiKey" in config_data:
            settings.custom_openai_api_key = config_data["customOpenaiApiKey"]
        
        if "customOpenaiApiUrl" in config_data:
            settings.custom_openai_api_url = config_data["customOpenaiApiUrl"]
        
        if "customOpenaiModelName" in config_data:
            settings.custom_openai_model_name = config_data["customOpenaiModelName"]
        
        return {"message": "Config updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))