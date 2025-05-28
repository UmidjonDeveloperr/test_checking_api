from dataclasses import Field
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TestCreate(BaseModel):
    test_id: str
    subject1: str
    subject2: str
    status: str
    answers: str
    created_at: datetime

class DeleteResponse(BaseModel):
    success: bool
    message: str


class TestResponse(TestCreate):
    id: int
    #created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class UserResponseCreate(BaseModel):
    test_id: str
    telegram_id: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    region: str
    answers: str

class UserResponseOut(BaseModel):
    #test_id: str
    telegram_id: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    region: str
    answers: str

class UserResponseResponse(UserResponseOut):
    id: int
    score: float

    class Config:
        orm_mode = True