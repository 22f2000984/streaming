import os
import json
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

OPENAI_BASE_URL = "https://aipipe.org/openai/v1"
OPENAI_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjIwMDA5ODRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.G7srIOp35q_kYBkoQ9D4CusHekbXlHbCvsP4YiuaoRM"
MODEL = "gpt-4o-mini"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# ==============================
# SSE Streaming Generator
# ==============================

async def stream_generator(prompt: str):
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{OPENAI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "stream": True,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Write a 222-word article about renewable energy. "
                                       f"Include quotes and statistics. Ensure it is over 888 characters."
                        }
                    ],
                },
            ) as response:

                # async for line in response.aiter_lines():
                #     if line.startswith("data: "):
                #         if line.strip() == "data: [DONE]":
                #             yield "data: [DONE]\n\n"
                #             break

                #         try:
                #             payload = json.loads(line[6:])
                #             delta = payload["choices"][0]["delta"]
                #             if "content" in delta:
                #                 chunk = delta["content"]
                #                 sse_data = json.dumps(
                #                     {"choices": [{"delta": {"content": chunk}}]}
                #                 )
                #                 yield f"data: {sse_data}\n\n"
                #                 await asyncio.sleep(0)  # flush immediately
                #         except Exception:
                #             continue
                async for line in response.aiter_lines():

                    if not line:
                        continue

                    if not line.startswith("data: "):
                        continue

                    data = line[6:].strip()

                    if data == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break

                    try:
                        payload = json.loads(data)
                    except json.JSONDecodeError:
                        continue  # skip malformed chunks safely

                    delta = payload.get("choices", [{}])[0].get("delta", {})

                    content = delta.get("content")
                    if content:
                        sse_data = json.dumps(
                            {"choices": [{"delta": {"content": content}}]}
                        )
                        yield f"data: {sse_data}\n\n"
                        await asyncio.sleep(0)


    except Exception:
        error_event = json.dumps(
            {"error": "Streaming service temporarily unavailable"}
        )
        yield f"data: {error_event}\n\n"
        yield "data: [DONE]\n\n"

# ==============================
# API Endpoint
# ==============================

@app.post("/stream")
async def stream_endpoint(request: Request):
    body = await request.json()

    if not body.get("stream", False):
        return {"error": "Streaming must be enabled (stream: true)"}

    prompt = body.get("prompt", "Generate article")

    return StreamingResponse(
        stream_generator(prompt),
        media_type="text/event-stream",
    )
