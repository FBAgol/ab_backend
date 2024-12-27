from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Super_Admin, Company_Editor, Telekom_Editor, Company, Project, City, Street, City_Street, Coordinate, Notification

class SuperAdminOperations:
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session
    async def create_company_editor(self, email:str, secret_key:str, suer_admin_id:str, company_id:str)-> Company_Editor:
        editor = Company_Editor(editor_email=email, secret_key=secret_key, super_admin_id=suer_admin_id, company_id=company_id)
        async with self.db_session() as session:
            session.add(editor)
            await session.commit()
            #await session.refresh(editor)

    async def create_telekom_editor(self, email:str, secret_key:str, super_admin_id:str)-> Telekom_Editor:
        editor = Telekom_Editor(email=email, secret_key=secret_key, super_admin_id=super_admin_id)
        async with self.db_session() as session:
            session.add(editor)
            await session.commit()
            #await session.refresh(editor)

    async def create_company(self, company_name:str)-> Company:
        company = Company(company_name=company_name)
        async with self.db_session() as session:
            session.add(company)
            await session.commit()
            #await session.refresh(company)
    
    async def create_project(self, priject_name:str, company_id:str, telekom_editor_id:str, city_id:str)-> Project:
        project = Project(project_name=priject_name, company_id=company_id, telekom_editor_id=telekom_editor_id, city_id=city_id)
        async with self.db_session() as session:
            session.add(project)
            await session.commit()
            #await session.refresh(project)

    async def create_city(self, city_name:str)-> City:
        city = City(city_name=city_name)
        async with self.db_session() as session:
            session.add(city)
            await session.commit()
            #await session.refresh(city)
    async def create_city_street(self, city_id:str, street_id:str)-> City_Street:
        city_street = City_Street(city_id=city_id, street_id=street_id)
        async with self.db_session() as session:
            session.add(city_street)
            await session.commit()
            #await session.refresh(city_street)
    
    async def create_street(self, street_name:str)-> Street:
        street = Street(street_name=street_name)
        async with self.db_session() as session:
            session.add(street)
            await session.commit()
            #await session.refresh(street)

    async def create_coord(self, coord_number:int, target_material:str, street_id:str)-> Coordinate:
        coord = Coordinate(coord_number=coord_number, target_material=target_material, street_id=street_id)
        async with self.db_session() as session:
            session.add(coord)
            await session.commit()
            #await session.refresh(coord)

    