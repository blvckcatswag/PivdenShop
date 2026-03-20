from backend.app.db import get_db


def add_to_cart(user_id, product_id, quantity):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO cart_items (user_id, product_id, quantity) "
        "VALUES (%s, %s, %s) RETURNING id",
        (user_id, product_id, quantity),
    )
    item_id = cur.fetchone()[0]
    cur.close()
    return item_id


def get_cart(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT ci.id, ci.product_id, ci.quantity, p.title, p.price, p.image_url, p.category, "
        "u.full_name "
        "FROM cart_items ci "
        "JOIN products p ON ci.product_id = p.id "
        "JOIN users u ON p.seller_id = u.id "
        "WHERE ci.user_id = %s ORDER BY ci.added_at DESC",
        (user_id,),
    )
    items = []
    total = 0
    for row in cur.fetchall():
        subtotal = float(row[4]) * row[2]
        total += subtotal
        items.append({
            "id": row[0],
            "product_id": row[1],
            "quantity": row[2],
            "title": row[3],
            "price": float(row[4]),
            "image_url": row[5],
            "category": row[6],
            "seller_name": row[7],
            "subtotal": subtotal,
        })
    cur.close()
    return items, total


def remove_from_cart(user_id, item_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM cart_items WHERE id = %s AND user_id = %s",
        (item_id, user_id),
    )
    cur.close()


def clear_cart(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
    cur.close()


def get_cart_count(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM cart_items WHERE user_id = %s",
        (user_id,),
    )
    count = cur.fetchone()[0]
    cur.close()
    return int(count)
