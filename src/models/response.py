from typing import Optional, Any, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def success_response(cls, data: Any = None, message: str = "Success"):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, error: str, message: str = "Error"):
        return cls(success=False, message=message, error=error)