from pydantic import BaseModel


class companyInput(BaseModel):
    company_name: str
    editor_email: str
    project_name: str
    date: str
