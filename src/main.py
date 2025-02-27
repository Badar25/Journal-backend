from fastapi import FastAPI
from .api.v1.router import router as v1_router

app = FastAPI(title="Journal AI App", version="0.1.0")
app.include_router(v1_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Journal AI"}