from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
import json
import asyncio

from app.services.llm.providers import get_chat_model, get_embedding_model, get_available_chat_model_providers, get_available_embedding_model_providers
from app.services.search.agents import get_search_agent

router = APIRouter()

class ChatModel(BaseModel):
    provider: str
    name: str
    customOpenAIKey: Optional[str] = None
    customOpenAIBaseURL: Optional[str] = None

class EmbeddingModel(BaseModel):
    provider: str
    name: str

class SearchRequest(BaseModel):
    optimizationMode: str = "balanced"
    focusMode: str = "writingAssistant"
    chatModel: Optional[ChatModel] = None
    embeddingModel: Optional[EmbeddingModel] = None
    query: str
    history: List[List[str]] = []
    stream: bool = False
    systemInstructions: str = ""

@router.post("/search")
async def search(request: SearchRequest):
    try:
        if not request.focusMode or not request.query:
            raise HTTPException(status_code=400, detail="Missing focus mode or query")
        
        # Get available providers
        chat_providers = await get_available_chat_model_providers()
        embedding_providers = await get_available_embedding_model_providers()
        
        # Determine chat model
        chat_model_provider = request.chatModel.provider if request.chatModel else list(chat_providers.keys())[0] if chat_providers else "openai"
        chat_model_name = request.chatModel.name if request.chatModel else (
            list(chat_providers[chat_model_provider].keys())[0] if chat_model_provider in chat_providers and chat_providers[chat_model_provider] else "gpt-3.5-turbo"
        )
        
        # Determine embedding model
        embedding_model_provider = request.embeddingModel.provider if request.embeddingModel else list(embedding_providers.keys())[0] if embedding_providers else "openai"
        embedding_model_name = request.embeddingModel.name if request.embeddingModel else (
            list(embedding_providers[embedding_model_provider].keys())[0] if embedding_model_provider in embedding_providers and embedding_providers[embedding_model_provider] else "text-embedding-3-small"
        )
        
        # Create model instances
        try:
            llm_kwargs = {}
            if request.chatModel and request.chatModel.customOpenAIKey:
                llm_kwargs["customOpenAIKey"] = request.chatModel.customOpenAIKey
            if request.chatModel and request.chatModel.customOpenAIBaseURL:
                llm_kwargs["customOpenAIBaseURL"] = request.chatModel.customOpenAIBaseURL
            
            llm = get_chat_model(chat_model_provider, chat_model_name, **llm_kwargs)
            embeddings = get_embedding_model(embedding_model_provider, embedding_model_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating models: {str(e)}")
        
        # Convert history to LangChain messages
        chat_history = []
        for role, content in request.history:
            if role == "human":
                chat_history.append(HumanMessage(content=content))
            else:
                chat_history.append(AIMessage(content=content))
        
        # Get search agent
        try:
            search_agent = get_search_agent(request.focusMode)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        if request.stream:
            async def generate():
                try:
                    # Generate response using search agent
                    async for chunk in search_agent.search_and_answer(
                        query=request.query,
                        chat_history=chat_history,
                        llm=llm,
                        embeddings=embeddings,
                        optimization_mode=request.optimizationMode,
                        file_ids=[],  # TODO: Implement file handling
                        system_instructions=request.systemInstructions
                    ):
                        yield f'data: {json.dumps(chunk)}\n\n'
                        
                except Exception as e:
                    yield f'data: {json.dumps({"type": "error", "data": str(e)})}\n\n'
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "Connection": "keep-alive"
                }
            )
        else:
            # Non-streaming response
            response_text = ""
            sources = []
            
            async for chunk in search_agent.search_and_answer(
                query=request.query,
                chat_history=chat_history,
                llm=llm,
                embeddings=embeddings,
                optimization_mode=request.optimizationMode,
                file_ids=[],
                system_instructions=request.systemInstructions
            ):
                if chunk["type"] == "response":
                    response_text += chunk["data"]
                elif chunk["type"] == "sources":
                    sources = chunk["data"]
                elif chunk["type"] == "error":
                    raise HTTPException(status_code=500, detail=chunk["data"])
            
            return {
                "message": response_text,
                "sources": sources
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))