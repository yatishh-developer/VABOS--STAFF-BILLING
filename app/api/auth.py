from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import ensure_database_schema, get_session
from app.models.staff import StaffUser
from app.schemas.staff import (
    LoginRequest,
    StaffCreate,
    StaffLoginRequest,
    StaffSignupRequest,
    StaffUserOut,
    TokenResponse,
)
from app.services.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])


def _staff_payload(staff: StaffUser) -> dict:
    return {
        'staffId': str(staff.id),
        'staffName': staff.name,
        'businessId': staff.business_id,
        'branchId': staff.branch_id,
        'counterId': None,
        'role': staff.role,
        'permissions': {
            'canCreateKot': True,
            'canConvertKotToBill': True,
            'canCollectPayment': True,
            'canPrintBill': True,
            'canCancelKot': staff.role in {'admin', 'manager', 'cashier'},
            'canViewOwnBillsOnly': staff.role not in {'admin', 'manager'},
        },
    }


def _auth_response(staff: StaffUser) -> dict:
    token = create_access_token(
        str(staff.id),
        {
            'business_id': staff.business_id,
            'branch_id': staff.branch_id,
            'role': staff.role,
        },
    )
    return {
        'accessToken': token,
        'refreshToken': token,
        'staff': _staff_payload(staff),
    }


@router.post('/register', response_model=StaffUserOut)
async def register(payload: StaffCreate, session: AsyncSession = Depends(get_session)):
    await ensure_database_schema()
    existing = await session.scalar(
        select(StaffUser).where(or_(StaffUser.phone == payload.phone, StaffUser.email == str(payload.email)))
        .where(StaffUser.business_id == payload.business_id)
        .where(StaffUser.deleted_at.is_(None))
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
        created_by=payload.email or payload.phone,
        updated_by=payload.email or payload.phone,
    )
    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    return staff


@router.post('/login', response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    await ensure_database_schema()
    staff = await session.scalar(
        select(StaffUser).where(or_(StaffUser.phone == payload.username, StaffUser.email == payload.username))
        .where(StaffUser.deleted_at.is_(None))
    )
    if staff is None or not verify_password(payload.password, staff.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    token = create_access_token(str(staff.id), {'business_id': staff.business_id, 'role': staff.role})
    return TokenResponse(access_token=token)


@router.post('/staff/login')
async def staff_login(payload: StaffLoginRequest, session: AsyncSession = Depends(get_session)) -> dict:
    await ensure_database_schema()
    staff = await session.scalar(
        select(StaffUser).where(or_(StaffUser.phone == payload.loginId, StaffUser.email == payload.loginId))
        .where(StaffUser.deleted_at.is_(None))
    )
    if staff is None or not verify_password(payload.password, staff.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return _auth_response(staff)


@router.post('/staff/signup')
async def staff_signup(payload: StaffSignupRequest, session: AsyncSession = Depends(get_session)) -> dict:
    await ensure_database_schema()
    phone = payload.phone or payload.email
    existing = await session.scalar(
        select(StaffUser).where(or_(StaffUser.phone == phone, StaffUser.email == payload.email))
        .where(StaffUser.business_id == payload.businessId)
        .where(StaffUser.deleted_at.is_(None))
    )
    if existing:
        raise HTTPException(status_code=409, detail='Staff already exists')
    staff = StaffUser(
        business_id=payload.businessId,
        branch_id=payload.branchId,
        name=payload.name,
        phone=phone,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        created_by=payload.email,
        updated_by=payload.email,
    )
    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    return _auth_response(staff)


@router.post('/forgot-password')
async def forgot_password() -> dict[str, str]:
    return {'status': 'pending', 'message': 'Password reset provider is not configured yet.'}


@router.post('/reset-password')
async def reset_password() -> dict[str, str]:
    return {'status': 'pending', 'message': 'Password reset provider is not configured yet.'}


@router.post('/logout')
async def logout() -> dict[str, str]:
    return {'status': 'ok'}
