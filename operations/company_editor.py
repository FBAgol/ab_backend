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



# Verzeichnisse für Bilder
ORIGINAL_DIR = "/app/images/original"
ANALYSE_DIR = "/app/images/analyse"

# Verzeichnisse sicherstellen
os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(ANALYSE_DIR, exist_ok=True)

class CompanyEditorOperations: 
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session
        self.hash= Hash()

    
    async def registration(self, secret_key: str, email: str, password: str, role:int) -> Company_Editor| str:
        query = sa.select(Company_Editor).where(Company_Editor.editor_email == email)
        
        async with self.db_session as session:
            try:
                editor = await session.scalar(query)

                if not editor or self.hash.verify(editor.secret_key, secret_key)!=True and editor.role != role:
                    return "Invalid secret key or email or role."
                
                if editor.password and self.hash.verify(editor.password, password):
                    return "A password already exists for this editor."
                
                updated_password = self.hash.bcrypt(password)
                updated_editor = (sa.update(Company_Editor).where(Company_Editor.editor_email == email).values(password=updated_password))
                await session.execute(updated_editor)
                await session.commit()
                editor.password = updated_password
                return to_dict(editor)

            except Exception as e:
                raise Exception(f"Unexpected error occurred: {e}")

    async def login(self, email:str, password:str, role:int)-> dict | str:
        try:
            query= sa.select(Company_Editor).options(selectinload(Company_Editor.projects), joinedload(Company_Editor.company)).where(Company_Editor.editor_email==email)

            async with self.db_session as session:
                editor = await session.scalar(query)
                if editor:
                    if self.hash.verify(editor.password, password) and editor.role == role:
                        list_projecnamen= [project.project_name for project in editor.projects]
                        return {
                            "company_name": editor.company.company_name,
                            "projekts": list_projecnamen,
                            "editor_info": to_dict(editor)
                        }
                    return "Invalid password."
                return "Invalid email."
        except Exception as e:
            raise Exception(f"Error logging in: {str(e)}")


    async def get_projects_info(self, editor_token: str, projectname: str) -> dict | str:
        editor_id = UUID(get_user_id_from_token(editor_token))
        print("editor_id is:   ",editor_id)
        try:
            query = (
                sa.select(Company_Editor)
                .options(
                    selectinload(Company_Editor.projects)
                    .selectinload(Project.city)
                    .selectinload(City.city_streets)
                    .selectinload(City_Street.street)
                    .selectinload(Street.coordinates)
                )
                .where(Company_Editor.id == editor_id)
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
        

    
    async def analyse_img(self, token: str, lat: float, long: float, file: UploadFile) -> dict:
        editor_id = UUID(get_user_id_from_token(token))

        query_editor = sa.select(Company_Editor).where(Company_Editor.id == editor_id)
        query_coord = sa.select(Coordinate).where(Coordinate.latitude == lat, Coordinate.longitude == long)

        async with self.db_session as session:
            editor = await session.scalar(query_editor)
            coord_obj = await session.scalar(query_coord)

            if not editor or not coord_obj:
                raise HTTPException(status_code=404, detail="Editor or coordinates not found.")

            # Temporäre Datei für das Originalbild erstellen
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(await file.read())
                tmp_file_path = tmp_file.name

            try:
                analysed_image, detected_objects = analyse_imgs(tmp_file_path)

                # Originalbild speichern
                original_filename = f"{uuid4()}.jpg"
                original_filepath = os.path.join(ORIGINAL_DIR, original_filename)
                shutil.move(tmp_file_path, original_filepath)

                # Analysiertes Bild speichern
                analysed_filename = f"{uuid4()}.jpg"
                analysed_filepath = os.path.join(ANALYSE_DIR, analysed_filename)
                with open(analysed_filepath, "wb") as analysed_file:
                    analysed_file.write(analysed_image.getvalue())

                # Bild-URLs generieren
                original_image_url = f"/static/images/original/{original_filename}"
                analysed_image_url = f"/static/images/analyse/{analysed_filename}"

                # Datenbank aktualisieren
                coord_obj.original_image_url = original_image_url
                coord_obj.analysed_image_url = analysed_image_url
                coord_obj.result_materiallist = detected_objects

                project_query = sa.select(Project).where(Project.company_editor_id == editor.id)
                project = await session.scalar(project_query)

                if not project:
                    raise HTTPException(status_code=404, detail="Project not found.")

                # Überprüfen, ob Benachrichtigungen nötig sind
                notification_message = None
                for obj in detected_objects:
                    if obj["status"] == False:
                        telekom_editor_query = sa.select(Telekom_Editor).where(Telekom_Editor.id == project.telekom_editor_id)
                        telekom_editor = await session.scalar(telekom_editor_query)

                        if not telekom_editor:
                            raise HTTPException(status_code=404, detail="Telekom Editor not found.")

                        city_query = sa.select(City).where(City.id == project.city_id)
                        city = await session.scalar(city_query)

                        street_query = sa.select(Street).where(Street.id == coord_obj.street_id)
                        street = await session.scalar(street_query)

                        # Benachrichtigung erstellen (JSON)
                        notification_message = {
                            "project_name": project.project_name,
                            "city": city.city_name if city else "N/A",
                            "street": street.street_name if street else "N/A",
                            "company_editor": editor.editor_email,
                            "latitude": float(coord_obj.latitude),
                            "longitude": float(coord_obj.longitude),
                            "analysed_image_url": analysed_image_url,
                            "objects": obj,
                        }

                        notification = Notification(
                            message=notification_message,
                            coordinate_id=coord_obj.id,
                            telekom_editor_id=telekom_editor.id
                        )
                        session.add(notification)

                await session.commit()

                return {
                    "detected_objects": detected_objects,
                    "original_image_url": original_image_url,
                    "analysed_image_url": analysed_image_url,
                    "notification": notification_message
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error during image analysis: {str(e)}")

            finally:
                # Sicherstellen, dass temporäre Datei gelöscht wird, falls sie noch existiert
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
    


        
    async def update_coord_img(self, token: str, lat: float, long: float, oldOriginalImgUrl: str, oldAnalyseImgUrl: str, newFile: UploadFile) -> None:
        editor_id = UUID(get_user_id_from_token(token))
        query_editor = sa.select(Company_Editor).where(Company_Editor.id == editor_id)
        query_coord = sa.select(Coordinate).where(Coordinate.latitude == lat, Coordinate.longitude == long)
        
        
        async with self.db_session as session:
            editor = await session.scalar(query_editor)
            coord= await session.scalar(query_coord)

            if not editor or not coord:
                raise HTTPException(status_code=404, detail="Editor or coordinate not found.")

            # Temporäre Datei für das neue Originalbild erstellen
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(await newFile.read())
                tmp_file_path = tmp_file.name

            try:
                # Analyse des neuen Bildes durchführen
                analysed_image, detected_objects = analyse_imgs(tmp_file_path)

                # Alte Bilder löschen, wenn sie existieren
                if oldOriginalImgUrl:
                    old_original_path = os.path.join(ORIGINAL_DIR, os.path.basename(oldOriginalImgUrl))
                    if os.path.exists(old_original_path):
                        os.remove(old_original_path)

                if oldAnalyseImgUrl:
                    old_analysed_path = os.path.join(ANALYSE_DIR, os.path.basename(oldAnalyseImgUrl))
                    if os.path.exists(old_analysed_path):
                        os.remove(old_analysed_path)

                # Neues Originalbild speichern
                original_filename = f"{uuid4()}.jpg"
                original_filepath = os.path.join(ORIGINAL_DIR, original_filename)
                shutil.move(tmp_file_path, original_filepath)

                # Neues analysiertes Bild speichern
                analysed_filename = f"{uuid4()}.jpg"
                analysed_filepath = os.path.join(ANALYSE_DIR, analysed_filename)
                with open(analysed_filepath, "wb") as analysed_file:
                    analysed_file.write(analysed_image.getvalue())

                # Neue Bild-URLs generieren
                original_image_url = f"/static/images/original/{original_filename}"
                analysed_image_url = f"/static/images/analyse/{analysed_filename}"

                 # Lösche alte Benachrichtigungen
                query_notification = sa.select(Notification).where(Notification.coordinate_id == coord.id)

                notification = await session.scalar(query_notification)
            


                if notification:
                    delete_coord_notification_query = sa.delete(Notification).where(Notification.coordinate_id == coord.id)
                    #await session.scalar(delete_coord_notification_query)
                    await session.execute(delete_coord_notification_query)
                

                # Datenbank aktualisieren
                coord.original_image_url = original_image_url
                coord.analysed_image_url = analysed_image_url
                coord.result_materiallist = detected_objects

                project_query = sa.select(Project).where(Project.company_editor_id == editor.id)
                project = await session.scalar(project_query)

                if not project:
                    raise HTTPException(status_code=404, detail="Project not found.")

                # Überprüfen, ob Benachrichtigungen nötig sind
                notification_message = None
                for obj in detected_objects:
                    if obj["status"] == False:
                        telekom_editor_query = sa.select(Telekom_Editor).where(Telekom_Editor.id == project.telekom_editor_id)
                        telekom_editor = await session.scalar(telekom_editor_query)

                        if not telekom_editor:
                            raise HTTPException(status_code=404, detail="Telekom Editor not found.")

                        city_query = sa.select(City).where(City.id == project.city_id)
                        city = await session.scalar(city_query)

                        street_query = sa.select(Street).where(Street.id == coord.street_id)
                        street = await session.scalar(street_query)

                        # Benachrichtigung erstellen (JSON)
                        notification_message = {
                            "project_name": project.project_name,
                            "city": city.city_name if city else "N/A",
                            "street": street.street_name if street else "N/A",
                            "company_editor": editor.editor_email,
                            "latitude": float(coord.latitude),
                            "longitude": float(coord.longitude),
                            "analysed_image_url": analysed_image_url,
                            "objects": obj,
                        }

                        notification = Notification(
                            message=notification_message,
                            coordinate_id=coord.id,
                            telekom_editor_id=telekom_editor.id
                        )
                        session.add(notification)

                    await session.commit()
                return {
                "detected_objects": detected_objects,
                "original_image_url": original_image_url,
                "analysed_image_url": analysed_image_url,
                "notification": notification_message
            }

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error during image analysis: {str(e)}")

            finally:
                # Sicherstellen, dass temporäre Datei gelöscht wird, falls sie noch existiert
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
            

    async def get_img(self, token: str, img_url: str) -> bytes | None:
        editor_id = UUID(get_user_id_from_token(token))
        query_editor = sa.select(Company_Editor).where(Company_Editor.id == editor_id)
        query_coord = sa.select(Coordinate).where(Coordinate.original_image_url == img_url)

        async with self.db_session as session:
            editor = await session.scalar(query_editor)
            coord = await session.scalar(query_coord)

            if not editor or not coord:
                raise HTTPException(status_code=404, detail="Editor or coordinate not found.")

            image_path = os.path.join(ORIGINAL_DIR, os.path.basename(img_url))

            if os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    return image_file.read()
            return None
         

                

            