from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified
import sqlalchemy as sa
from fastapi import  HTTPException
from uuid import UUID

from db.models import  Coordinate, Notification, Telekom_Editor, Project, City, City_Street, Street
from db import Hash 
from convert_to_dict import to_dict
from jwt_utils import get_user_id_from_token




class TelekomEditorOperations: 
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session
        self.hash= Hash()

    
    async def registration(self, secret_key: str, email: str, password: str, role:int) -> Telekom_Editor| str:
        query = sa.select(Telekom_Editor).where(Telekom_Editor.email == email)
        
        async with self.db_session as session:
            try:
                editor = await session.scalar(query)

                if not editor or self.hash.verify(editor.secret_key, secret_key)!=True and editor.role!=role:
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

    async def login(self, email:str, password:str, role:int)-> dict | str:
        try:
            editor_query= sa.select(Telekom_Editor).options(selectinload(Telekom_Editor.projects), joinedload(Telekom_Editor.super_admin), selectinload(Telekom_Editor.notifications)).where(Telekom_Editor.email==email)
            async with self.db_session as session:
                editor = await session.scalar(editor_query)
                if editor:
                    if self.hash.verify(editor.password, password) and editor.role==role:  
                        notification_query= sa.select(Notification).options(selectinload(Notification.telekom_editor), selectinload(Notification.coordinate)).where(Notification.telekom_editor_id==editor.id)
                        notifications= await session.scalars(notification_query)
                        list_notifications= [notification.message for notification in notifications]
                        return {
                            "notifications": list_notifications,
                            "editor_id":to_dict(editor),
                        }
                    return "Invalid password or role."
                return "Invalid email."
        except Exception as e:
            raise Exception(f"Error logging in: {str(e)}")

    async def update_status_img(self, token: str, status: bool, lat:float, lon:float, object:str)-> str:
        editor_id = UUID(get_user_id_from_token(token))
        if not editor_id:
            raise HTTPException(status_code=401, detail="Telekom Editor not found.")
        
        editor_query = sa.select(Telekom_Editor).where(Telekom_Editor.id == editor_id)
        coord_query= sa.select(Coordinate).where(Coordinate.latitude==lat, Coordinate.longitude==lon)
        async with self.db_session as session:
            editor = await session.scalar(editor_query)
            if not editor:
                raise HTTPException(status_code=404, detail="Editor not found.")
            
            coord = await session.scalar(coord_query)
            
            delet_notification_query = sa.delete(Notification).where(
                Notification.coordinate_id == coord.id,
            )
            
            if status:                    
                if not coord:
                    raise HTTPException(status_code=404, detail="Coordinate not found.")
                
                materiallist = coord.result_materiallist 
                
                for material in materiallist:
                    if material["object"] == object:  
                        material["status"] = status   
                        coord.result_materiallist = materiallist[:] 
                        flag_modified(coord, "result_materiallist")  # SQLAlchemy Änderungen mitteilen
                        session.add(coord)  # Objekt zur Session hinzufügen
     
                        break
                
                await session.execute(delet_notification_query)
                
                await session.commit()
        
        return "Status updated successfully."
    
    

    async def get_projects_info(self, editor_token: str, projectname: str) -> dict | str:
        editor_id = UUID(get_user_id_from_token(editor_token))
       # print("editor_id is:   ",editor_id)
        try:
            query = (
                sa.select(Telekom_Editor)
                .options(
                    selectinload(Telekom_Editor.projects)
                    .selectinload(Project.city)
                    .selectinload(City.city_streets)
                    .selectinload(City_Street.street)
                    .selectinload(Street.coordinates)
                )
                .where(Telekom_Editor.id == editor_id)
            )
            
            async with self.db_session as session:
                editor = await session.scalar(query)
                if editor:
                    for project in editor.projects:
                        if project.project_name == projectname:
                            # Extrahiere alle gewünschten Informationen
                            city = project.city
                            streets = [
                                {
                                    "street_name": street.street_name,
                                    "coordinates_ZoneId": [
                                        {   "zone_id": coord.zone_id,
                                            "latitude": coord.latitude,
                                            "longitude": coord.longitude,
                                            "target_material": coord.result_materiallist,
                                            "result_materiallist": coord.result_materiallist,
                                            "original_image_url": coord.original_image_url,
                                            "analysed_image_url": coord.analysed_image_url,
                                        }
                                        for coord in street.coordinates
                                    ],
                                }
                                for city_street in city.city_streets
                                for street in [city_street.street]
                            ]
                            
                            project_info = {
                                "project_name": project.project_name,
                                "city": city.city_name if city else None,
                                "streets": streets,
                            }
                            return project_info
                    return "Project not found."
                return "Editor not found."
        except Exception as e:
            raise Exception(f"Error getting project info: {str(e)}")


"""
[
    {
        "object": "NT-Gehause",
        "status": true,
        "confidence": 92.43764281272888
    }
]
"""


