from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme for Google OAuth
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes={
        "openid": "OpenID Connect",
        "email": "View your email address",
        "profile": "View your profile",
    },
)


class GoogleUser(BaseModel):
    sub: str
    email: str
    name: str | None = None
    picture: str | None = None


@router.get("/google/login")
def google_login():
    """Redirect user to Google OAuth consent screen."""
    # TODO: Generate OAuth URL with redirect_uri
    raise NotImplementedError


@router.get("/callback")
def oauth_callback(code: str):
    """Handle Google OAuth callback, exchange code for tokens."""
    # TODO: Exchange code for ID token, verify, create/lookup user
    raise NotImplementedError


@router.get("/me", response_model=GoogleUser)
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from token."""
    # TODO: Verify token, return user
    raise NotImplementedError
