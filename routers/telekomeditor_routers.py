from fastapi import APIRouter, HTTPException, Depends, status, Body, File, UploadFile, Form
from starlette.responses import JSONResponse
from typing import Annotated
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from operations.telekom_editor import TelekomEditorOperations
from db.engine import get_db
from schemas._input import Editor_regist , Login, UploadImgRequest, UpdateImgRequest
from jwt_utils import create_access_token, create_refresh_token



telekomeditor_router = APIRouter()


@telekomeditor_router.post("/registeration")
async def register_telekom_Editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    telekom_editor: Editor_regist= Body(...),
)-> dict:
    try:
        editor = await TelekomEditorOperations(db_session).registration(telekom_editor.secret_key, telekom_editor.email, telekom_editor.password)
        
        if isinstance(editor, str): 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=editor)
        
        access_token = create_access_token(data={"sub": str(editor["id"])}, expires_delta=timedelta(days=1)) 
        refresh_token = create_refresh_token(data={"sub": str(editor["id"])}, expires_delta=timedelta(days=7))
        
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
    "secret_key":"string123",
    "email":"golzari@telekom.de",
    "password":"telekom"
}
"""



@telekomeditor_router.post("/login")
async def login_company_editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editor_login: Login
)-> dict:
    try:
        editor = await TelekomEditorOperations(db_session).login(editor_login.email, editor_login.password)
        print("editor info ",editor)
        
        if isinstance(editor, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=editor)
        
        access_token = create_access_token(data={"sub": str(editor["editor_id"]["id"])}, expires_delta=timedelta(days=1)) 
        refresh_token = create_refresh_token(data={"sub": str(editor["editor_id"]["id"])}, expires_delta=timedelta(days=7))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "notifications": editor["notifications"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")
    
@telekomeditor_router.put("/update_status_img")
async def update_status_img(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    token: str,
    status: bool,
    objekt: str
):
    try:
        update_status= await TelekomEditorOperations(db_session).update_status_img(token, status, objekt)
        if not update_status:
            raise HTTPException(status_code=404, detail="Image not found.")
        return{"result": update_status} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating image status: {str(e)}")
    
"""

{
    "email":"golzari@telekom.de",
    "password":"telekom"
}
"""
