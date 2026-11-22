from fastapi import FastAPI
from wdp.api.v1.router import router as v1_router

app = FastAPI()
app.include_router(v1_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
