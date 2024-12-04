from pydantic import BaseModel

class MedalistModel(BaseModel):
    name: str
    medal_type: str
    gender: str
    country: str
    country_code: str
    nationality: str
    medal_code: str
    medal_date: str
