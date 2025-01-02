import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from pydantic import ValidationError
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from operations.superadmin import SuperAdminOperations
from db.engine import get_db
from schemas._input import Editors_info
from exel_conver import convert_excel_to_list as exel_convert


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
        city_name = exel_converter["data"]["city"]
        city = await SuperAdminOperations(db_session).create_city(city_name)
        
        for streeet in exel_converter["data"]["streets"]:
            street = await SuperAdminOperations(db_session).create_street(streeet["street"])
            city_street =await SuperAdminOperations(db_session).create_city_street(city.id, street.id)
            for coord in streeet["coordinates"]:
                coord =await SuperAdminOperations(db_session).create_coord(coord["lat_lang"], coord["target_material"], street.id)

        company =await SuperAdminOperations(db_session).create_company(editors["company_name"], editors["superadmin_id"])
        company_editor =await SuperAdminOperations(db_session).create_company_editor(editors["Com_Editor_email"], editors["Com_Editor_secret_key"], company.id)
        telekom_editor =await SuperAdminOperations(db_session).create_telekom_editor(editors["TelEditor_email"], editors["TelEditor_secret_key"], editors["superadmin_id"])
        project=await SuperAdminOperations(db_session).create_project(editors["project_name"], company_editor.id, telekom_editor.id, city.id)
        

        # Rückgabe der verarbeiteten Daten
        return {
            "editors": editors,
            "headers": exel_converter["headers"],
            "rows": exel_converter["data"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    




    """
    {
  "superadmin_id": "123123166aee42c88b6a4dcbc99bafe1", 
  "company_name": "baumax",
  "TelEditor_email": "golzari@telekom.de",
  "TelEditor_secret_key": "string123",
  "Com_Editor_email": "max@baumax.de",
  "Com_Editor_secret_key": "string456",
  "project_name": "telMax"
}

    """


