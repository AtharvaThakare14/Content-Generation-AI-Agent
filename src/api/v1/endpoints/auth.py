import sys
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.schemas.users import (
    AdministratorCreate, 
    CourseCreatorCreate, 
    OrganizationCreate, 
    UserResponse,
    TokenResponse,
    LoginRequest
)
from src.components.auth import AuthComponent
from src.exception import CustomException
from src.logging import logging

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Initialize the auth component
auth_component = AuthComponent()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current authenticated user from the JWT token"""
    try:
        # Decode JWT token and get user ID
        from jose import jwt, JWTError
        from src.components.auth import SECRET_KEY, ALGORITHM
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        # Get user from Supabase
        user = auth_component.get_user_by_id(user_id)
        return UserResponse(
            id=user["id"],
            email=user["email"],
            role=user["role"],
            full_name=user.get("full_name"),
            organization_name=user.get("organization_name")
        )
    except Exception as e:
        logging.error(f"Error getting current user: {e}")
        raise CustomException(e, sys)


async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)):
    """Check if the current user is active"""
    return current_user


@router.post("/register/administrator", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_administrator(user_data: AdministratorCreate):
    """Register a new administrator"""
    try:
        logging.info(f"Registering new administrator: {user_data.email}")
        return auth_component.register_administrator(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
    except Exception as e:
        logging.error(f"Error in register_administrator endpoint: {e}")
        raise CustomException(e, sys)


@router.post("/register/course-creator", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_course_creator(user_data: CourseCreatorCreate):
    """Register a new course creator"""
    try:
        logging.info(f"Registering new course creator: {user_data.email}")
        return auth_component.register_course_creator(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
    except Exception as e:
        logging.error(f"Error in register_course_creator endpoint: {e}")
        raise CustomException(e, sys)


@router.post("/register/organization", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_organization(user_data: OrganizationCreate):
    """Register a new organization"""
    try:
        logging.info(f"Registering new organization: {user_data.email}")
        return auth_component.register_organization(
            email=user_data.email,
            password=user_data.password,
            organization_name=user_data.organization_name
        )
    except Exception as e:
        logging.error(f"Error in register_organization endpoint: {e}")
        raise CustomException(e, sys)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Login endpoint to authenticate users and get access token"""
    try:
        logging.info(f"Login attempt for user: {login_data.email}")
        result = auth_component.login(
            email=login_data.email,
            password=login_data.password
        )
        return TokenResponse(**result)
    except Exception as e:
        logging.error(f"Error in login endpoint: {e}")
        raise CustomException(e, sys)


@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user profile"""
    try:
        logging.info(f"Getting profile for user: {current_user.email}")
        return current_user
    except Exception as e:
        logging.error(f"Error in get_user_profile endpoint: {e}")
        raise CustomException(e, sys)