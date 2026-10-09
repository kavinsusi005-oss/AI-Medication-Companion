import os
from datetime import datetime
from backend.database.db import get_db, init_db

def seed_database():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM interaction_logs")
    cursor.execute("DELETE FROM medication_history")
    cursor.execute("DELETE FROM medications")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('medications', 'medication_history', 'interaction_logs')")

    sample_medications = [
        ("Metformin 500mg", "08:00", "daily", "After food", "500mg", "Diabetes management (Morning dose)"),
        ("Amlodipine 5mg", "08:00", "daily", "After food", "5mg", "Blood pressure control"),
        ("Aspirin 75mg", "14:00", "daily", "After food", "75mg", "Blood thinner"),
        ("Metformin 500mg", "20:00", "daily", "After food", "500mg", "Diabetes management (Evening dose)")
    ]

    for name, schedule_time, frequency, instruction, dosage, notes in sample_medications:
        cursor.execute("""
            INSERT INTO medications (name, schedule_time, frequency, instruction, dosage, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, schedule_time, frequency, instruction, dosage, notes))

    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT id, schedule_time FROM medications WHERE active = 1")
    meds = cursor.fetchall()
    
    for med in meds:
        cursor.execute("""
            INSERT INTO medication_history (medication_id, scheduled_date, scheduled_time, status)
            VALUES (?, ?, ?, 'PENDING')
        """, (med['id'], today, med['schedule_time']))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully with demo data.")
