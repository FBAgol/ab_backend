import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, status, Body
from pydantic import ValidationError
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from uuid import UUID

from operations.superadmin import SuperAdminOperations
from db.engine import get_db
from schemas._input import ManagementInfo, Login, Editor_regist
from exel_conver import convert_excel_to_list as exel_convert
from jwt_utils import create_access_token, create_refresh_token, get_user_id_from_token



superadmin_router = APIRouter()

@superadmin_router.post("/registration")
async def register_superadadmin(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    company_editor: Login,
)-> dict | str:
    try:
        ##print("company_editor", company_editor)
        editor = await SuperAdminOperations(db_session).registration( company_editor.email, company_editor.password, company_editor.role)
        
        if isinstance(editor, str): 
            return editor
        
        print("editor info ",editor["editor_id"]["id"])
        
        access_token = create_access_token(data={"sub": str(editor["editor_id"]["id"])}, expires_delta=timedelta(days=1)) 
        refresh_token = create_refresh_token(data={"sub": str(editor["editor_id"]["id"])}, expires_delta=timedelta(days=7))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",  
            "status": "registaion successful",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

"""
{
"email": "farzad@gmail.com",
"password": "Farzad(18)",
"role": 0
}
"""

@superadmin_router.post("/login")
async def login_superadmin(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editor_login: Login
)-> dict | str:
    try:
        editor = await SuperAdminOperations(db_session).login(editor_login.email, editor_login.password, editor_login.role)
        print("editor info ",editor)
        
        if isinstance(editor, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=editor)
        
        access_token = create_access_token(data={"sub": str(editor["editor_id"]["id"])}, expires_delta=timedelta(days=1)) 
        refresh_token = create_refresh_token(data={"sub": str(editor["editor_id"]["id"])}, expires_delta=timedelta(days=7))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    

"""
{
"email": "farzad@gmail.com",
"password": "farzad",
"role": 0
}
"""
    
@superadmin_router.post("/define_projects")
async def create_editors_projects(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editors: str= Form(...),
    file: UploadFile = File(...)
):
    
    try:
        try:
            editors_data = json.loads(editors)
            editors = ManagementInfo(**editors_data).model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON structure: {str(e)}")

        exel_converter= await exel_convert(file)
        city_name = exel_converter["data"]["city"]
        super_admin_id= UUID(get_user_id_from_token(editors["token"]))
        city = await SuperAdminOperations(db_session).create_city(super_admin_id,city_name)
        
        for streeet in exel_converter["data"]["streets"]:
            street = await SuperAdminOperations(db_session).create_street(streeet["street"])
            city_street =await SuperAdminOperations(db_session).create_city_street(city.id, street.id)
            for coord in streeet["coordinates"]:
                coord =await SuperAdminOperations(db_session).create_coord(coord["fid"],coord["latitude"],coord["longitude"], coord["target_material"], street.id)

        company =await SuperAdminOperations(db_session).create_company(editors["company_name"], super_admin_id)
        company_editor =await SuperAdminOperations(db_session).create_company_editor(editors["Com_Editor_email"], editors["Com_Editor_secret_key"], company.id)
        telekom_editor =await SuperAdminOperations(db_session).create_telekom_editor(editors["TelEditor_email"], editors["TelEditor_secret_key"], super_admin_id)
        project=await SuperAdminOperations(db_session).create_project(editors["project_name"], company_editor.id, telekom_editor.id, city.id)
        
        """
        return {
            "editors": editors,
            "headers": exel_converter["headers"],
            "rows": exel_converter["data"],
        }
        """

        return {
            "status": "project created successfully",
        }

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    




    """
    { 
  "company_name": "baumax",
  "TelEditor_email": "golzari@telekom.de",
  "TelEditor_secret_key": "string123",
  "Com_Editor_email": "max@gmail.de",
  "Com_Editor_secret_key": "string456",
  "project_name": "telMax"
}

    """


