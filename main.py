import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

ARTICLE = """
Renewable energy is rapidly transforming the global power landscape. According to the International Energy Agency, renewables accounted for nearly 30% of global electricity generation in 2023, a figure expected to rise sharply over the next decade. “Clean energy is no longer an alternative,” notes an IEA report, “it is becoming the backbone of modern economies.”

Solar and wind energy lead this transition. The cost of solar photovoltaics has dropped by more than 85% since 2010, while onshore wind costs have fallen by nearly 60%. These dramatic reductions have made renewables competitive with fossil fuels even without subsidies. Countries like Germany and India now deploy gigawatts of renewable capacity annually.

Beyond cost, renewables offer resilience and security. Unlike fossil fuels, sunlight and wind are immune to geopolitical shocks. A 2022 World Bank study estimated that renewable adoption could reduce energy-import dependency by up to 70% in some regions.

Energy storage and smart grids further enhance reliability. Lithium-ion battery prices have declined 89% since 2010, enabling round-the-clock clean power. “The grid of the future will be digital, decentralized, and decarbonized,” says energy analyst Fatih Birol.

Renewable energy also delivers environmental and health benefits. The World Health Organization links air pollution to seven million premature deaths annually, many caused by fossil fuel combustion. Transitioning to clean energy reduces emissions while creating millions of jobs worldwide.

As climate urgency grows, renewable energy is no longer optional—it is essential.
""".strip()

def chunk_text(text: str, chunks: int = 8):
    size = len(text) // chunks
    return [text[i:i+size] for i in range(0, len(text), size)]

@app.post("/stream")
async def stream(request: Request):
    body = await request.json()
    if not body.get("stream"):
        return {"error": "stream must be true"}

    async def event_generator():
        try:
            chunks = chunk_text(ARTICLE, chunks=8)

            # Send chunks progressively
            for chunk in chunks:
                data = {
                    "choices": [
                        {"delta": {"content": chunk}}
                    ]
                }
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(0.05)  # ensures multiple flushes

            yield "data: [DONE]\n\n"

        except Exception as e:
            err = {"error": str(e)}
            yield f"data: {json.dumps(err)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )