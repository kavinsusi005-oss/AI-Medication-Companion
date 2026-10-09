from datetime import datetime, timedelta
from backend.database.db import get_db

def get_all_medications():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medications WHERE active = 1")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_medication_by_id(med_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medications WHERE id = ? AND active = 1", (med_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_medication(data: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medications (name, schedule_time, frequency, instruction, dosage, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data.get('name'), data.get('schedule_time'), data.get('frequency', 'daily'), 
          data.get('instruction', ''), data.get('dosage', ''), data.get('notes', '')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_medication(med_id, data: dict):
    conn = get_db()
    cursor = conn.cursor()
    updates = []
    values = []
    for k, v in data.items():
        if v is not None:
            updates.append(f"{k} = ?")
            values.append(v)
    if updates:
        values.append(med_id)
        cursor.execute(f"UPDATE medications SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    conn.close()

def delete_medication(med_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE medications SET active = 0 WHERE id = ?", (med_id,))
    conn.commit()
    conn.close()

def get_due_medications():
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    window_end = (now + timedelta(minutes=30)).strftime('%H:%M')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM medications 
        WHERE active = 1 AND schedule_time >= ? AND schedule_time <= ?
    """, (current_time, window_end))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_today_schedule():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, mh.status, mh.id as history_id, mh.action_time
        FROM medications m
        LEFT JOIN medication_history mh ON m.id = mh.medication_id AND mh.scheduled_date = ?
        WHERE m.active = 1
    """, (today,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_history_entry(medication_id, scheduled_date, scheduled_time):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medication_history (medication_id, scheduled_date, scheduled_time, status)
        VALUES (?, ?, ?, 'PENDING')
    """, (medication_id, scheduled_date, scheduled_time))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_history_status(history_id, status, user_response='', detected_language=''):
    conn = get_db()
    cursor = conn.cursor()
    action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        UPDATE medication_history 
        SET status = ?, action_time = ?, user_response = ?, detected_language = ?
        WHERE id = ?
    """, (status, action_time, user_response, detected_language, history_id))
    conn.commit()
    conn.close()

def get_history(date_filter=None):
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT mh.*, m.name as medication_name 
        FROM medication_history mh
        JOIN medications m ON mh.medication_id = m.id
    """
    params = ()
    if date_filter:
        query += " WHERE mh.scheduled_date = ?"
        params = (date_filter,)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_interaction_logs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interaction_logs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def log_interaction(history_id, user_msg, system_response, language, intent):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interaction_logs (medication_history_id, user_message, system_response, detected_language, detected_intent)
        VALUES (?, ?, ?, ?, ?)
    """, (history_id, user_msg, system_response, language, intent))
    conn.commit()
    conn.close()

def ensure_today_entries():
    today = datetime.now().strftime('%Y-%m-%d')
    meds = get_all_medications()
    
    conn = get_db()
    cursor = conn.cursor()
    for med in meds:
        cursor.execute("""
            SELECT id FROM medication_history 
            WHERE medication_id = ? AND scheduled_date = ?
        """, (med['id'], today))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO medication_history (medication_id, scheduled_date, scheduled_time, status)
                VALUES (?, ?, ?, 'PENDING')
            """, (med['id'], today, med['schedule_time']))
    conn.commit()
    conn.close()
