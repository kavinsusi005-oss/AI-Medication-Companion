from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.medication_service import ensure_today_entries, get_due_medications

scheduler = BackgroundScheduler()

def check_due_medications():
    ensure_today_entries()
    due = get_due_medications()
    if due:
        print(f"[SCHEDULER] {len(due)} medication(s) currently due.")

def start_scheduler():
    ensure_today_entries()
    scheduler.add_job(check_due_medications, 'interval', minutes=1, id='check_due_meds', replace_existing=True)
    scheduler.start()

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
