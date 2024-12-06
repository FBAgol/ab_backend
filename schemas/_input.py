from pydantic import BaseModel


class companyInput(BaseModel):
    company_name: str
