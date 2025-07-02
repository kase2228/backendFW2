from pydantic import BaseModel

class EmployeeCreate(BaseModel):
    first_name: str
    middle_name: str = ""
    last_name: str
    position: str
    company_id: int
    site_id: int

class EmployeeDelete(BaseModel):
    id: int