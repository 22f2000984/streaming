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

# async def stream_generator(prompt: str):
#     try:
#         async with httpx.AsyncClient(timeout=None) as client:
#             async with client.stream(
#                 "POST",
#                 f"{OPENAI_BASE_URL}/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {OPENAI_API_KEY}",
#                     "Content-Type": "application/json",
#                 },
#                 json={
#                     "model": MODEL,
#                     "stream": True,
#                     "messages": [
#                         {
#                             "role": "user",
#                             "content": f"Write a 222-word article about renewable energy. "
#                                        f"Include quotes and statistics. Ensure it is over 888 characters."
#                         }
#                     ],
#                 },
#             ) as response:
#                 if response.status_code != 200:
#                     error_text = await response.aread()
#                     yield f'data: {json.dumps({"error": "Upstream error"})}\n\n'
#                     yield "data: [DONE]\n\n"
#                     return

#                 # async for line in response.aiter_lines():
#                 #     if line.startswith("data: "):
#                 #         if line.strip() == "data: [DONE]":
#                 #             yield "data: [DONE]\n\n"
#                 #             break

#                 #         try:
#                 #             payload = json.loads(line[6:])
#                 #             delta = payload["choices"][0]["delta"]
#                 #             if "content" in delta:
#                 #                 chunk = delta["content"]
#                 #                 sse_data = json.dumps(
#                 #                     {"choices": [{"delta": {"content": chunk}}]}
#                 #                 )
#                 #                 yield f"data: {sse_data}\n\n"
#                 #                 await asyncio.sleep(0)  # flush immediately
#                 #         except Exception:
#                 #             continue
#                 # 
#                 async for line in response.aiter_lines():

#                     if not line:
#                         continue

#                     if not line.startswith("data:"):
#                         continue

#                     data = line.replace("data:", "", 1).strip()

#                     # Skip empty lines
#                     if not data:
#                         continue

#                     # Handle end of stream
#                     if data == "[DONE]":
#                         yield "data: [DONE]\n\n"
#                         break

#                     try:
#                         payload = json.loads(data)
#                     except json.JSONDecodeError:
#                         continue  # ignore malformed chunk safely

#                     delta = payload.get("choices", [{}])[0].get("delta", {})
#                     content = delta.get("content")

#                     if content:
#                         yield f'data: {json.dumps({"choices":[{"delta":{"content":content}}]})}\n\n'
#                         await asyncio.sleep(0)



#     except Exception:
#         error_event = json.dumps(
#             {"error": "Streaming service temporarily unavailable"}
#         )
#         yield f"data: {error_event}\n\n"
#         yield "data: [DONE]\n\n"

