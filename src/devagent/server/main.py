from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio

from starlette.staticfiles import StaticFiles

from ..agent.graph_agent import graph_agent
app = FastAPI(
    title="DevAgent API",
    description="代码仓库智能体后端接口",
    version="0.1.0"
)

app.mount("/static", StaticFiles(directory="src/devagent/server/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],       # 允许所有请求方法
    allow_headers=["*"],       # 允许所有请求头
)

class ChatRequest(BaseModel):
    query: str
    session_id: str

@app.post("/api/chat", summary="同步问答接口（一次性返回完整答案）")
def chat(request: ChatRequest):
    answer = graph_agent.run_with_session(request.query, request.session_id)

    return {
        "code": 200,
        "message": "success",
        "data":{
            "answer": answer
        }

    }


@app.get("/api/chat/stream", summary="流式问答接口")
async def stream(query:str):
    async def event_generator():
        yield {
            "event":"start",
            "data":"正在思考..."
        }
        await asyncio.sleep(0.1)

        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None,
            lambda : graph_agent.run(query),
        )

        for char in answer:
            yield char

        yield {
            "event":"end",
            "data":None
        }

    return EventSourceResponse(event_generator())




