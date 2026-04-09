import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=2000)
    turnstile_token: str = Field(min_length=1, max_length=2048)

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_control_characters(cls, v: object) -> object:
        """
        Strip C0 control characters before Field length constraints run.
        """
        if isinstance(v, str):
            return re.sub(r"[\r\n\x00-\x1f\x7f]", "", v)
        return v
