from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class GoogleUser(BaseModel):
    sub: str
    email: str
    name: str | None = None
    picture: str | None = None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_session),
) -> User:
    """Get current authenticated user from token and create if not exists."""
    import base64
    import json

    try:
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        claims = json.loads(decoded)
        google_sub = str(claims["sub"])
        email = str(claims["email"])
        name = claims.get("name")
        picture = claims.get("picture")

        # Look up or create user
        stmt = select(User).where(User.google_sub == google_sub)
        user = db.execute(stmt).scalar_one_or_none()

        if not user:
            user = User(
                google_sub=google_sub,
                email=email,
                full_name=name or email.split("@")[0],
                given_name=name.split(" ")[0] if name else None,
                family_name=" ".join(name.split(" ")[1:]) if name and " " in name else None,
                picture_url=picture,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=GoogleUser)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return the authenticated user's profile."""
    return GoogleUser(
        sub=str(current_user.google_sub),
        email=str(current_user.email),
        name=str(current_user.full_name) if current_user.full_name else None,
        picture=str(current_user.picture_url) if current_user.picture_url else None,
    )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Check if user is active."""
    if not bool(getattr(current_user, "is_active", True)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user
