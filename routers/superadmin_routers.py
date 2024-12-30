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
        #print(f"city_name1: {city_name}")
    
        #print(f"type of city_name: {type(city_name)}")
        #print(f"city_name2: {city_name}")
    
        city = await SuperAdminOperations(db_session).create_city(city_name)
        print(f"City created: {city}")
      

        
        for streeet in exel_converter["data"]["streets"]:
            street = await SuperAdminOperations(db_session).create_street(streeet["street"])
          #  print(f"Street created: {street}")
            city_street =await SuperAdminOperations(db_session).create_city_street(city.id, street.id)
            #print(f"City_Street created: {city_street.city.city_name}, {city_street.street.street_name}")
            #for coord in streeet["coordinates"]:
             #   coord =await SuperAdminOperations(db_session).create_coord(coord["lat_lang"], coord["target_material"], street.id)
        #company = SuperAdminOperations(db_session).create_company(editors["company_name"])
       # company_editor = SuperAdminOperations(db_session).create_company_editor(editors["Com_Editor_email"], editors["Com_Editor_secret_key"])
        #Telekom_editor = SuperAdminOperations(db_session).create_telekom_editor(editors_obj.TelEditor_email, editors_obj.TelEditor_secret_key)
        


        
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
  "company_name": "string",
  "TelEditor_email": "string",
  "TelEditor_secret_key": "string",
  "Com_Editor_email": "string",
  "Com_Editor_secret_key": "string",
  "project_name": "string"
}

    """


