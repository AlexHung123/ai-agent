from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.chat import Chat, Message
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import asyncio
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from app.services.llm.providers import (
    get_available_chat_model_providers,
    get_available_embedding_model_providers,
    get_chat_model,
    get_embedding_model
)
from app.services.search.agents import get_search_agent
from app.core.config import settings

router = APIRouter()

class MessageData(BaseModel):
    messageId: str = Field(..., min_length=1, description="Message ID is required")
    chatId: str = Field(..., min_length=1, description="Chat ID is required")
    content: str = Field(..., min_length=1, description="Message content is required")

class ChatModelConfig(BaseModel):
    provider: Optional[str] = None
    name: Optional[str] = None

class EmbeddingModelConfig(BaseModel):
    provider: Optional[str] = None
    name: Optional[str] = None

class ChatRequest(BaseModel):
    message: MessageData
    optimizationMode: str = Field(default="balanced", pattern="^(speed|balanced|quality)$")
    focusMode: str = Field(..., min_length=1, description="Focus mode is required")
    history: List[List[str]] = Field(default=[])
    files: List[str] = Field(default=[])
    chatModel: Optional[ChatModelConfig] = None
    embeddingModel: Optional[EmbeddingModelConfig] = None
    systemInstructions: Optional[str] = None

@router.post("/chat")
async def create_chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        # Validate request body
        message = request.message
        
        if not message.content or message.content.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Please provide a message to process"
            )
        
        # Get available providers
        # chat_model_providers = await get_available_chat_model_providers()
        # embedding_model_providers = await get_available_embedding_model_providers()
        
        # Determine chat model provider and model
        # chat_model_provider_key = (
        #     request.chatModel.provider if request.chatModel and request.chatModel.provider
        #     else list(chat_model_providers.keys())[0] if chat_model_providers
        #     else None
        # )
        
        # if not chat_model_provider_key or chat_model_provider_key not in chat_model_providers:
        #     raise HTTPException(status_code=400, detail="Invalid chat model provider")

        
        
        # chat_model_provider = chat_model_providers[chat_model_provider_key]
        # chat_model_name = (
        #     request.chatModel.name if request.chatModel and request.chatModel.name
        #     else list(chat_model_provider.keys())[0] if chat_model_provider
        #     else None
        # )
        
        # if not chat_model_name or chat_model_name not in chat_model_provider:
        #     raise HTTPException(status_code=400, detail="Invalid chat model")
        
        # chat_model = chat_model_provider[chat_model_name]
        
        # Determine embedding model provider and model
        # embedding_model_provider_key = (
        #     request.embeddingModel.provider if request.embeddingModel and request.embeddingModel.provider
        #     else list(embedding_model_providers.keys())[0] if embedding_model_providers
        #     else None
        # )
        
        # if not embedding_model_provider_key or embedding_model_provider_key not in embedding_model_providers:
        #     raise HTTPException(status_code=400, detail="Invalid embedding model provider")
        
        # embedding_model_provider = embedding_model_providers[embedding_model_provider_key]
        # embedding_model_name = (
        #     request.embeddingModel.name if request.embeddingModel and request.embeddingModel.name
        #     else list(embedding_model_provider.keys())[0] if embedding_model_provider
        #     else None
        # )
        
        # if not embedding_model_name or embedding_model_name not in embedding_model_provider:
        #     raise HTTPException(status_code=400, detail="Invalid embedding model")
        
        # embedding_model = embedding_model_provider[embedding_model_name]
        
        # Create LLM instances
        llm = None
        embedding = None

        request.chatModel.provider = "custom_openai"
        
        if request.chatModel.provider == "custom_openai":
            llm = get_chat_model(
                "custom_openai",
                settings.custom_openai_model_name or "gpt-3.5-turbo",
                customOpenAIKey=settings.custom_openai_api_key,
                customOpenAIBaseURL=settings.custom_openai_api_url
            )
        elif chat_model_provider and chat_model:
            llm = chat_model.model
        
        if not llm:
            raise HTTPException(status_code=400, detail="Invalid chat model")
        
        # if not embedding:
        #     raise HTTPException(status_code=400, detail="Invalid embedding model")
        
        # Generate human message ID
        human_message_id = message.messageId or str(uuid.uuid4())[:14]  # Match crypto.randomBytes(7).toString('hex')
        
        print('---1---')
        print(human_message_id)
        # Convert history to LangChain messages
        history: List[BaseMessage] = []
        for msg in request.history:
            if len(msg) >= 2:
                if msg[0] == "human":
                    history.append(HumanMessage(content=msg[1]))
                else:
                    history.append(AIMessage(content=msg[1]))
        
        # Get search handler
        try:
            handler = get_search_agent(request.focusMode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid focus mode"
            )
        
        # Handle streaming response
        async def generate_response():
            try:
                # Get the response stream
                stream = handler.search_and_answer(
                    message.content,
                    history,
                    llm,
                    None,
                    request.optimizationMode,
                    request.files,
                    request.systemInstructions or ""
                )
                
                received_message = ""
                ai_message_id = str(uuid.uuid4())[:14]
                
                async for chunk in stream:
                    if chunk["type"] == "response":
                        yield f'data: {json.dumps({"type": "message", "data": chunk["data"], "messageId": ai_message_id})}\n\n'
                        received_message += chunk["data"]
                    elif chunk["type"] == "sources":
                        yield f'data: {json.dumps({"type": "sources", "data": chunk["data"], "messageId": ai_message_id})}\n\n'
                        
                        # Save source message to database
                        source_message_id = str(uuid.uuid4())[:14]
                        source_message = Message(
                            id=str(uuid.uuid4()),
                            chat_id=message.chatId,
                            message_id=source_message_id,
                            role="source",
                            sources=chunk["data"],
                            created_at=datetime.now()
                        )
                        db.add(source_message)
                        db.commit()
                    elif chunk["type"] == "messageEnd":
                        yield f'data: {json.dumps({"type": "messageEnd"})}\n\n'
                        
                        # Save AI message to database
                        ai_message = Message(
                            id=str(uuid.uuid4()),
                            content=received_message,
                            chat_id=message.chatId,
                            message_id=ai_message_id,
                            role="assistant",
                            created_at=datetime.now()
                        )
                        db.add(ai_message)
                        db.commit()
                        break
                    elif chunk["type"] == "error":
                        yield f'data: {json.dumps({"type": "error", "data": chunk["data"]})}\n\n'
                        break
                        
            except Exception as e:
                yield f'data: {json.dumps({"type": "error", "data": str(e)})}\n\n'
        
        # Handle history save
        await handle_history_save(message, human_message_id, request.focusMode, request.files, db)
        
        # Return streaming response
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Content-Type": "text/event-stream",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache, no-transform",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing chat request"
        )

