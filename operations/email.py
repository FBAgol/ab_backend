import smtplib
from email.mime.multipart import MIMEMultipart
from sqlalchemy.ext.asyncio import AsyncSession
from email.mime.text import MIMEText
from fastapi import  HTTPException
import sqlalchemy as sa
from uuid import UUID
from dotenv import load_dotenv
import os

from db.models import Telekom_Editor
from jwt_utils import get_user_id_from_token


load_dotenv()


class EmailOperations: 
    def __init__(self, db_session: AsyncSession)->None: 
        self.db_session = db_session


    async def send_email(self, token:str,from_email: str, to_email: str, subject: str, body: str):
        editor_id = UUID(get_user_id_from_token(token))
        if not editor_id:
            raise HTTPException(status_code=401, detail="Telekom Editor not found.")
        
        editor_query = sa.select(Telekom_Editor).where(Telekom_Editor.id == editor_id)
        async with self.db_session as session:
            editor = await session.scalar(editor_query)
            if not editor:
                raise HTTPException(status_code=401, detail="Telekom Editor not found.")

            password = os.getenv("EMAIL_PASSWORD")

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, password)

            # email content 
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()

