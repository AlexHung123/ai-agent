from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.chat import Chat, Message
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

class ChatCreate(BaseModel):
    title: str
    focus_mode: str = "writingAssistant"

class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    focus_mode: str
    files: List[dict] = []

@router.get("/chats")
async def get_chats(db: Session = Depends(get_db)):
    try:
        chats = db.query(Chat).order_by(Chat.created_at.desc()).all()
        return [
            ChatResponse(
                id=chat.id,
                title=chat.title,
                created_at=chat.created_at,
                focus_mode=chat.focus_mode,
                files=chat.files or []
            )
            for chat in chats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats")
async def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db)
):
    try:
        chat_id = str(uuid.uuid4())
        new_chat = Chat(
            id=chat_id,
            title=chat_data.title,
            focus_mode=chat_data.focus_mode,
            created_at=datetime.now(),
            files=[]
        )
        db.add(new_chat)
        db.commit()
        
        return ChatResponse(
            id=new_chat.id,
            title=new_chat.title,
            created_at=new_chat.created_at,
            focus_mode=new_chat.focus_mode,
            files=new_chat.files or []
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats/{chat_id}")
async def get_chat(
    chat_id: str,
    db: Session = Depends(get_db)
):
    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
        
        return {
            "chat": ChatResponse(
                id=chat.id,
                title=chat.title,
                created_at=chat.created_at,
                focus_mode=chat.focus_mode,
                files=chat.files or []
            ),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "sources": msg.sources or [],
                    "messageId": msg.message_id,
                    "createdAt": msg.created_at
                }
                for msg in messages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db)
):
    try:
        # Delete messages first
        db.query(Message).filter(Message.chat_id == chat_id).delete()
        
        # Delete chat
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        db.delete(chat)
        db.commit()
        
        return {"message": "Chat deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))