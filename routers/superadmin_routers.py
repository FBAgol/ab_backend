from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Body
from schemas._input import Editors_info
from pydantic import ValidationError
from db.engine import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from operations.superadmin import SuperAdminOperations
from exel_conver import convert_excel_to_list as exel_convert
import json

superadmin_router = APIRouter()


@superadmin_router.post("/")
async def create_editors_projects(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    editors: str= Form(...),
    file: UploadFile = File(...)
):
    
    try:
        try:
            editors_data = json.loads(editors)
            editors = Editors_info(**editors_data).model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON structure: {str(e)}")

        exel_converter= await exel_convert(file)
        city = SuperAdminOperations(db_session).create_city(data[0][1])
        company = SuperAdminOperations(db_session).create_company(editors["company_name"])

        for data in exel_converter["data"]:
            if len(data) == 0:
                raise HTTPException(status_code=400, detail="empty exel file")


        
        #company_editor = SuperAdminOperations(db_session).create_company_editor(editors_obj.Com_Editor_email, editors_obj.Com_Editor_secret_key)
        #Telekom_editor = SuperAdminOperations(db_session).create_telekom_editor(editors_obj.TelEditor_email, editors_obj.TelEditor_secret_key)
        

        # Rückgabe der verarbeiteten Daten
        return {
            "editors": editors,
            "headers": exel_converter["headers"],
            "rows": exel_converter["data"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")