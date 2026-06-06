from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.models.staff import StaffUser
from app.schemas.staff import LoginRequest, StaffCreate, StaffUserOut, TokenResponse
from app.services.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=StaffUserOut)
async def register(payload: StaffCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.scalar(
        select(StaffUser).where(or_(StaffUser.phone == payload.phone, StaffUser.email == str(payload.email)))
    )
    if existing:
        raise HTTPException(status_code=409, detail='Staff already exists')
    staff = StaffUser(
        business_id=payload.business_id,
        branch_id=payload.branch_id,
        name=payload.name,
        phone=payload.phone,
        email=str(payload.email),
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    return staff


@router.post('/login', response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    staff = await session.scalar(
        select(StaffUser).where(or_(StaffUser.phone == payload.username, StaffUser.email == payload.username))
    )
    if staff is None or not verify_password(payload.password, staff.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    token = create_access_token(str(staff.id), {'business_id': staff.business_id, 'role': staff.role})
    return TokenResponse(access_token=token)
