from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
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
