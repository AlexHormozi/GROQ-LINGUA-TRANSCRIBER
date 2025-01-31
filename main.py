import asyncio
import requests
import tempfile
from fastapi import FastAPI, WebSocket

app = FastAPI()

# Groq API Key
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/v1/audio/transcriptions"

@app.get("/")
async def root():
    return {"message": "Welcome to Groq-powered transcription API!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connection established!")

    audio_buffer = bytearray()  # Buffer to store incoming audio

    try:
        while True:
            # Receive audio chunks from the WebSocket
            audio_data = await websocket.receive_bytes()
            audio_buffer.extend(audio_data)  # Append to buffer

            if len(audio_buffer) > 16000:  # Buffer size check (adjust as needed)
                transcription = transcribe_audio_with_groq(audio_buffer)
                await websocket.send_text(transcription)
                audio_buffer.clear()  # Clear buffer after sending
    except Exception as e:
        await websocket.close()
        print(f"WebSocket closed: {e}")

def transcribe_audio_with_groq(audio_bytes):
    """ Sends audio bytes to Groq API for transcription. """
    
    # Save bytes to temporary file (Groq API expects a file)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    # Prepare request
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": open(temp_audio_path, "rb")}
    data = {"model": "whisper-large", "language": "en"}

    # Send request to Groq
    response = requests.post(GROQ_API_URL, headers=headers, files=files, data=data)

    if response.status_code == 200:
        return response.json().get("text", "Transcription failed.")
    else:
        return f"Error: {response.status_code} - {response.text}"
