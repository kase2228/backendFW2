from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    position: str
    company_id: int
    site_id: int

class EmployeeDelete(BaseModel):
    id: int
