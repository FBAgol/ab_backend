from fastapi import APIRouter, HTTPException, Depends, status, Body, Header
from typing import Annotated
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from operations.telekom_editor import TelekomEditorOperations
from db.engine import get_db
from schemas._input import Editor_regist , Login
from jwt_utils import create_access_token, create_refresh_token



telekomeditor_router = APIRouter()


@telekomeditor_router.post("/registration")
async def register_telekom_Editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    telekom_editor: Editor_regist= Body(...),
)-> dict | str:
    try:
        editor = await TelekomEditorOperations(db_session).registration(telekom_editor.secret_key, telekom_editor.email, telekom_editor.password,telekom_editor.role)
        
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
    "password":"Telekom(123)",
    "role":2
}
"""



@telekomeditor_router.post("/login")
async def login_telekom_editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editor_login: Login
)-> dict | str:
    try:
        editor = await TelekomEditorOperations(db_session).login(editor_login.email, editor_login.password, editor_login.role)
       # print("editor info ",editor)
        
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
    status: bool,
    objekt: str,
    Authorization: str=Header(...)
):
    try:
        update_status= await TelekomEditorOperations(db_session).update_status_img(Authorization, status, objekt)
        if not update_status:
            raise HTTPException(status_code=404, detail="Image not found.")
        return{"result": update_status} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating image status: {str(e)}")
    
"""

    {
        "email":"golzari@telekom.de",
        "password":"Telekom(123)",
        "role":2
    }
"""


@telekomeditor_router.get("/projectname/{projectname}")
async def get_projects_info(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    projectname: str,
    Authorization: str=Header(...)
)-> dict:
    # Entferne den "Bearer " Präfix (falls vorhanden)
    if Authorization.startswith("Bearer "):
        token = Authorization.replace("Bearer ", "")
    else:
        token = Authorization  # Falls kein Präfix vorhanden ist, verwende den gesamten Header

    #print(f"Extracted token: {token}")  # Debugging

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization header is missing or invalid.",
        )
    try:
        projects = await TelekomEditorOperations(db_session).get_projects_info(token, projectname)
        if isinstance(projects, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=projects)
        
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")