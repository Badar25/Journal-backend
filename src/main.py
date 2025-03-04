from fastapi import FastAPI, Request
from .api.v1.router import router as v1_router
from .core.firebase import AuthError
from .models.response import APIResponse
from fastapi.responses import JSONResponse
from .core.cleanup import cleanup_old_journals
import asyncio

app = FastAPI(title="Journal AI App", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    # Start the cleanup task in the background
    asyncio.create_task(cleanup_old_journals())

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=401,
        content=APIResponse(
            success=False,
            message=exc.message,
            error=exc.error
        ).dict()
    )

app.include_router(v1_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Journal AI"}
