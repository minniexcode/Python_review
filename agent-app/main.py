import json
import traceback
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from utils.config import settings
from graph.email_graph import build_email_graph

app = FastAPI(
    title="Agent App FastAPI",
    description="A FastAPI application for handling customer emails using a state graph agent.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    """验证 X-API-Key 请求头。"""
    if not settings.app_api_key or x_api_key != settings.app_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")


email_app = build_email_graph()

@app.post("/chat/stream", summary="chat with agent (streaming)", dependencies=[Depends(verify_api_key)])
async def chat_stream(request: Request) -> JSONResponse:
    payload = await request.json()
    graph = payload.get("graph", "email")
    email_content = payload.get("email_content", "")
    # Placeholder for streaming response logic
    if graph == "email":
        email_id = payload.get("email_id") or str(uuid.uuid4())
        sender_email = payload.get("sender_email", "unknown@example.com")
        thread_id = payload.get("thread_id") or email_id

        output = email_app.invoke(
            {
                "email_content": email_content,
                "sender_email": sender_email,
                "email_id": email_id,
                "messages": [],
            },
            config={"configurable": {"thread_id": thread_id}},
        )

        interrupts = output.get("__interrupt__", [])
        interrupt_payloads = [item.value for item in interrupts]
        return JSONResponse(
            content={
                "message": "This endpoint will stream responses from the agent.",
                "output": {k: v for k, v in output.items() if k != "__interrupt__"},
                "interrupted": bool(interrupt_payloads),
                "interrupts": interrupt_payloads,
            }
        )
    
    return JSONResponse(content={"message": "This endpoint will stream responses from the agent."})


@app.get("/health", summary="health check")
async def health() -> dict:
    return {"status": "ok", "version": "1.0.0"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_id = str(uuid.uuid4())
    error_trace = traceback.format_exc()
    print(f"Error ID: {error_id}\n{error_trace}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
