
from typing import List
from pydantic import BaseModel
from models.medialist import MedalistModel

class AggregatedStatsModel(BaseModel):
    event: str
    discipline: str
    event_date: str
    medalists: List[MedalistModel]