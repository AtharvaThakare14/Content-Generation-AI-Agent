import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.exception import CustomException
from src.logging import logging
from src.configurations.supabase import SupabaseConnection
from src.schemas.users import UserResponse

# JWT Configuration
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # Should be stored in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthComponent:
    def __init__(self):
        try:
            self.supabase_conn = SupabaseConnection()
            self.supabase = self.supabase_conn.connect()
        except Exception as e:
            raise CustomException(e, sys)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if the provided password matches the hashed password"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logging.error(f"Error verifying password: {e}")
            raise CustomException(e, sys)

    def get_password_hash(self, password: str) -> str:
        """Hash a password for storing"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logging.error(f"Error hashing password: {e}")
            raise CustomException(e, sys)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logging.error(f"Error creating access token: {e}")
            raise CustomException(e, sys)

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID from Supabase"""
        try:
            user_data = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not user_data.data or len(user_data.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return user_data.data[0]
        except Exception as e:
            logging.error(f"Error getting user by ID: {e}")
            raise CustomException(e, sys)

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email from Supabase"""
        try:
            user_data = self.supabase.table("users").select("*").eq("email", email).execute()
            
            if not user_data.data or len(user_data.data) == 0:
                return None
            
            return user_data.data[0]
        except Exception as e:
            logging.error(f"Error getting user by email: {e}")
            raise CustomException(e, sys)

    def register_administrator(self, email: str, password: str, full_name: str) -> UserResponse:
        """Register a new administrator"""
        try:
            logging.info(f"Registering new administrator: {email}")
            return self.register_user(
                email=email,
                password=password,
                role="administrator",
                full_name=full_name
            )
        except Exception as e:
            logging.error(f"Error registering administrator: {e}")
            raise CustomException(e, sys)

    def register_course_creator(self, email: str, password: str, full_name: str) -> UserResponse:
        """Register a new course creator"""
        try:
            logging.info(f"Registering new course creator: {email}")
            return self.register_user(
                email=email,
                password=password,
                role="course_creator",
                full_name=full_name
            )
        except Exception as e:
            logging.error(f"Error registering course creator: {e}")
            raise CustomException(e, sys)

    def register_organization(self, email: str, password: str, organization_name: str) -> UserResponse:
        """Register a new organization"""
        try:
            logging.info(f"Registering new organization: {email}")
            return self.register_user(
                email=email,
                password=password,
                role="organization",
                organization_name=organization_name
            )
        except Exception as e:
            logging.error(f"Error registering organization: {e}")
            raise CustomException(e, sys)

    def register_user(self, email: str, password: str, role: str, full_name: Optional[str] = None, organization_name: Optional[str] = None) -> UserResponse:
        """Register a new user in Supabase"""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            # Create user data
            user_data = {
                "email": email,
                "password": self.get_password_hash(password),
                "role": role,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Add role-specific fields
            if role == "administrator" or role == "course_creator":
                user_data["full_name"] = full_name
            elif role == "organization":
                user_data["organization_name"] = organization_name
            
            # Insert user into Supabase
            result = self.supabase.table("users").insert(user_data).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            created_user = result.data[0]
            logging.info(f"Successfully registered user: {email} with role: {role}")
            
            return UserResponse(
                id=created_user["id"],
                email=created_user["email"],
                role=created_user["role"],
                full_name=created_user.get("full_name"),
                organization_name=created_user.get("organization_name")
            )
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise e
        except Exception as e:
            logging.error(f"Error registering user: {e}")
            raise CustomException(e, sys)

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and return user data"""
        try:
            # Get user from Supabase
            user = self.get_user_by_email(email)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify password
            if not self.verify_password(password, user["password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logging.info(f"User authenticated successfully: {email}")
            return user
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise e
        except Exception as e:
            logging.error(f"Error authenticating user: {e}")
            raise CustomException(e, sys)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and return access token and user data"""
        try:
            # Authenticate user
            user = self.authenticate_user(email, password)
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user["id"]},
                expires_delta=access_token_expires
            )
            
            logging.info(f"Login successful for user: {email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse(
                    id=user["id"],
                    email=user["email"],
                    role=user["role"],
                    full_name=user.get("full_name"),
                    organization_name=user.get("organization_name")
                )
            }
        except Exception as e:
            logging.error(f"Error during login: {e}")
            raise CustomException(e, sys)
