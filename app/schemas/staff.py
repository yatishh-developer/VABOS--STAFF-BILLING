from datetime import datetime
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class LoginRequest(BaseModel):
    username: str
    password: str


class StaffLoginRequest(BaseModel):
    loginId: str
    password: str


class StaffSignupRequest(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8)
    phone: str = ''
    businessId: str = 'test_business'
    branchId: str = 'test_branch'
    role: str = 'cashier'


class StaffUserOut(BaseModel):
    id: int
    business_id: str
    branch_id: str
    name: str
    phone: str
    email: str
    role: str
    active: bool

    model_config = {'from_attributes': True}


class StaffCreate(BaseModel):
    business_id: str
    branch_id: str = ''
    name: str
    phone: str
    email: str = ''
    password: str = Field(min_length=6)
    role: str = 'staff'


class AttendanceCreate(BaseModel):
    event_type: str = Field(pattern='^(check_in|check_out)$')
    note: str = ''


class AttendanceOut(BaseModel):
    id: int
    staff_id: int
    event_type: str
    note: str
    created_at: datetime

    model_config = {'from_attributes': True}


class TaskCreate(BaseModel):
    title: str
    description: str = ''
    staff_id: int | None = None
    business_id: str
    branch_id: str = ''
    priority: str = 'normal'


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    staff_id: int | None

    model_config = {'from_attributes': True}


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    read: bool
    created_at: datetime

    model_config = {'from_attributes': True}
