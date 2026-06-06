from fastapi import APIRouter, Depends

from app.api.deps import get_current_staff
from app.models.staff import StaffUser

router = APIRouter(prefix='/staff', tags=['staff'])


def staff_payload(staff: StaffUser) -> dict:
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


@router.get('/me')
async def me(staff: StaffUser = Depends(get_current_staff)) -> dict:
    return staff_payload(staff)


@router.get('/menu')
async def menu(staff: StaffUser = Depends(get_current_staff)) -> dict:
    return {
        'businessId': staff.business_id,
        'branchId': staff.branch_id,
        'categories': [],
        'products': [],
    }


@router.get('/kots')
async def kots(staff: StaffUser = Depends(get_current_staff)) -> list:
    return []


@router.get('/bills')
async def bills(staff: StaffUser = Depends(get_current_staff)) -> list:
    return []


@router.post('/sync/batch')
async def sync_batch(staff: StaffUser = Depends(get_current_staff)) -> dict:
    return {'results': []}


@router.get('/sync/pull')
async def sync_pull(staff: StaffUser = Depends(get_current_staff)) -> dict:
    return {'events': [], 'serverTime': None}
