from pydantic import BaseModel
from uuid import UUID
from typing import List

class  ManagementInfo(BaseModel):
    token:str
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
    role:int

    class Config:
        orm_mode = True

class Login(BaseModel):
    email:str
    password:str
    role:int

    class Config:
        orm_mode = True


class ProjectInfo(BaseModel):
    editor_toekn:str
    projectname:str

    class Config:
        orm_mode = True

class AnalyseImg(BaseModel):
    obejct:str
    confidense:int
    status:bool

    class Config:
        orm_mode = True



class CoordinateOfImg(BaseModel):
    lat: float
    long: float

    class Config:
        orm_mode = True


class UpdateImgRequest(BaseModel):
    oldOriginalImgUrl: str
    oldAnalyzedImgUrl: str

    class Config:
        orm_mode = True

class UpdateObjectStatusRequest(BaseModel):
    status: bool
    lat: float
    long: float
    objectName: str
    class Config:
        orm_mode = True