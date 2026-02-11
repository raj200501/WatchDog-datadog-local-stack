from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..db import get_session
from ..deps import require_api_key
from ..models import SyntheticCheck, SyntheticResult
from ..schemas import SyntheticCheckIn

synthetics_router = APIRouter(prefix="/api/v1/synthetics", dependencies=[Depends(require_api_key)])


@synthetics_router.get("")
async def list_checks() -> list[dict]:
    with get_session() as session:
        checks = session.exec(select(SyntheticCheck)).all()
        return [check.model_dump() for check in checks]


@synthetics_router.post("")
async def create_check(payload: SyntheticCheckIn) -> dict:
    with get_session() as session:
        check = SyntheticCheck(**payload.model_dump())
        session.add(check)
        session.commit()
        session.refresh(check)
        return check.model_dump()


@synthetics_router.delete("/{check_id}")
async def delete_check(check_id: int) -> dict:
    with get_session() as session:
        check = session.get(SyntheticCheck, check_id)
        if not check:
            raise HTTPException(status_code=404, detail="check not found")
        session.delete(check)
        session.commit()
        return {"deleted": check_id}


@synthetics_router.get("/{check_id}/results")
async def list_results(check_id: int, limit: int = 20) -> list[dict]:
    with get_session() as session:
        results = session.exec(
            select(SyntheticResult)
            .where(SyntheticResult.check_id == check_id)
            .order_by(SyntheticResult.ts.desc())
            .limit(limit)
        ).all()
        return [result.model_dump() for result in results]
