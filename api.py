from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from core.video_processor import process_video
from config.config_handler import DetectorConfig
import os
import shutil
import tempfile
import uuid

app = FastAPI()

PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


@app.post("/process_video")
async def process_video_endpoint(file: UploadFile = File(...)):
    """Endpoint to upload, process, and return a video."""
    try:
        # 1. Create a temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            tmp_path = tmp.name
            shutil.copyfileobj(file.file, tmp)

        # 2. Generate unique output filename
        output_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        output_path = os.path.join(PROCESSED_DIR, output_filename)

        config = DetectorConfig()
        config.show = False
        config.draw_direction = True
        process_video(video_path=tmp_path, config=config, output_path=output_path)

        os.remove(tmp_path)  # Delete the temporary file after processing

        # 4. Create download URL
        download_url = f"/download/{output_filename}"

        return {"download_url": download_url, "message": "Video processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Endpoint to download a processed video."""
    file_path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename, media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
