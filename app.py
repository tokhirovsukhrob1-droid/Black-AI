from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import requests

app = FastAPI()

# API key (Vercel env dan olinadi)
API_KEY = os.getenv("OPENAI_API_KEY")


@app.get("/")
def home():
    return {"message": "AI is working 🚀"}


@app.post("/chat")
async def chat(request: Request):

    # API key tekshiruv
    if not API_KEY:
        return {"error": "API key not found"}

    # userdan data olish
    data = await request.json()
    user_message = data.get("message", "")

    # message tekshiruv
    if not user_message:
        return {"error": "No message provided"}

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
        )

        return JSONResponse(response.json())

    except Exception as e:
        return {"error": str(e)}
