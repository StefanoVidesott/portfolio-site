import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=2000)
    turnstile_token: str = Field(min_length=1, max_length=2048)

    @field_validator("name", mode="before")
    @classmethod
    def strip_control_characters(cls, v: object) -> object:
        """
        Strip C0 control characters before Field length constraints run.
        Name lands in the email Subject header, so newlines must go.
        """
        if isinstance(v, str):
            return re.sub(r"[\r\n\x00-\x1f\x7f]", "", v)
        return v

    @field_validator("message", mode="before")
    @classmethod
    def strip_message_control_characters(cls, v: object) -> object:
        """
        Message is body-only: keep \n and \t, drop other control characters,
        and normalise \r\n so length matches what the user sees.
        """
        if isinstance(v, str):
            v = v.replace("\r\n", "\n").replace("\r", "\n")
            return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", v)
        return v
