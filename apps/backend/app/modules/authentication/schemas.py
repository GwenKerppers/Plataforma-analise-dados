from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing import Annotated

FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class RegisterIn(BaseModel):
    email: EmailStr
    # Só comprimento (orientação do NIST): sem regras artificiais de composição.
    password: str = Field(min_length=12, max_length=128)
    full_name: FullName


class LoginIn(BaseModel):
    email: EmailStr
    # Sem mínimo no login, para não revelar a política; o máximo evita abuso de CPU.
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
