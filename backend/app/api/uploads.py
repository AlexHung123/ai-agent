from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
import os

router = APIRouter()

@router.post("/uploads")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        uploaded_files = []
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        for file in files:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename)[1]
            filename = f"{file_id}{file_extension}"
            file_path = os.path.join(uploads_dir, filename)
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append({
                "fileId": file_id,
                "name": file.filename,
                "size": len(content)
            })
        
        return {"files": uploaded_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))