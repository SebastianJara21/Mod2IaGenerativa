"""Security utilities for password hashing and JWT token management.

Per Artículo IV (Security - non-negotiable):
- Passwords: hash with passlib[bcrypt], NEVER store or log in plain text
- Tokens: JWT HS256 via pyjwt (single library choice, not python-jose)
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from app.config import settings

# Password hashing context (per Artículo IV.3 - passlib 1.7.4 + bcrypt<4.1)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Used during user registration. Plain password is never stored or logged.
    Args:
        password: Plain-text password from user
    Returns:
        Hashed password string (bcrypt format)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash.

    Used during authentication. Comparison is constant-time (prevents timing attacks).
    Args:
        plain_password: Plain-text password from user login attempt
        hashed_password: Hashed password from database
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token.

    Per Artículo IV.2: JWT signed with HS256, expiry configurable via .env,
    never infinite. Uses pyjwt (single maintained library).
    Per Artículo VIII (Compatibility): JWT payload should contain "sub" (email)
    following standard OAuth2 pattern.

    Args:
        data: Dict containing user info to encode (e.g., {'sub': 'user@example.com'})
        expires_delta: Optional custom expiry time; defaults to ACCESS_TOKEN_EXPIRE_MINUTES
    Returns:
        Signed JWT string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Sign with HS256 using SECRET_KEY from .env
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    Raises jwt.InvalidTokenError if token is expired, malformed, or signed with wrong key.
    Args:
        token: JWT token string
    Returns:
        Decoded payload dict (contains usuario_id, exp, etc.)
    Raises:
        jwt.InvalidTokenError: If token invalid or expired
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
