from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class GoogleUser(BaseModel):
    sub: str
    email: str
    name: str | None = None
    picture: str | None = None


@router.get("/me", response_model=GoogleUser)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    """Get current authenticated user from token."""
    # TODO: Verify JWT with Google's public keys
    # For now, decode basic claims
    import base64
    import json

    try:
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        claims = json.loads(decoded)
        return GoogleUser(sub=claims["sub"], email=claims["email"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: Annotated[GoogleUser, Depends(get_current_user)],
):
    """Check if user is active."""
    if current_user.email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user
