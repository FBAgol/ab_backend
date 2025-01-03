from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Super_Admin, Company_Editor, Telekom_Editor, Company, Project, City, Street, City_Street, Coordinate, Notification
from db import Hash 
import sqlalchemy as sa
from sqlalchemy.orm import joinedload, selectinload


class CompanyEditorOperations: 
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session
        self.hash= Hash()

    async def registration (self, secret_key:str, email:str, password:str)-> Company_Editor | str:
        try:
            print("password is", password)
            query= sa.select(Company_Editor).where(Company_Editor.editor_email==email, Company_Editor.secret_key==secret_key)

            async with self.db_session as session:
                editor = await session.scalar(query)
                if editor:
                    if editor.password:
                        return "A password already exists for this editor."
                    editor.password = self.hash.bcrypt(password)
                    session.add(editor)
                    await session.commit()
                    return "Password set successfully."
                return "Invalid secret key or email."
        except Exception as e:
            raise Exception(f"Error creating company_editor: {str(e)}")
        

    async def login(self, email:str, password:str)-> Company_Editor | str:
        try:
            query= sa.select(Company_Editor).where(Company_Editor.editor_email==email)

            async with self.db_session as session:
                editor = await session.scalar(query)
                if editor:
                    if self.hash.verify(editor.password, password):
                        return editor
                    return "Invalid password."
                return "Invalid email."
        except Exception as e:
            raise Exception(f"Error logging in: {str(e)}")

"""

{
    "secret_key":"string456",
    "email":"max@baumax.de",
    "password":"maxbauman"
}
"""