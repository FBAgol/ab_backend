from fastapi import APIRouter, HTTPException, Depends, status, Body, File, UploadFile, Form
from starlette.responses import JSONResponse
from typing import Annotated
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from operations.company_editor import CompanyEditorOperations
from db.engine import get_db
from schemas._input import Editor_regist , Login, UploadImgRequest, UpdateImgRequest
from jwt_utils import create_access_token, create_refresh_token



companyeditor_router = APIRouter()

@companyeditor_router.post("/registeration")
async def register_company_Editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    company_editor: Editor_regist= Body(...),
)-> dict:
    try:
        editor = await CompanyEditorOperations(db_session).registration(company_editor.secret_key, company_editor.email, company_editor.password, company_editor.role)
        
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
    "secret_key":"string456",
    "email":"max@baumax.de",
    "password":"maxbauman",
    "role":1
}
"""



@companyeditor_router.post("/login")
async def login_company_editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editor_login: Login
)-> dict:
    try:
        editor = await CompanyEditorOperations(db_session).login(editor_login.email, editor_login.password, editor_login.role)
        
        if isinstance(editor, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=editor)
        
        access_token = create_access_token(data={"sub": str(editor["editor_info"]["id"])}, expires_delta=timedelta(days=1)) 
        refresh_token = create_refresh_token(data={"sub": str(editor["editor_info"]["id"])}, expires_delta=timedelta(days=7))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer", 
            "projects": editor["projekts"],
            "company_name": editor["company_name"] 
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")
    
"""

{
    "email":"max@baumax.de",
    "password":"maxbauman",
    "role":1
}
"""

@companyeditor_router.get("/projectname/{projectname}")
async def get_projects_info(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editor_token: str,
    projectname: str
)-> dict:
    try:
        projects = await CompanyEditorOperations(db_session).get_projects_info(editor_token, projectname)
        if isinstance(projects, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=projects)
        
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


"""
{
    "editor_toekn":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlOWEyNzg3Zi00Njk1LTQxM2YtYWZjOC0wYWI5ODkxMDNiZTAiLCJleHAiOjE3MzYxODk1NjJ9.9aO14EFDiJ7mCzJfss53WkwlbLPsaMY5mf0ZraLSdBw",
    "projectname":"telMax"
}
"""



    
@companyeditor_router.post("/upload/img")
async def upload_img(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    upload_img_request: str= Form(...),
    file: UploadFile = File(...)
):
    try:
        upload_request = UploadImgRequest.model_validate_json(upload_img_request).model_dump()
        # Analysiere das Bild und erhalte die Ergebnisse
        result = await CompanyEditorOperations(db_session).analyse_img(upload_request["token"], upload_request["lat"], upload_request["long"], file)

        # Rückgabe der Analyseergebnisse als JSON
        return JSONResponse(content=result)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
   
    



"""
{   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNWU5NjdiNC0xYzI3LTQwM2QtOGYzMy1mZDNiY2M4NWM3MjMiLCJleHAiOjE3MzY1ODY0NTN9.rrqde5m2hmIhAfGNzkIIdGAtemdOec4Y5PncTfYTJPU", 
   "lat": 53.129916900000000,  
     "long":8.864370220000000
 }

"""

@companyeditor_router.put("/update/img_coordinate")
async def update_img_coordinate(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    update_img_request: str= Form(...),
    file: UploadFile = File(...)
):
    try:
        update_request = UpdateImgRequest.model_validate_json(update_img_request).model_dump()
        result = await CompanyEditorOperations(db_session).update_coord_img(update_request["token"], update_request["lat"], update_request["long"], update_request["oldOriginalImgUrl"], update_request["oldAnalyzedImgUrl"], file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    

"""
    {  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMDAzMzcyZS04ZjM2LTQ0NzYtOTU4OS0wNDE3YjgwZDM3MmEiLCJleHAiOjE3MzY0NDg1Njl9.AQ9W0hpDBy2xZDj54oSGcN4mQvgZrJHCKQUXVneK_Dw", 
    "lat": 53.129916900000000,  
    "long":8.864370220000000,
    "oldOriginalImgUrl":"/static/images/original/7a092857-4e0d-47af-a9d6-a0ae87d59adb.jpg",
    "oldAnalyzedImgUrl":"/static/images/analyse/c95be6d1-f721-4a12-bed6-09babe73aa51.jpg"
    }
"""