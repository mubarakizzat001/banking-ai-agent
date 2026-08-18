import json
from collections.abc import AsyncIterator

from agent.agent import create_banking_agent
from api.schema.Agent import ChatMessage


def format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


class AgentService:
    def __init__(self, auth_headers: dict, customer_name: str):
        self._auth_headers = auth_headers
        self._customer_name = customer_name
        self._agent = None

    async def _ensure_agent(self):
        if self._agent is None:
            self._agent = await create_banking_agent(
                self._auth_headers, self._customer_name
            )
        return self._agent

    async def stream_chat(
        self, message: str, history: list[ChatMessage]
    ) -> AsyncIterator[str]:
        agent = await self._ensure_agent()
        messages = [m.model_dump() for m in history] + [
            {"role": "user", "content": message}
        ]
        try:
            async for stream_mode, chunk in agent.astream(
                {"messages": messages}, stream_mode=["messages", "updates"]
            ):
                async for event in self._handle_chunk(stream_mode, chunk):
                    yield event
        except Exception as exc:
            yield format_sse("error", {"detail": str(exc)})
        finally:
            yield "event: done\ndata: [DONE]\n\n"

    async def _handle_chunk(self, stream_mode: str, chunk) -> AsyncIterator[str]:
        if stream_mode == "messages":
            message_chunk, _metadata = chunk
            is_tool_call = bool(getattr(message_chunk, "tool_calls", None))
            is_ai_chunk = message_chunk.type in ("ai", "AIMessageChunk")
            if is_ai_chunk and message_chunk.content and not is_tool_call:
                yield format_sse("token", {"content": message_chunk.content})

        elif stream_mode == "updates":
            for node_name, node_output in chunk.items():
                for message in node_output.get("messages", []):
                    if node_name == "model" and getattr(message, "tool_calls", None):
                        for call in message.tool_calls:
                            yield format_sse(
                                "tool_call", {"name": call["name"], "args": call["args"]}
                            )
                    elif node_name == "tools":
                        yield format_sse(
                            "tool_result",
                            {"name": message.name, "content": message.content},
                        )