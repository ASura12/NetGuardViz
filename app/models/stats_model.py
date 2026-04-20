from pydantic import BaseModel

class StatsModel(BaseModel):
    total_logs: int
    total_alerts: int
    suspicious_percentage: float
