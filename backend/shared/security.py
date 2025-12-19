"""
Security utilities for JWT handling and password hashing.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from pydantic import ValidationError

from .schemas import TokenPayload, UserRole


class SecurityManager:
    """JWT and password security manager."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    # Password hashing
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            plain_password.encode(),
            hashed_password.encode(),
        )
    
    # JWT Token creation
    def create_access_token(
        self,
        user_id: int,
        email: str,
        role: UserRole,
    ) -> str:
        """Create JWT access token."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role.value,
            "exp": expire,
            "iat": now,
            "type": "access",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(
        self,
        user_id: int,
        email: str,
        role: UserRole,
    ) -> str:
        """Create JWT refresh token."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role.value,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> TokenPayload | None:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return TokenPayload(
                sub=payload["sub"],
                email=payload["email"],
                role=UserRole(payload["role"]),
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
                type=payload["type"],
            )
        except (JWTError, ValidationError, KeyError):
            return None
    
    def create_token_pair(
        self,
        user_id: int,
        email: str,
        role: UserRole,
    ) -> tuple[str, str]:
        """Create access and refresh token pair."""
        access_token = self.create_access_token(user_id, email, role)
        refresh_token = self.create_refresh_token(user_id, email, role)
        return access_token, refresh_token