# async def stream_generator(prompt: str):
#     try:
        # # async with httpx.AsyncClient(timeout=None) as client:
        #     client = httpx.AsyncClient(timeout=None)

        #     async with client.stream(
        #         "POST",
        #         f"{OPENAI_BASE_URL}/chat/completions",
        #         headers={
        #             "Authorization": f"Bearer {OPENAI_API_KEY}",
        #             "Content-Type": "application/json",
        #         },
        #         json={
        #             "model": MODEL,
        #             "stream": True,
        #             "max_tokens": 350,
        #             "messages": [
        #                 {
        #                     "role": "user",
        #                     "content": "Write a 222-word article about renewable energy. "
        #                                "Include quotes and statistics. Ensure it is over 888 characters."
        #                 }
        #             ],
        #         },
        #     ) as response:

        #         # 🔥 SAFETY CHECK #1 — HTTP STATUS
        #         if response.status_code != 200:
        #             yield f'data: {json.dumps({"error": "Upstream API error"})}\n\n'
        #             yield "data: [DONE]\n\n"
        #             return

        #         # async for raw_line in response.aiter_lines():

        #         #     # SAFETY CHECK #2 — skip empty lines
        #         #     if not raw_line:
        #         #         continue

        #         #     # SAFETY CHECK #3 — only process data lines
        #         #     if not raw_line.startswith("data:"):
        #         #         continue

        #         #     data = raw_line[len("data:"):].strip()

        #         #     # SAFETY CHECK #4 — skip empty payload
        #         #     if not data:
        #         #         continue

        #         #     # Handle stream end
        #         #     if data == "[DONE]":
        #         #         yield "data: [DONE]\n\n"
        #         #         break

        #         #     # SAFETY CHECK #5 — JSON decode safely
        #         #     try:
        #         #         payload = json.loads(data)
        #         #     except Exception:
        #         #         continue

        #         #     delta = payload.get("choices", [{}])[0].get("delta", {})
        #         #     content = delta.get("content")

        #         #     if content:
        #         #         yield f'data: {json.dumps({"choices":[{"delta":{"content":content}}]})}\n\n'
        #         #         await asyncio.sleep(0)
        #         buffer = ""

        #         async for raw_line in response.aiter_lines():

        #             if not raw_line or not raw_line.startswith("data:"):
        #                 continue

        #             data = raw_line[len("data:"):].strip()

        #             if not data:
        #                 continue

        #             if data == "[DONE]":
        #                 if buffer:
        #                     # yield f'data: {json.dumps({"choices":[{"delta":{"content":buffer}}]})}\n\n'
        #                     yield json.dumps({"content": buffer}) + "\n"
        #                 yield "data: [DONE]\n\n"
        #                 break

        #             try:
        #                 payload = json.loads(data)
        #             except:
        #                 continue

        #             delta = payload.get("choices", [{}])[0].get("delta", {})
        #             content = delta.get("content")

        #             if content:
        #                 buffer += content

        #                 # Send larger chunks (~80 chars)
        #                 # if len(buffer) > 80:
        #                 if len(buffer) >= 250:
        #                     # yield f'data: {json.dumps({"choices":[{"delta":{"content":buffer}}]})}\n\n'
        #                     yield json.dumps({"content": buffer}) + "\n"
        #                     buffer = ""
async def stream_generator(prompt: str):
    buffer = ""
    try:
        # async with httpx.AsyncClient(timeout=None) as client:
        client = httpx.AsyncClient(timeout=None)
        async with client.stream(
            "POST",
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            # json={
            #     "model": MODEL,
            #     "stream": True,
            #     "max_tokens": 350,
            #     "messages": [{"role": "user", "content": prompt}],
            # },
            json={
                    "model": "gpt-4o-mini",
                    "stream": True,
                    "max_tokens": 350,
                    "temperature": 0.7,
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "Write an article about renewable energy. "
                                "Start immediately. Include quotes and statistics."
                            )
                        }
                    ],
                },

        ) as response:

            if response.status_code != 200:
                yield json.dumps({"error": "Upstream error"}) + "\n"
                return

            async for raw_line in response.aiter_lines():
                if not raw_line or not raw_line.startswith("data:"):
                    continue

                data = raw_line[5:].strip()
                if not data or data == "[DONE]":
                    break

                try:
                    payload = json.loads(data)
                except:
                    continue

                content = payload.get("choices", [{}])[0].get("delta", {}).get("content")
                if content:
                    buffer += content

                    # 🔥 BIG CHUNKS = HIGH THROUGHPUT
                    if len(buffer) >= 250:
                        yield json.dumps({"content": buffer}) + "\n"
                        buffer = ""

            if buffer:
                yield json.dumps({"content": buffer}) + "\n"

    except Exception:
        yield f'data: {json.dumps({"error": "Streaming service unavailable"})}\n\n'
        yield "data: [DONE]\n\n"


# ==============================
# API Endpoint
# ==============================

@app.post("/stream")
async def stream_endpoint(request: Request):
    # body = await request.json()
    try:
        body = await request.json()
    except Exception:
        body = {}

    if not body.get("stream", False):
        return {"error": "Streaming must be enabled (stream: true)"}

    prompt = body.get("prompt", "Generate article")

    return StreamingResponse(
        stream_generator(prompt),
        # media_type="text/event-stream",
        media_type="application/x-ndjson",
    )
