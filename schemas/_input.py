from pydantic import BaseModel
from uuid import UUID

class  Editors_info(BaseModel):
    superadmin_id:UUID
    company_name: str
    TelEditor_email: str
    TelEditor_secret_key: str
    Com_Editor_email: str
    Com_Editor_secret_key: str
    project_name: str

    class Config:
        orm_mode = True


class Editor_regist(BaseModel):
    secret_key:str
    email:str
    password:str

    class Config:
        orm_mode = True

class Login(BaseModel):
    email:str
    password:str

    class Config:
        orm_mode = True