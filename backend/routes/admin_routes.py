from fastapi import APIRouter
from backend.services.medication_service import get_today_schedule, get_history, get_interaction_logs
from backend.seed_data import seed_database
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/schedule/today")
def today_schedule():
    return get_today_schedule()

@router.get("/history")
def history(date: Optional[str] = None):
    return get_history(date)

@router.get("/interactions")
def interactions():
    return get_interaction_logs()

@router.post("/seed")
def seed_db():
    seed_database()
    return {"message": "Database seeded successfully"}
