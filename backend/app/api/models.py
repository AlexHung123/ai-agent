from fastapi import APIRouter, HTTPException
from typing import Dict, List
from app.services.llm.providers import get_available_models

router = APIRouter()

@router.get("/models")
async def get_models():
    try:
        # Return available models
        return await get_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))