"""
Osmosis Session Routes

Conversational agent that helps users synthesize knowledge into daily life.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from core.agent import run_agent_turn

router = APIRouter(prefix="/api/osmosis", tags=["osmosis"])


class SessionMessage(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None


class ChatRequest(BaseModel):
    conversation: List[SessionMessage]
    message: str


@router.post("/chat")
async def osmosis_chat(request: ChatRequest):
    """Send a message in an osmosis session. Agent may use tools before responding."""
    try:
        # Convert to dicts for the agent
        conversation = []
        for msg in request.conversation:
            entry: Dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                entry["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            conversation.append(entry)

        result = await run_agent_turn(conversation, request.message)

        response: Dict[str, Any] = {
            "success": True,
            "message": result.content,
        }
        if result.options:
            response["options"] = result.options

        return JSONResponse(response)

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
