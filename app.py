from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Black AI</title>
        </head>
        <body style="background:black;color:white;text-align:center;">
            <h1>Welcome to Black AI</h1>
            <p>Your AI is working 🔥</p>
        </body>
    </html>
    """
