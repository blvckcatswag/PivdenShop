from backend.app.db import get_db


def create_notification(user_id, text):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO notifications (user_id, text) VALUES (%s, %s) RETURNING id",
        (user_id, text),
    )
    nid = cur.fetchone()[0]
    cur.close()
    return nid


def get_notifications(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, text, is_read, created_at FROM notifications "
        "WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    return [
        {
            "id": r[0],
            "text": r[1],
            "is_read": r[2],
            "created_at": r[3].isoformat() if r[3] else None,
        }
        for r in rows
    ]


def get_unread_count(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE",
        (user_id,),
    )
    count = cur.fetchone()[0]
    cur.close()
    return count
