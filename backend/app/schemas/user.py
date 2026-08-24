from pydantic import BaseModel, EmailStr, Field


# ============================================================
# SIGNUP
# ============================================================

class UserSignup(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72
    )


# ============================================================
# LOGIN
# ============================================================

class UserLogin(BaseModel):

    email: EmailStr

    password: str


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    role: str

    email_verified: bool

    class Config:
        from_attributes = True


# ============================================================
# TOKEN RESPONSE
# ============================================================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str

    user: UserResponse


# ============================================================
# SIGNUP RESPONSE
# ============================================================

class SignupResponse(BaseModel):

    message: str

    email: EmailStr

    requires_verification: bool


# ============================================================
# VERIFY EMAIL OTP
# ============================================================

class VerifyEmailRequest(BaseModel):

    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6
    )


# ============================================================
# RESEND OTP
# ============================================================

class ResendOTPRequest(BaseModel):

    email: EmailStr


# ============================================================
# GENERIC MESSAGE RESPONSE
# ============================================================

class MessageResponse(BaseModel):

    message: str