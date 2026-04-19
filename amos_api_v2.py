"""AMOS API v2.0 - REST Endpoints for New Engines."""

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from amos_engine_integration import EngineOperation, EngineType, get_engine_integration

app = FastAPI(title="AMOS API v2.0", version="2.0.0")


class TemporalRequest(BaseModel):
    operation: str
    params: Dict[str, Any] = {}


class FieldRequest(BaseModel):
    grid_size: int = 64
    steps: int = 100
    mass: float = 1.0


class SafetyRequest(BaseModel):
    code: str
    test_code: str = ""
    evidence: Dict[str, Any] = {}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/engines/temporal")
async def temporal_endpoint(req: TemporalRequest) -> Dict[str, Any]:
    engine = get_engine_integration()
    op = EngineOperation(EngineType.TEMPORAL, req.operation, req.params)
    result = await engine.execute(op)
    if not result.success:
        raise HTTPException(400, detail=result.errors)
    return result.data


@app.post("/engines/field/simulate")
async def field_endpoint(req: FieldRequest) -> Dict[str, Any]:
    engine = get_engine_integration()
    op = EngineOperation(EngineType.FIELD, "simulate", req.__dict__)
    result = await engine.execute(op)
    return result.data


@app.post("/engines/safety/validate")
async def safety_endpoint(req: SafetyRequest) -> Dict[str, Any]:
    engine = get_engine_integration()
    op = EngineOperation(EngineType.SAFETY, "validate", req.__dict__)
    result = await engine.execute(op)
    return result.data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