async def handle_history_save(
    message: MessageData,
    human_message_id: str,
    focus_mode: str,
    files: List[str],
    db: Session
):
    """Handle saving chat history and user message."""
    try:
        # Check if chat exists
        chat = db.query(Chat).filter(Chat.id == message.chatId).first()
        
        # Get file data (simplified - in real implementation would process files)
        file_data = []
        
        if not chat:
            # Create new chat
            new_chat = Chat(
                id=message.chatId,
                title=message.content,
                created_at=datetime.now(),
                focus_mode=focus_mode,
                files=file_data
            )
            db.add(new_chat)
        else:
            # Update chat files if changed
            if json.dumps(chat.files or []) != json.dumps(file_data):
                chat.files = file_data
        
        # Check if user message exists
        message_exists = db.query(Message).filter(
            Message.message_id == human_message_id
        ).first()
        
        if not message_exists:
            # Create new user message
            user_message = Message(
                id=str(uuid.uuid4()),
                content=message.content,
                chat_id=message.chatId,
                message_id=human_message_id,
                role="user",
                created_at=datetime.now()
            )
            db.add(user_message)
        else:
            # Delete messages after this one (for regeneration)
            db.query(Message).filter(
                Message.id > message_exists.id,
                Message.chat_id == message.chatId
            ).delete()
        
        db.commit()
    except Exception as e:
        db.rollback()
        # Log error but don't fail the request
        print(f"Error saving history: {e}")