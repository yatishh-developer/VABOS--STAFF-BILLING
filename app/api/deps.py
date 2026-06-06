from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.db.database import get_session
from app.models.staff import StaffUser

bearer = HTTPBearer(auto_error=False)


async def get_current_staff(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> StaffUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        staff_id = int(payload['sub'])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token') from None
    staff = await session.get(StaffUser, staff_id)
    if staff is None or not staff.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Inactive staff')
    return staff
