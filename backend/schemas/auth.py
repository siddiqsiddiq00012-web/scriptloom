from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    avatar_url: str | None = None
    bio: str | None = None
    company: str | None = None
    role: str | None = None
    timezone: str | None = None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProfileUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    company: str | None = None
    role: str | None = None
    timezone: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class GoogleAuthRequest(BaseModel):
    id_token: str | None = Field(None, description="Google OAuth ID Token")
    token: str | None = Field(None, description="Alternative field for Google OAuth ID Token")
    credential: str | None = Field(None, description="Google GIS credential response field")

    @property
    def get_token(self) -> str:
        tok = self.id_token or self.token or self.credential
        if not tok:
            raise ValueError("Google ID Token is required.")
        return tok