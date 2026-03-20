from backend.app.db import get_db


def _get_role(is_seller, is_admin):
    if is_admin:
        return "admin"
    if is_seller:
        return "seller"
    return "buyer"


def create_user(email, phone, password_hash, **extra_fields):
    db = get_db()
    cur = db.cursor()

    columns = ["email", "phone", "password_hash"]
    values = [email, phone, password_hash]

    allowed_extra = ["full_name", "avatar_url", "is_seller", "is_admin", "is_verified", "bio"]
    for key in allowed_extra:
        if key in extra_fields:
            columns.append(key)
            values.append(extra_fields[key])

    cols_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(values))

    cur.execute(
        f"INSERT INTO users ({cols_str}) VALUES ({placeholders}) RETURNING id, email, phone, is_seller, is_admin",
        tuple(values),
    )
    row = cur.fetchone()
    cur.close()
    return {"id": row[0], "email": row[1], "phone": row[2], "role": _get_role(row[3], row[4])}


def find_user_by_email(email):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, email, phone, password_hash, is_seller, is_admin FROM users WHERE email = %s",
        (email,),
    )
    row = cur.fetchone()
    cur.close()
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "phone": row[2],
            "password_hash": row[3],
            "role": _get_role(row[4], row[5]),
        }
    return None
