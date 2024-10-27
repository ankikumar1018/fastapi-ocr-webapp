from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
import os
import asyncio
from typing import List, Dict
import aiofiles
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Ensure static directory exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use a more thread-safe approach for storing WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        async with self._lock:
            disconnected_clients = []
            for client in self.active_connections:
                try:
                    await client.send_text(message)
                except WebSocketDisconnect:
                    disconnected_clients.append(client)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.active_connections.remove(client)

manager = ConnectionManager()

# Thread-safe storage for extracted texts
class DataStore:
    def __init__(self):
        self.data: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def set(self, key: str, value: str):
        async with self._lock:
            self.data[key] = value

    async def get(self, key: str) -> str:
        async with self._lock:
            return self.data.get(key)

extracted_data = DataStore()

async def safe_file_operations(file_path: str, file: UploadFile) -> None:
    """Safely handle file operations with proper cleanup."""
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

async def extract_text(image_path: str) -> str:
    """Extract text from image with error handling."""
    try:
        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img)
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        raise HTTPException(status_code=500, detail="Text extraction failed")
    finally:
        # Optionally remove temporary file
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                logger.error(f"Error removing temporary file: {e}")

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Generate safe filename
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{asyncio.current_task().get_name()}{file_extension}"
        image_path = os.path.join("static", safe_filename)

        await manager.broadcast("Upload started")
        await safe_file_operations(image_path, file)
        
        await manager.broadcast("Processing started")
        extracted_text = await extract_text(image_path)
        
        await extracted_data.set(file.filename, extracted_text)
        await manager.broadcast("Processing complete")
        
        return {
            "filename": file.filename,
            "extracted_text": extracted_text
        }
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        await manager.broadcast(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing failed")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive and handle incoming messages
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)

@app.get("/")
async def get():
    try:
        async with aiofiles.open("static/index.html", mode='r') as f:
            content = await f.read()
        return HTMLResponse(content)
    except Exception as e:
        logger.error(f"Error reading index.html: {e}")
        raise HTTPException(status_code=500, detail="Failed to load page")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")