from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_staff
from app.db.database import get_session
from app.db.tenant import tenant_filter
from app.models.staff import StaffTask, StaffUser
from app.schemas.staff import TaskCreate, TaskOut

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.post('', response_model=TaskOut)
async def create_task(
    payload: TaskCreate,
    staff: StaffUser = Depends(get_current_staff),
    session: AsyncSession = Depends(get_session),
):
    task = StaffTask(
        **payload.model_dump(exclude={'business_id', 'branch_id'}),
        business_id=staff.business_id,
        branch_id=staff.branch_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.get('', response_model=list[TaskOut])
async def list_tasks(
    staff: StaffUser = Depends(get_current_staff),
    session: AsyncSession = Depends(get_session),
):
    rows = await session.scalars(
        tenant_filter(
            select(StaffTask),
            StaffTask,
            business_id=staff.business_id,
            branch_id=staff.branch_id,
        )
        .where(or_(StaffTask.staff_id == staff.id, StaffTask.staff_id.is_(None)))
        .order_by(StaffTask.created_at.desc())
    )
    return list(rows)
