from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/perplexica"
    
    # LLM API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    # Ollama settings
    ollama_api_url: Optional[str] = None
    ollama_api_key: Optional[str] = None
    
    # Custom OpenAI settings
    custom_openai_api_key: Optional[str] = None
    custom_openai_api_url: Optional[str] = None
    custom_openai_model_name: Optional[str] = None
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    
    # General settings
    similarity_measure: str = "cosine"
    keep_alive: str = "5m"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with environment variables if they exist
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Map environment variables to settings
        env_mapping = {
            'OPENAI_API_KEY': 'openai_api_key',
            'ANTHROPIC_API_KEY': 'anthropic_api_key', 
            'GOOGLE_API_KEY': 'google_api_key',
            'GROQ_API_KEY': 'groq_api_key',
            'DEEPSEEK_API_KEY': 'deepseek_api_key',
            'OLLAMA_API_URL': 'ollama_api_url',
            'OLLAMA_API_KEY': 'ollama_api_key',
            'CUSTOM_OPENAI_API_KEY': 'custom_openai_api_key',
            'CUSTOM_OPENAI_API_URL': 'custom_openai_api_url',
            'CUSTOM_OPENAI_MODEL_NAME': 'custom_openai_model_name',
            'SIMILARITY_MEASURE': 'similarity_measure',
            'KEEP_ALIVE': 'keep_alive',
        }
        
        for env_var, setting_name in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                setattr(self, setting_name, value)

settings = Settings()