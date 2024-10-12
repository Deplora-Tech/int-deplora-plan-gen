from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserQuery(BaseModel):
    email: str

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True
