from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from api.schema.Agent import ChatRequest
from api.dependencies import agentServiceDep
from service.AgentService import AgentService

router=APIRouter(prefix="/agent",tags=["Agent"])

@router.post("/chat")
async def chat(request:ChatRequest,agent_service:agentServiceDep):
    return StreamingResponse(agent_service.stream_chat(request.message,request.history), media_type="text/event-stream")