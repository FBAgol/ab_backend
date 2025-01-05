from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import ValidationError
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from operations.company_editor import CompanyEditorOperations
from db.engine import get_db
from schemas._input import Editor_regist , Login
from jwt_utils import create_access_token, create_refresh_token
from datetime import timedelta

companyeditor_router = APIRouter()

@companyeditor_router.post("/registeration")
async def register_company_Editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    company_editor: Editor_regist,
)-> dict:
    try:
        editor = await CompanyEditorOperations(db_session).registration(company_editor.secret_key, company_editor.email, company_editor.password)
        
        if isinstance(editor, str): 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=editor)
        
        access_token = create_access_token(data={"sub": str(editor["id"])}, expires_delta=timedelta(days=1)) 
        refresh_token = create_refresh_token(data={"sub": str(editor["id"])}, expires_delta=timedelta(days=7))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",  
            "editor": editor  
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    
"""

{
    "secret_key":"string456",
    "email":"max@baumax.de",
    "password":"maxbauman"
}
"""



@companyeditor_router.post("/login")
async def login_company_editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editor_login: Login
)-> dict:
    try:
        editor = await CompanyEditorOperations(db_session).login(editor_login.email, editor_login.password)
        
        if isinstance(editor, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=editor)
        
        access_token = create_access_token(data={"sub": str(editor["id"])}, expires_delta=timedelta(days=1)) 
        refresh_token = create_refresh_token(data={"sub": str(editor["id"])}, expires_delta=timedelta(days=7))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer", 
            "editor": editor  
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")



"""

{
    "email":"max@baumax.de",
    "password":"maxbauman"
}
"""