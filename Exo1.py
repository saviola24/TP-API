from fastapi import FastAPI
from starlette.responses import PlainTextResponse
app = FastAPI()
@app.get("/ping", response_model=PlainTextResponse)
async def ping():
    return PlainTextResponse("pong")