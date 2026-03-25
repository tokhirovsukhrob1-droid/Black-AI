from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os
import requests

app = FastAPI()

API_KEY = os.getenv("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Black AI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0b0b0b;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
            }
            #chat-box {
                background: #111;
                border: 1px solid #333;
                border-radius: 12px;
                min-height: 400px;
                padding: 15px;
                overflow-y: auto;
                margin-bottom: 15px;
            }
            .msg {
                margin: 10px 0;
                padding: 10px 14px;
                border-radius: 10px;
                max-width: 80%;
                white-space: pre-wrap;
            }
            .user {
                background: #2563eb;
                margin-left: auto;
                text-align: right;
            }
            .ai {
                background: #1f2937;
                margin-right: auto;
            }
            .row {
                display: flex;
                gap: 10px;
            }
            input {
                flex: 1;
                padding: 14px;
                border-radius: 10px;
                border: 1px solid #333;
                background: #111;
                color: white;
                font-size: 16px;
            }
            button {
                padding: 14px 18px;
                border: none;
                border-radius: 10px;
                background: #2563eb;
                color: white;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover {
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Black AI 🤖</h1>
            <div id="chat-box"></div>
            <div class="row">
                <input id="message" type="text" placeholder="Write something..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById("message");
                const chatBox = document.getElementById("chat-box");
                const text = input.value.trim();

                if (!text) return;

                const userDiv = document.createElement("div");
                userDiv.className = "msg user";
                userDiv.textContent = text;
                chatBox.appendChild(userDiv);

                input.value = "";

                const loadingDiv = document.createElement("div");
                loadingDiv.className = "msg ai";
                loadingDiv.textContent = "Typing...";
                chatBox.appendChild(loadingDiv);

                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    const res = await fetch("/chat", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ message: text })
                    });

                    const data = await res.json();

                    loadingDiv.remove();

                    const aiDiv = document.createElement("div");
                    aiDiv.className = "msg ai";

                    if (data.choices && data.choices[0] && data.choices[0].message) {
                        aiDiv.textContent = data.choices[0].message.content;
                    } else if (data.response) {
                        aiDiv.textContent = data.response;
                    } else if (data.error) {
                        aiDiv.textContent = "Error: " + data.error;
                    } else {
                        aiDiv.textContent = JSON.stringify(data);
                    }

                    chatBox.appendChild(aiDiv);
                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch (err) {
                    loadingDiv.remove();
                    const errDiv = document.createElement("div");
                    errDiv.className = "msg ai";
                    errDiv.textContent = "Error: " + err;
                    chatBox.appendChild(errDiv);
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    if not API_KEY:
        return {"error": "API key not found"}

    data = await request.json()
    user_message = data.get("message", "")

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

        if response.status_code != 200:
            return {"error": response.text}

        return JSONResponse(response.json())

    except Exception as e:
        return {"error": str(e)}
