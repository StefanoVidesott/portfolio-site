import re
from pydantic import BaseModel, EmailStr, Field, field_validator

class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=2000)
    turnstile_token: str = Field(min_length=1, max_length=2048)

    @field_validator("name", "message")
    @classmethod
    def strip_control_characters(cls, v: str) -> str:
        """Remove CR, LF, and all ASCII control characters.
        Prevents email header injection via the Subject line (which interpolates
        `name`) and eliminates null-byte smuggling in the message body.
        """
        return re.sub(r"[\r\n\x00-\x1f\x7f]", "", v)
