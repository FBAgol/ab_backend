from io import BytesIO
import pandas as pd
from fastapi import HTTPException


from pydantic import BaseModel
class coords(BaseModel):
    lat_lang: list[str, str]
    target_material: str
class street_of_city(BaseModel):
    street: str
    coordinates: coords

class Editors_info(BaseModel):
    city: str
    street_of_city: street_of_city


i= {
    "city": "jeddah",
    "street_of_city": {
        "street": "alnuzhah",
        "coordinates": [
            {
                "lat_lang": "[21.285406, 39.237550]",
                "target_material": "fiber"
            },
            {
                "lat_lang": [21.285406, 39.237550],
                "target_material": "fiber"
            }
        ]
    }
}


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


def convert(data):
    pass

    
async def convert_excel_to_list(file_content) -> list:
    file_extension = file_content.filename.split('.')[-1].lower()
    if file_extension not in ['xls', 'xlsx', 'csv']:
        raise HTTPException(status_code=400, detail="Only .xls, .xlsx, and .csv files are supported")

    # Datei lesen und Daten extrahieren
    file_content = await file_content.read()
    excel_data = BytesIO(file_content)

    if file_extension in ['xls', 'xlsx']:
        data = pd.read_excel(excel_data, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
    elif file_extension == 'csv':
        data = pd.read_csv(excel_data)

    # Daten in Listenform bringen
    rows = data.values.tolist()
    headers = data.columns.tolist()

    info= {
        "city":rows[0][1],
        "street_of_city": {
            "street": rows[1][1],
            "coordinates": []
        }
    }

    return {"headers": headers, "data": rows}