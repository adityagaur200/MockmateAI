from fastapi import APIRouter, UploadFile, File, HTTPException
from app.service.media_service import save_file

router = APIRouter()


#Upload Audio/Video File
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = await save_file(file)

        return {
            "message": "File uploaded successfully",
            "file_path": file_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))