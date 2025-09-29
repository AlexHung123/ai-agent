from sqlalchemy import Column, String, DateTime, JSON, func
from app.core.database import Base
from typing import List, Dict, Any

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    focus_mode = Column(String, nullable=False)
    files = Column(JSON, default=[])

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    role = Column(String, nullable=False)  # 'assistant', 'user', 'source'
    chat_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    message_id = Column(String, nullable=False)
    content = Column(String)
    sources = Column(JSON, default=[])