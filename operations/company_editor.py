from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
import sqlalchemy as sa
from db.models import Company_Editor, Project, City, City_Street, Street
from db import Hash 
from convert_to_dict import to_dict
from jwt_utils import get_user_id_from_token
from uuid import UUID


class CompanyEditorOperations: 
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session
        self.hash= Hash()

    
    async def registration(self, secret_key: str, email: str, password: str) -> Company_Editor| str:
        query = sa.select(Company_Editor).where(Company_Editor.editor_email == email)
        
        async with self.db_session as session:
            try:
                editor = await session.scalar(query)

                if not editor or self.hash.verify(editor.secret_key, secret_key)!=True:
                    return "Invalid secret key or email."
                
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

    async def login(self, email:str, password:str)-> dict | str:
        try:
            query= sa.select(Company_Editor).options(selectinload(Company_Editor.projects), joinedload(Company_Editor.company)).where(Company_Editor.editor_email==email)

            async with self.db_session as session:
                editor = await session.scalar(query)
                if editor:
                    if self.hash.verify(editor.password, password):
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
                                    "coordinates": [
                                        {
                                            "latitude_longitude": coord.latitude_longitude,
                                            "target_material": coord.result_materiallist,
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

