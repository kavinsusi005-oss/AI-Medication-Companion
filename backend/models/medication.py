from pydantic import BaseModel
from typing import Optional

class MedicationCreate(BaseModel):
    name: str
    schedule_time: str
    frequency: str = 'daily'
    instruction: str = ''
    dosage: str = ''
    notes: str = ''

class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    schedule_time: Optional[str] = None
    frequency: Optional[str] = None
    instruction: Optional[str] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[int] = None

class MedicationResponse(BaseModel):
    id: int
    name: str
    schedule_time: str
    frequency: str
    instruction: str
    dosage: str
    notes: str
    active: int
    created_at: str

class InteractionRequest(BaseModel):
    text: str
    medication_history_id: Optional[int] = None

class InteractionResponse(BaseModel):
    response: str
    language: str
    intent: str
    medication_history_id: Optional[int] = None
    action: str
    delay_minutes: Optional[int] = None

class HistoryResponse(BaseModel):
    id: int
    medication_id: int
    medication_name: str
    scheduled_date: str
    scheduled_time: str
    status: str
    action_time: Optional[str] = None
    user_response: str
    detected_language: str
    created_at: str
