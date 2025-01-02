from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Super_Admin, Company_Editor, Telekom_Editor, Company, Project, City, Street, City_Street, Coordinate, Notification
from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import joinedload, selectinload
from uuid import UUID

class SuperAdminOperations:
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session

    async def create_superadmin(self, email:str, password:str)-> Super_Admin:
        try:
            query = sa.select(Super_Admin).options(selectinload(Super_Admin.companys), selectinload(Super_Admin.telekom_editors)).where(Super_Admin.email == email)
        
            async with self.db_session as session:
                
                superadmin = await session.scalar(query)
                if superadmin:
                    return superadmin
                else:
                    superadmin = Super_Admin(email= email, password= password)
                    session.add(superadmin)
                    await session.commit()
                    #await session.refresh(company)
                    superadmin = await session.scalar(query)
                    return superadmin
        except Exception as e:
            raise Exception(f"Error creating superadmin: {str(e)}")
        
            
    async def create_company_editor(self, email:str, secret_key:str, company_id:UUID)-> Company_Editor:
        try:
            query= sa.select(Company_Editor).options(selectinload(Company_Editor.projects), joinedload(Company_Editor.company)).where(Company_Editor.editor_email==email)

            async with self.db_session as session:
                editor = await session.scalar(query)
                if editor:
                    return editor
                else:
                    editor = Company_Editor(company_id=company_id, editor_email=email, secret_key=secret_key)
                    session.add(editor)
                    await session.commit()
                    #await session.refresh(editor)
                    editor = await session.scalar(query)
                    return editor
        except Exception as e:
            raise Exception(f"Error creating company_editor: {str(e)}")
        

    async def create_telekom_editor(self, email:str, secret_key:str, super_admin_id:UUID)-> Telekom_Editor:
        try:
            query= sa.select(Telekom_Editor).options(selectinload(Telekom_Editor.notifications),joinedload(Telekom_Editor.super_admin), selectinload(Telekom_Editor.projects)).where(Telekom_Editor.email==email)
        
            async with self.db_session as session:
                editor= await session.scalar(query)
                if editor:
                    return editor
                else:
                    editor = Telekom_Editor(super_admin_id=super_admin_id, email=email, secret_key=secret_key)
                    session.add(editor)
                    await session.commit()
                    #await session.refresh(editor)
                    editor= await session.scalar(query)
                    return editor
        except Exception as e:
            raise Exception(f"Error creating telekom_editor: {str(e)}")
        
            

    async def create_company(self, company_name:str, super_admin_id:UUID)-> Company:
        try:
            query = sa.select(Company).options(selectinload(Company.company_editors), joinedload(Company.super_admin)).where(Company.company_name == company_name)
        
            async with self.db_session as session:
                company = await session.scalar(query)
                if company:
                    return company
                else:
                    company = Company(company_name=company_name, super_admin_id=super_admin_id)
                    session.add(company)
                    await session.commit()
                    #await session.refresh(company)
                    company = await session.scalar(query)
                    return company
                
        except Exception as e:
            raise Exception(f"Error creating company: {str(e)}")
        
        

    
    async def create_project(self, priject_name:str, company_editor_id:UUID, telekom_editor_id:UUID, city_id:UUID)-> Project:
        try:
            query = sa.select(Project).options( joinedload(Project.city),joinedload(Project.telekom_editor), joinedload(Project.company_editor)).where(Project.project_name == priject_name, Project.city_id == city_id)
            
            async with self.db_session as session:
                project= await session.scalar(query)
                if project:
                    return project
                else:
                    project = Project(project_name=priject_name, company_editor_id=company_editor_id, telekom_editor_id=telekom_editor_id, city_id=city_id)
                    session.add(project)
                    await session.commit()
                    #await session.refresh(project)
                    project = await session.scalar(query)
                    return project
        except Exception as e:
            raise Exception(f"Error creating project: {str(e)}")
        


    async def create_city(self, name: str) -> City:
        try:
            # nutzen wir joinedload, um auch die "projects"-Beziehung zu laden
            query = sa.select(City).options( selectinload(City.projects),selectinload(City.city_streets)).where(City.city_name == name)
            
            async with self.db_session as session:
                city = await session.scalar(query)
                if city:
                    return city
                else:
                    city = City(city_name=name)
                    session.add(city)
                    await session.commit()
                    #await session.refresh(city)
                    # um nicht diese lazy loading zu passieren, dann sollen wir wieder die nächste Zeile schreiben damit session offen bleibt
                    city = await session.scalar(query)
                    return city
        except Exception as e:
            print(f"Error: {str(e)}")
            raise Exception(f"Error creating city: {str(e)}")

            
            
    async def create_city_street(self, city_id:UUID, street_id:UUID)-> City_Street:
        try:
            query =  sa.select(City_Street).options(joinedload(City_Street.city), joinedload(City_Street.street)).where(City_Street.street_id == street_id)
        
            async with self.db_session as session:

                city_street = await session.scalar(query) 
                if city_street: 
                    return city_street
                else:  
                    city_street = City_Street(city_id=city_id, street_id=street_id)
                    session.add(city_street)
                    await session.commit()
                    city_street= await session.scalar(query)
                    return city_street
                    
        except Exception as e:
            raise Exception(f"Error creating city_street: {str(e)}")
        
                
    
    async def create_street(self, street_name:str)-> Street:
        try:
            query = sa.select(Street).options(selectinload(Street.city_streets), selectinload(Street.coordinates)).where(Street.street_name == street_name)
        
            async with self.db_session as session:
                street = await session.scalar(query)
                if street:
                    return street
                else:
                    street = Street(street_name=street_name)
                    session.add(street)
                    await session.commit()
                    #await session.refresh(street)
                    street = await session.scalar(query)
                    return street
        except Exception as e:
            raise Exception(f"Error creating Street: {str(e)}")
        

    async def create_coord(self, coord_number:List[float], target_material:str, street_id:UUID)-> Coordinate:
        try:
            query = sa.select(Coordinate).options(joinedload(Coordinate.notification), joinedload(Coordinate.street)).where(Coordinate.latitude_longitude == coord_number, Coordinate.street_id == street_id)
            async with self.db_session as session:
                coord= await session.scalar(query)
                if coord:
                    return coord
                else:
                    coord = Coordinate(latitude_longitude=coord_number, result_materiallist=target_material, street_id=street_id)
                    session.add(coord)
                    await session.commit()
                    #await session.refresh(coord)
                    coord= await session.scalar(query)
                    return coord

                    
        except Exception as e:
            raise Exception(f"Error creating Coord: {str(e)}")
        

    