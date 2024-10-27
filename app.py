# app.py
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
import os
import asyncio

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory store for extracted texts
extracted_data = {}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Notify the WebSocket that upload has started
    await notify_clients("Upload started")
    
    # Save the uploaded image
    image_path = f"static/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Notify that processing has begun
    await notify_clients("Processing started")
    
    # Perform OCR
    extracted_text = await extract_text(image_path)
    
    # Store the extracted text
    extracted_data[file.filename] = extracted_text
    
    # Notify that processing is complete
    await notify_clients("Processing complete")
    return {"filename": file.filename, "extracted_text": extracted_text}

async def extract_text(image_path: str):
    # Perform OCR using Tesseract
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

# WebSocket for notifications
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Keep the connection open
    except WebSocketDisconnect:
        clients.remove(websocket)

async def notify_clients(message: str):
    for client in clients:
        await client.send_text(message)

@app.get("/")
async def get():
    return HTMLResponse(open("static/index.html").read())
