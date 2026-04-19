"""
AMOS LLM API

REST API endpoints for LLM operations.
Supports chat completion, streaming, and provider management.

Creator: Trang Phan
Version: 3.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..llm_providers import LLMRequest, Message, llm_router
from .schemas import ChatRequest, ChatResponse, ProviderInfo, ProvidersResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Send a chat completion request to the best available LLM.

    Automatically routes to local Ollama (if available) or cloud providers.
    """
    try:
        llm_request = LLMRequest(
            messages=[
                Message(role=m.role, content=m.content, metadata=m.metadata)
                for m in request.messages
            ],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )

        response = await llm_router.route_request(llm_request, preference=request.provider)

        return ChatResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            usage=response.usage,
            latency_ms=response.latency_ms,
            timestamp=response.timestamp,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat completion response token by token.

    Returns Server-Sent Events (SSE) stream.
    """

    async def generate():
        try:
            llm_request = LLMRequest(
                messages=[
                    Message(role=m.role, content=m.content, metadata=m.metadata)
                    for m in request.messages
                ],
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )

            async for chunk in llm_router.route_stream(llm_request, preference=request.provider):
                yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: ERROR: {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/providers", response_model=ProvidersResponse)
async def list_providers():
    """List all available LLM providers and their models."""
    providers = llm_router.get_available_providers()
    return ProvidersResponse(providers=[ProviderInfo(**p) for p in providers])


@router.get("/models")
async def list_models(provider: str = Query(None, description="Filter by provider")):
    """List available models, optionally filtered by provider."""
    providers = llm_router.get_available_providers()

    if provider:
        for p in providers:
            if p["name"] == provider:
                return {"provider": provider, "models": p["models"]}
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")

    # Return all models grouped by provider
    all_models = {}
    for p in providers:
        all_models[p["name"]] = p["models"]

    return {"models_by_provider": all_models}
