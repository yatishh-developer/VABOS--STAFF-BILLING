from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_staff
from app.db.database import get_session
from app.db.tenant import tenant_filter
from app.models.staff import StaffNotification, StaffUser
from app.schemas.staff import NotificationOut

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('', response_model=list[NotificationOut])
async def list_notifications(
    staff: StaffUser = Depends(get_current_staff),
    session: AsyncSession = Depends(get_session),
):
    rows = await session.scalars(
        tenant_filter(
            select(StaffNotification),
            StaffNotification,
            business_id=staff.business_id,
            branch_id=staff.branch_id,
        )
        .where(or_(StaffNotification.staff_id == staff.id, StaffNotification.staff_id.is_(None)))
        .order_by(StaffNotification.created_at.desc())
    )
    return list(rows)
