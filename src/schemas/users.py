from pydantic import BaseModel, Field, validator
from typing import Optional, Literal


class UserBase(BaseModel):
    email: str
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class AdministratorCreate(UserBase):
    full_name: str
    role: Literal["administrator"] = "administrator"


class CourseCreatorCreate(UserBase):
    full_name: str
    role: Literal["course_creator"] = "course_creator"


class OrganizationCreate(UserBase):
    organization_name: str
    role: Literal["organization"] = "organization"


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    full_name: Optional[str] = None
    organization_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse