from fastapi import APIRouter
from backend.models.medication import MedicationCreate, MedicationUpdate
from backend.services.medication_service import (
    get_all_medications, get_medication_by_id, add_medication,
    update_medication, delete_medication, get_due_medications
)

router = APIRouter(prefix="/medications", tags=["medications"])

@router.get("/")
def list_medications():
    return get_all_medications()

@router.post("/")
def create_medication(med: MedicationCreate):
    med_id = add_medication(med.dict())
    return {"id": med_id, "message": "Medication created successfully"}

@router.put("/{med_id}")
def edit_medication(med_id: int, med: MedicationUpdate):
    update_medication(med_id, med.dict(exclude_unset=True))
    return {"message": "Medication updated successfully"}

@router.delete("/{med_id}")
def remove_medication(med_id: int):
    delete_medication(med_id)
    return {"message": "Medication deleted successfully"}

@router.get("/due")
def list_due_medications():
    return get_due_medications()
