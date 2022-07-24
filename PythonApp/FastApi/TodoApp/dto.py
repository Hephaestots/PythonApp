from pydantic import BaseModel, Field
from typing import Optional


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description='The priority must be between 1 and 5.')
    complete: bool

    # Configuration of the default values for the BaseModel.
    class Config:
        schema_extra = {
            "example": {
                "title": "Gotta do this.",
                "description": "Short description of the `this`.",
                "priority": 4,
                "complete": False
            }
        }