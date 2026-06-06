import asyncio
import os

from sqlalchemy import or_, select

from app.db.database import AsyncSessionLocal
from app.models.staff import StaffUser
from app.services.security import hash_password


async def main() -> None:
    email = os.getenv('TEST_STAFF_EMAIL', 'test@vriddhi.app')
    password = os.getenv('TEST_STAFF_PASSWORD', 'Test@12345')
    name = os.getenv('TEST_STAFF_NAME', 'Test Staff')
    business_id = os.getenv('TEST_BUSINESS_ID', 'test_business')
    branch_id = os.getenv('TEST_BRANCH_ID', 'test_branch')
    role = os.getenv('TEST_STAFF_ROLE', 'cashier')

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(
            select(StaffUser).where(
                or_(StaffUser.email == email, StaffUser.phone == email),
            ),
        )
        if existing is not None:
            existing.name = name
            existing.business_id = business_id
            existing.branch_id = branch_id
            existing.role = role
            existing.hashed_password = hash_password(password)
            existing.active = True
            print(f'Updated test staff: {email}')
        else:
            session.add(
                StaffUser(
                    business_id=business_id,
                    branch_id=branch_id,
                    name=name,
                    phone=email,
                    email=email,
                    hashed_password=hash_password(password),
                    role=role,
                    active=True,
                ),
            )
            print(f'Created test staff: {email}')
        await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
