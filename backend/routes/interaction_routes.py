from fastapi import APIRouter
from backend.models.medication import InteractionRequest, InteractionResponse
from backend.services.ai_service import process_message
from backend.services.medication_service import (
    get_due_medications, update_history_status, log_interaction,
    create_history_entry, get_all_medications, get_today_schedule
)
from datetime import datetime

router = APIRouter(tags=["interactions"])

@router.post("/interact", response_model=InteractionResponse)
def interact(req: InteractionRequest):
    due = get_due_medications()
    if due:
        context = ", ".join([f"{m['name']} ({m.get('dosage', '')}) - {m.get('instruction', '')}" for m in due])
    else:
        all_meds = get_all_medications()
        if all_meds:
            context = ", ".join([f"{m['name']} ({m.get('dosage', '')})" for m in all_meds])
        else:
            context = "No medications scheduled."
    
    ai_resp = process_message(req.text, context)
    intent = ai_resp.get('intent', 'UNKNOWN')
    detected_lang = ai_resp.get('language', 'english')
    system_response = ai_resp.get('response', '')
    
    history_id = req.medication_history_id
    if not history_id and intent in ['MEDICINE_TAKEN', 'REMIND_LATER', 'NOT_TAKEN']:
        today_sched = get_today_schedule()
        pending_items = [item for item in today_sched if item.get('status') in ['PENDING', None, 'DELAYED']]
        if pending_items:
            history_id = pending_items[0].get('history_id')
            if not history_id:
                today = datetime.now().strftime('%Y-%m-%d')
                history_id = create_history_entry(
                    pending_items[0]['id'], 
                    today, 
                    pending_items[0]['schedule_time']
                )

    if history_id:
        if intent == 'MEDICINE_TAKEN':
            update_history_status(history_id, 'TAKEN', req.text, detected_lang)
        elif intent == 'REMIND_LATER':
            update_history_status(history_id, 'DELAYED', req.text, detected_lang)
        elif intent == 'NOT_TAKEN':
            update_history_status(history_id, 'NEEDS_ATTENTION', req.text, detected_lang)
            
    log_interaction(history_id, req.text, system_response, detected_lang, intent)
    
    return InteractionResponse(
        response=system_response,
        language=detected_lang,
        intent=intent,
        medication_history_id=history_id,
        action=intent,
        delay_minutes=ai_resp.get('delay_minutes')
    )

@router.post("/trigger-reminder")
def trigger_reminder():
    due = get_due_medications()
    med = due[0] if due else None
    if not med:
        meds = get_all_medications()
        if meds:
            med = meds[0]
            
    if not med:
        return {"message": "No active medications found"}
        
    today = datetime.now().strftime('%Y-%m-%d')
    history_id = create_history_entry(med['id'], today, med['schedule_time'])
    
    instruction = med.get('instruction', '')
    dosage = med.get('dosage', '')
    reminder_text = f"It's time to take your {med['name']} ({dosage}). {instruction}".strip()
    
    return {
        "medication": med,
        "history_id": history_id,
        "reminder_text": reminder_text,
        "language": "english"
    }
