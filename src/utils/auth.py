from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.configurations.supabase import SupabaseConnection
from src.schemas.users import UserResponse

# JWT Configuration
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # Should be stored in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Supabase connection
supabase_conn = SupabaseConnection()


def verify_password(plain_password, hashed_password):
    """Verify if the provided password matches the hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password for storing"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current authenticated user from the JWT token"""
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
    supabase = supabase_conn.connect()
    user_data = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if not user_data.data or len(user_data.data) == 0:
        raise credentials_exception
    
    user = user_data.data[0]
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        full_name=user.get("full_name"),
        organization_name=user.get("organization_name")
    )


async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)):
    """Check if the current user is active"""
    return current_user


async def register_user(email: str, password: str, role: str, full_name: Optional[str] = None, organization_name: Optional[str] = None):
    """Register a new user in Supabase"""
    supabase = supabase_conn.connect()
    
    # Check if user already exists
    existing_user = supabase.table("users").select("*").eq("email", email).execute()
    if existing_user.data and len(existing_user.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user data
    user_data = {
        "email": email,
        "password": get_password_hash(password),
        "role": role,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Add role-specific fields
    if role == "administrator" or role == "course_creator":
        user_data["full_name"] = full_name
    elif role == "organization":
        user_data["organization_name"] = organization_name
    
    # Insert user into Supabase
    result = supabase.table("users").insert(user_data).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    created_user = result.data[0]
    return UserResponse(
        id=created_user["id"],
        email=created_user["email"],
        role=created_user["role"],
        full_name=created_user.get("full_name"),
        organization_name=created_user.get("organization_name")
    )