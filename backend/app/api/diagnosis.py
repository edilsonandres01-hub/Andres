"""Diagnosis API Routes v2.0.0"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.services.diagnosis_service import diagnosis_service

router = APIRouter(prefix="/api/v1/diagnosis", tags=["diagnosis"])


class DiagnosisRequest(BaseModel):
    video_id: Optional[str] = None
    input_data: Dict[str, Any] = Field(...)
    context: Optional[Dict[str, Any]] = None


@router.post("/")
async def create_diagnosis(req: DiagnosisRequest):
    try:
        return await diagnosis_service.create(req.video_id, req.input_data, req.context)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Diagnosis failed: {e}")


@router.get("/health")
async def health():
    return diagnosis_service.health()


@router.get("/stats")
async def stats():
    return diagnosis_service.stats()


@router.get("/taxonomy")
async def taxonomy():
    return diagnosis_service.taxonomy()


@router.get("/rules")
async def rules(category: str = None):
    return diagnosis_service.rules(category)
