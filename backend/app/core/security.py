
import re
from datetime import datetime, timedelta
from typing import Optional, Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext
import bcrypt

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_password(password: str) -> str:
    """
    Truncate password to 72 bytes to comply with bcrypt limit.
    
    Args:
        password: Original password string
        
    Returns:
        Truncated password string (max 72 bytes)
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= 72:
        return password
    
    # Truncate to 72 bytes
    password_bytes = password_bytes[:72]
    
    # Remove any incomplete UTF-8 sequences at the end
    while len(password_bytes) > 0:
        try:
            return password_bytes.decode('utf-8')
        except UnicodeDecodeError:
            password_bytes = password_bytes[:-1]
    
    return ""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Note: bcrypt has a 72-byte limit. If password exceeds this, it will be truncated.
    """
    # Truncate password before verification to comply with bcrypt's 72-byte limit
    plain_password = _truncate_password(plain_password)
    
    # Use bcrypt directly to avoid passlib's internal checks
    try:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        # Fallback to passlib if direct bcrypt fails
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Note: bcrypt has a 72-byte limit. If password exceeds this, it will be truncated.
    """
    # Truncate password before hashing to comply with bcrypt's 72-byte limit
    password = _truncate_password(password)
    
    # Use bcrypt directly to avoid passlib's internal checks
    try:
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception:
        # Fallback to passlib if direct bcrypt fails
        return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_token_expiry_seconds(payload: dict) -> int:
    """
    Get remaining seconds until token expiry.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Remaining seconds until expiry, or 0 if already expired
    """
    exp = payload.get("exp")
    if not exp:
        return 0
    
    import time
    remaining = exp - int(time.time())
    return max(0, remaining)


def _get_token_hash(token: str) -> str:
    """
    Get hash of token for use as cache key.
    
    Args:
        token: JWT token string
        
    Returns:
        SHA256 hash of token
    """
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.
    
    Args:
        token: JWT token string
        
    Returns:
        True if token is blacklisted, False otherwise
    """
    try:
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        token_hash = _get_token_hash(token)
        blacklisted = await redis.get(f"token:blacklist:{token_hash}")
        return blacklisted is not None
    except Exception:
        # If Redis fails, assume token is not blacklisted (fail open)
        return False


async def blacklist_token(token: str, expires_in_seconds: int) -> bool:
    """
    Add a token to the blacklist.
    
    Args:
        token: JWT token string
        expires_in_seconds: Time in seconds until token expires (used as TTL)
        
    Returns:
        True if successfully blacklisted, False otherwise
    """
    try:
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        # Use token hash as key to avoid storing full token
        token_hash = _get_token_hash(token)
        await redis.set(f"token:blacklist:{token_hash}", "1", ex=expires_in_seconds)
        return True
    except Exception:
        # If Redis fails, log but don't fail the request
        return False


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength based on configuration.
    Requires:
    - Min length (settings.PASSWORD_MIN_LENGTH)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False
        
    if settings.PASSWORD_REQUIRE_COMPLEXITY:
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
            return False
            
    return True


def is_password_expired(password_updated_at: Optional[datetime]) -> bool:
    """Check if password has expired."""
    if not password_updated_at:
        # If never updated, assume expired if we want strict policy, 
        # or valid if we consider creation as update. 
        # Let's verify logic: newly created user usually sets password_updated_at = now
        return False # Or True depending on policy. Assuming False for graceful start.
        
    delta = datetime.utcnow() - password_updated_at
    return delta.days > settings.PASSWORD_EXPIRE_DAYS
