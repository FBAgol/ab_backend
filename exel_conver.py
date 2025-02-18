from io import BytesIO
import pandas as pd
from fastapi import HTTPException
from typing import List


from pydantic import BaseModel
class Coordinate(BaseModel):
    fid: int
    latitude: float
    longitude: float
    target_material: str
class Street(BaseModel):
    street: str
    coordinates: List[Coordinate]

class City(BaseModel):
    city: str
    streets: List[Street]



def convert(data:list):

    city_data = City(
        city=data[0][1],
        streets=[]
    )

    street_map = {}

    for row in data:
        street_name = row[3] 
        latitude = row[6]
        longitude = row[7]
        material = row[2]  
        f_id= row[0]
        
        if street_name not in street_map:
            street_map[street_name] = Street(street=street_name, coordinates=[])
        
        street_map[street_name].coordinates.append(
            Coordinate(fid=f_id,latitude=latitude,longitude=longitude, target_material=material)
        )

    city_data.streets.extend(street_map.values())

    return city_data.model_dump()
        


    
async def convert_excel_to_list(file_content) -> list:
    file_extension = file_content.filename.split('.')[-1].lower()
    if file_extension not in ['xls', 'xlsx', 'csv']:
        raise HTTPException(status_code=400, detail="Only .xls, .xlsx, and .csv files are supported")

    file_content = await file_content.read()
    excel_data = BytesIO(file_content)

    if file_extension in ['xls', 'xlsx']:
        data = pd.read_excel(excel_data, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
    elif file_extension == 'csv':
        data = pd.read_csv(excel_data)

    # Daten in Listenform bringen
    rows = data.values.tolist()
    headers = data.columns.tolist()


    return {"headers": headers, "data": convert(rows)}



"""

u= {"rows": [
    [
    1,
    "Bremen",
    "VNR12345 421-27-Trassenstart_1",
    "Niederblockland 3a",
    28357,
    "Bremen Blockland",
    53.14741478,
    8.84019546,
    "pti:nord-11 tk:nord-11",
    "Bildbedarfspunkt",
    "2024-11-11"
    ],
    [
    2,
    "Bremen",
    "VNR12345 421-27-Trassenstart_2",
    "Niederblockland 14",
    28357,
    "Bremen Blockland",
    53.16001483371285,
    8.828138106807858,
    "pti:nord-11 tk:nord-11",
    "Bildbedarfspunkt",
    "2024-11-11"
    ],
    [
    3,
    "Bremen",
    "VNR12345 421-27-Trassenende_1",
    "Niederblockland 5",
    28357,
    "Bremen Blockland",
    53.15224121870196,
    8.839131319261183,
    "pti:nord-11 tk:nord-11",
    "Bildbedarfspunkt",
    "2024-11-11"
    ],
    [
    4,
    "Bremen",
    "VNR12345 421-27-Trassenende_2",
    "Oberblockland 14a",
    28357,
    "Bremen Blockland",
    53.14241918095298,
    8.84828945682217,
    "pti:nord-11 tk:nord-11",
    "Bildbedarfspunkt",
    "2024-11-11"
    ]]
    }
    
  if __name__ == "__main__":
    print(convert(u["rows"]))

""" 

