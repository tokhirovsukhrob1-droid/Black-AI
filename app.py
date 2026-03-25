from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>Black AI</title></head>
        <body style="background:black;color:white;text-align:center;">
            <h1>Black AI 🚀</h1>
            <p>AI is connected ✅</p>
        </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return JSONResponse({
        "response": response.choices[0].message.content
    })
