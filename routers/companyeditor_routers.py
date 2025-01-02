from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from pydantic import ValidationError
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from operations.company_editor import CompanyEditorOperations
from db.engine import get_db
from schemas._input import company_editor


companyeditor_router = APIRouter()

@companyeditor_router.post("/registeration")
async def register_company_Editor(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    company_editor: company_editor,
)-> str:
    try:
        editor = await CompanyEditorOperations(db_session).registration(company_editor.secret_key, company_editor.email, company_editor.password)
        return editor
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")