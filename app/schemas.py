from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated
from pydantic.types import conint


class PostBase(BaseModel):
        title : str
        text : str

        class Config:
            from_attributes = True

class PostCreate(PostBase):
        pass

class PostUpdate(PostBase):
        pass

class UserResponse(BaseModel):
        id: int
        created_at: datetime

class PostResponse(PostBase):
        id: int
        created_at: datetime
        account_id: int
        account: UserResponse


class PostVoteResponse(BaseModel):
        post : PostResponse
        vote : int

        class Config:
            from_attributes = True



class UserBase(BaseModel):
        email : Annotated[str, Field(pattern=r'^[A-Za-z0-9._+%-]+@(gmail|yahoo|outlook|yandex)\.(com|ru)$')]
        
        class Config:
            from_attributes = True

class UserCreate(UserBase):
        password : str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # or orm_mode = True in older Pydantic

class UserLogin(UserBase):
        email : Annotated[str, Field(pattern=r'^[A-Za-z0-9._+%-]+@(gmail|yahoo|outlook|yandex)\.(com|ru)$')]
        password : str

class Token(BaseModel):
        access_token : str
        token_type : str | None = None

        class Config:
            from_attributes = True

class TokenData(BaseModel):
        id : int | None = None

class VoteBase(BaseModel):
        post_id : int
        vote_option : conint(le=1) #constrained int