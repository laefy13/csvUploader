

from typing import List
from pydantic import BaseModel
from models.aggregated_stats import AggregatedStatsModel

class PaginatedResponseModel(BaseModel):
    data: List[AggregatedStatsModel]
    paginate: dict