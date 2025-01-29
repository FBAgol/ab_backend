from fastapi import APIRouter,Depends, Header, HTTPException
from typing import Any, Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from schemas._input import EmailRequest
from operations.email import EmailOperations

email_router = APIRouter()

@email_router.post("/send_email")
async def send_email_endpoint(db_session: Annotated[AsyncSession, Depends(get_db)],request: EmailRequest, Authorization: str=Header(...)):
    email= await EmailOperations(db_session).send_email(Authorization,request.from_email,request.to_email, request.subject, request.body)
    try:
        if not email:
            raise HTTPException(status_code=404, detail="Email not sent.")
        return {"message": "Email sent successfull."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")