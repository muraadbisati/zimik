from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/images/{image_name}")
async def get_image(image_name: str):
    file_path = os.path.join("images", image_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}
