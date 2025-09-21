"""
Authentication and authorization for {{cookiecutter.project_name}}.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from app.config import Settings, get_settings
from app.exceptions import UnauthorizedError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data
            
        Raises:
            UnauthorizedError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.JWTError:
            raise UnauthorizedError("Invalid token")
    
    def create_api_key(self, user_id: str, name: Optional[str] = None) -> str:
        """
        Create an API key for a user.
        
        Args:
            user_id: User identifier
            name: Optional name for the API key
            
        Returns:
            API key string
        """
        data = {
            "user_id": user_id,
            "type": "api_key",
            "name": name,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # API keys don't expire by default
        return self.create_access_token(data, expires_delta=timedelta(days=365))
    
    def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Verify an API key.
        
        Args:
            api_key: API key string
            
        Returns:
            API key data
            
        Raises:
            UnauthorizedError: If API key is invalid
        """
        payload = self.verify_token(api_key)
        
        if payload.get("type") != "api_key":
            raise UnauthorizedError("Invalid API key format")
        
        return payload


class SimpleAuthProvider:
    """Simple authentication provider for basic auth needs."""
    
    def __init__(self):
        self.users = {}  # In production, use a database
        self.api_keys = {}  # In production, use a database
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User data if authenticated, None otherwise
        """
        if username not in self.users:
            return None
        
        user_data = self.users[username]
        auth_manager = AuthManager(get_settings())
        
        if not auth_manager.verify_password(password, user_data["password_hash"]):
            return None
        
        return {
            "user_id": user_data["user_id"],
            "username": username,
            "email": user_data.get("email"),
            "is_active": user_data.get("is_active", True)
        }
    
    async def create_user(
        self, 
        username: str, 
        password: str, 
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: Username
            password: Plain password
            email: Optional email
            
        Returns:
            User data
        """
        auth_manager = AuthManager(get_settings())
        user_id = f"user_{len(self.users) + 1}"
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": auth_manager.get_password_hash(password),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.users[username] = user_data
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "is_active": True
        }
    
    async def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify an API key.
        
        Args:
            api_key: API key string
            
        Returns:
            API key data if valid, None otherwise
        """
        try:
            auth_manager = AuthManager(get_settings())
            payload = auth_manager.verify_api_key(api_key)
            return payload
        except UnauthorizedError:
            return None


# Global auth provider instance
_auth_provider: Optional[SimpleAuthProvider] = None


def get_auth_provider() -> SimpleAuthProvider:
    """Get the global auth provider instance."""
    global _auth_provider
    if _auth_provider is None:
        _auth_provider = SimpleAuthProvider()
    return _auth_provider
