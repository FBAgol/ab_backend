from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified
import sqlalchemy as sa
from fastapi import UploadFile, File, HTTPException
from uuid import UUID, uuid4
import tempfile
import os
import shutil

from db.models import Company_Editor, Project, City, City_Street, Street, Coordinate, Notification, Telekom_Editor
from db import Hash 
from convert_to_dict import to_dict
from jwt_utils import get_user_id_from_token
from NT_O_Detection_v3_800.anaylse_img import analyse_imgs




class TelekomEditorOperations: 
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session
        self.hash= Hash()

    
    async def registration(self, secret_key: str, email: str, password: str) -> Telekom_Editor| str:
        query = sa.select(Telekom_Editor).where(Telekom_Editor.email == email)
        
        async with self.db_session as session:
            try:
                editor = await session.scalar(query)

                if not editor or self.hash.verify(editor.secret_key, secret_key)!=True:
                    return "Invalid secret key or email."
                
                if editor.password and self.hash.verify(editor.password, password):
                    return "A password already exists for this editor."
                
                updated_password = self.hash.bcrypt(password)
                updated_editor = (sa.update(Telekom_Editor).where(Telekom_Editor.email == email).values(password=updated_password))
                await session.execute(updated_editor)
                await session.commit()
                editor.password = updated_password
                return to_dict(editor)

            except Exception as e:
                raise Exception(f"Unexpected error occurred: {e}")

    async def login(self, email:str, password:str)-> dict | str:
        try:
            editor_query= sa.select(Telekom_Editor).options(selectinload(Telekom_Editor.projects), joinedload(Telekom_Editor.super_admin), selectinload(Telekom_Editor.notifications)).where(Telekom_Editor.email==email)
            async with self.db_session as session:
                editor = await session.scalar(editor_query)
                if editor:
                    if self.hash.verify(editor.password, password):
                        notification_query= sa.select(Notification).options(selectinload(Notification.telekom_editor), selectinload(Notification.coordinate)).where(Notification.telekom_editor_id==editor.id)
                        notifications= await session.scalars(notification_query)
                        list_notifications= [notification.message for notification in notifications]
                        return {
                            "notifications": list_notifications,
                            "editor_id":to_dict(editor),
                        }
                    return "Invalid password."
                return "Invalid email."
        except Exception as e:
            raise Exception(f"Error logging in: {str(e)}")

    async def update_status_img(self, token: str, status: bool, objekt: str):
        editor_id = UUID(get_user_id_from_token(token))
        if not editor_id:
            raise HTTPException(status_code=401, detail="Telekom Editor not found.")
        
        editor_query = sa.select(Telekom_Editor).where(Telekom_Editor.id == editor_id)
        async with self.db_session as session:
            editor = await session.scalar(editor_query)
            if not editor:
                raise HTTPException(status_code=404, detail="Editor not found.")
            
            notification_query = sa.select(Notification).options(
                selectinload(Notification.coordinate), 
                selectinload(Notification.telekom_editor)
            ).where(Notification.telekom_editor_id == editor.id)
            
            delet_notification_query = sa.delete(Notification).where(
                Notification.telekom_editor_id == editor.id
            )
            
            if status:
                notifications = await session.scalars(notification_query)
                notifications = notifications.all()
                for notification in notifications:
                    coord_query = sa.select(Coordinate).where(Coordinate.id == notification.coordinate_id)
                    coord = await session.scalar(coord_query)
                    
                    if not coord:
                        raise HTTPException(status_code=404, detail="Coordinate not found.")
                    
                    materiallist = coord.result_materiallist  # Lade die Materialliste
                    updated = False
                    
                    for material in materiallist:
                        if material["object"] == objekt:  # Finde das passende Objekt
                            material["status"] = status   # Status aktualisieren
                            coord.result_materiallist = materiallist[:]  # JSON-Feld explizit neu zuweisen
                            flag_modified(coord, "result_materiallist")  # SQLAlchemy Änderungen mitteilen
                            session.add(coord)  # Objekt zur Session hinzufügen
                            updated = True
                            break
                    
                    if updated:
                        await session.execute(delet_notification_query)  # Lösche die Notification
                        break
                
                await session.commit()  # Änderungen bestätigen
        
        return "Status updated successfully."



"""
[
    {
        "object": "NT-Gehause",
        "status": true,
        "confidence": 92.43764281272888
    }
]
"""


"""
{
    "city": "Bremen",
    "street": "Oberblockland 2",
    "objects": {
        "object": "Orang-Speednetrohrchen",
        "status": false,
        "confidence": 51.210564374923706
    },
    "latitude": 53.1299169,
    "longitude": 8.86437022,
    "project_name": "telMax",
    "company_editor": "max@baumax.de",
    "analysed_image_url": "/static/images/analyse/46a3fcc3-31e1-4cd9-a0b3-1a82e96722b9.jpg"
}
"""




