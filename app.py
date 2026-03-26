from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os
import requests

app = FastAPI()

user_limits = {}
paid_users = []  # premium user IP larini shu yerga qo‘shasan
API_KEY = os.getenv("OPENAI_API_KEY")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ShadowAI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #0b0b0b, #1a0033);
                color: white;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
            }
            #chat-box {
                background: #111;
                border: 1px solid #2a2a2a;
                border-radius: 16px;
                height: 500px;
                padding: 16px;
                overflow-y: auto;
                margin-bottom: 16px;
                box-shadow: 0 0 20px rgba(0,0,0,0.25);
            }
            .msg {
                margin: 10px 0;
                padding: 12px 14px;
                border-radius: 14px;
                max-width: 80%;
                white-space: pre-wrap;
                line-height: 1.5;
            }
            .user {
                background: #7c3aed;
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
                border-radius: 12px;
                border: 1px solid #2a2a2a;
                background: #111;
                color: white;
                font-size: 16px;
                outline: none;
            }
            button {
                padding: 14px 18px;
                border: none;
                border-radius: 12px;
                background: #4f6bed;
                color: white;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover {
                opacity: 0.92;
            }
            .avatar {
                font-size: 13px;
                opacity: 0.7;
                margin-bottom: 4px;
            }
            .left-count {
                font-size: 12px;
                color: #9ca3af;
                margin-top: 6px;
                margin-bottom: 8px;
            }
            .upgrade {
                margin-top: 10px;
                color: #facc15;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ShadowAI 🌑</h1>
            <div id="chat-box"></div>
            <div class="row">
                <input id="message" type="text" placeholder="Write something..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let history = [];

            function addMessage(role, text) {
                const chatBox = document.getElementById("chat-box");
                const wrapper = document.createElement("div");

                const avatar = document.createElement("div");
                avatar.className = "avatar";
                avatar.textContent = role === "user" ? "You" : "ShadowAI";

                const msg = document.createElement("div");
                msg.className = "msg " + (role === "user" ? "user" : "ai");
                msg.textContent = text;

                wrapper.appendChild(avatar);
                wrapper.appendChild(msg);
                chatBox.appendChild(wrapper);
                chatBox.scrollTop = chatBox.scrollHeight;
                return msg;
            }

            function addRemainingCount(count) {
                const chatBox = document.getElementById("chat-box");
                const left = document.createElement("div");
                left.className = "left-count";
                left.textContent = "Messages left: " + count;
                chatBox.appendChild(left);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function addUpgradeText() {
                const chatBox = document.getElementById("chat-box");
                const up = document.createElement("div");
                up.className = "upgrade";
                up.textContent = "Upgrade to Premium 💎";
                chatBox.appendChild(up);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            async function sendMessage() {
                const input = document.getElementById("message");
                const text = input.value.trim();
                if (!text) return;

                history.push({ role: "user", content: text });
                addMessage("user", text);
                input.value = "";

                const typing = addMessage("ai", "Typing...");

                try {
                    const res = await fetch("/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ messages: history })
                    });

                    const data = await res.json();
                    typing.textContent = "";

                    let reply = "Error";
                    if (data.reply) {
                        reply = data.reply;
                    } else if (data.error) {
                        reply = "Error: " + data.error;
                    }

                    history.push({ role: "assistant", content: reply });

                    let i = 0;
                    const timer = setInterval(() => {
                        typing.textContent = reply.slice(0, i);
                        i++;
                        if (i > reply.length) clearInterval(timer);
                    }, 12);

                    if (data.remaining !== undefined) {
                        addRemainingCount(data.remaining);
                    }

                    if (data.error && data.error.includes("Premium")) {
                        addUpgradeText();
                    }

                } catch (err) {
                    typing.textContent = "Error: " + err;
                }
            }

            document.getElementById("message").addEventListener("keydown", function(e) {
                if (e.key === "Enter") {
                    sendMessage();
                }
            });

            addMessage("ai", "Welcome to ShadowAI 🌑. Ask me anything...");
        </script>
    </body>
    </html>
    """


@app.post("/chat")
async def chat(request: Request):
    ip = request.client.host

    if ip not in user_limits:
        user_limits[ip] = 0

    limit = 1000 if ip in paid_users else 10

    if user_limits[ip] >= limit:
        return JSONResponse({
            "error": "Upgrade to Premium 💎"
        }, status_code=429)

    user_limits[ip] += 1
    remaining = max(0, limit - user_limits[ip])

    if not API_KEY:
        return {"error": "API key not found"}

    data = await request.json()
    messages = data.get("messages", [])

    if not messages:
        return {"error": "No messages provided"}

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages
            }
        )

        if response.status_code != 200:
            return {"error": response.text}

        result = response.json()
        reply = result["choices"][0]["message"]["content"]

        return JSONResponse({
            "reply": reply,
            "remaining": remaining
        })

    except Exception as e:
        return {"error": str(e)}
