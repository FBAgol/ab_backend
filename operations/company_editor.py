from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Company_Editor
from db import Hash 
import sqlalchemy as sa
from sqlalchemy.orm import joinedload, selectinload
from convert_to_dict import to_dict



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

    async def login(self, email:str, password:str)-> Company_Editor | str:
        try:
            query= sa.select(Company_Editor).where(Company_Editor.editor_email==email)

            async with self.db_session as session:
                editor = await session.scalar(query)
                if editor:
                    if self.hash.verify(editor.password, password):
                        return to_dict(editor)
                    return "Invalid password."
                return "Invalid email."
        except Exception as e:
            raise Exception(f"Error logging in: {str(e)}")

