from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_staff
from app.db.database import get_session
from app.db.tenant import tenant_filter
from app.models.staff import AttendanceEntry, StaffUser
from app.schemas.staff import AttendanceCreate, AttendanceOut

router = APIRouter(prefix='/attendance', tags=['attendance'])


@router.post('', response_model=AttendanceOut)
async def create_attendance(
    payload: AttendanceCreate,
    staff: StaffUser = Depends(get_current_staff),
    session: AsyncSession = Depends(get_session),
):
    entry = AttendanceEntry(
        staff_id=staff.id,
        business_id=staff.business_id,
        branch_id=staff.branch_id,
        event_type=payload.event_type,
        note=payload.note,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.get('', response_model=list[AttendanceOut])
async def list_attendance(
    staff: StaffUser = Depends(get_current_staff),
    session: AsyncSession = Depends(get_session),
):
    rows = await session.scalars(
        tenant_filter(
            select(AttendanceEntry),
            AttendanceEntry,
            business_id=staff.business_id,
            branch_id=staff.branch_id,
        )
        .where(AttendanceEntry.staff_id == staff.id)
        .order_by(AttendanceEntry.created_at.desc())
    )
    return list(rows)
