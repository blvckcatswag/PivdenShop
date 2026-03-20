import hashlib
import random

from backend.app.db import get_db


def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


SELLERS = [
    {"email": "oksana.koval@pivdenshop.ua", "phone": "+380501111111", "full_name": "Оксана Коваль", "password": "seller1pass"},
    {"email": "dmytro.shevchenko@pivdenshop.ua", "phone": "+380502222222", "full_name": "Дмитро Шевченко", "password": "seller2pass"},
    {"email": "iryna.bondarenko@pivdenshop.ua", "phone": "+380503333333", "full_name": "Ірина Бондаренко", "password": "seller3pass"},
    {"email": "oleksandr.melnyk@pivdenshop.ua", "phone": "+380504444444", "full_name": "Олександр Мельник", "password": "seller4pass"},
    {"email": "natalia.tkachenko@pivdenshop.ua", "phone": "+380505555555", "full_name": "Наталія Ткаченко", "password": "seller5pass"},
]

BUYERS = [
    {"email": "petro.ivanov@gmail.com", "phone": "+380661111111", "full_name": "Петро Іванов", "password": "buyerpass1"},
    {"email": "maria.sydorenko@gmail.com", "phone": "+380662222222", "full_name": "Марія Сидоренко", "password": "buyerpass2"},
    {"email": "andriy.kravchuk@gmail.com", "phone": "+380663333333", "full_name": "Андрій Кравчук", "password": "buyerpass3"},
]

ADMIN = {"email": "admin@pivdenshop.ua", "phone": "+380500000000", "full_name": "Адміністратор", "password": "admin123"}

PRODUCTS_BY_CATEGORY = {
    "Електроніка": [
        ("Смартфон Samsung Galaxy A54", "5.5'' AMOLED, 128GB, 6GB RAM", 12999.00),
        ("Навушники Sony WH-1000XM5", "Бездротові з активним шумопоглинанням", 9499.00),
        ("Ноутбук Lenovo IdeaPad 3", "15.6'' FHD, Ryzen 5, 8GB, 256GB SSD", 18999.00),
        ("Планшет Samsung Galaxy Tab A8", "10.5'' TFT, 64GB, Wi-Fi", 7999.00),
        ("Powerbank Xiaomi 20000mAh", "Швидка зарядка 22.5W, два USB", 899.00),
        ("Розумний годинник Amazfit GTS 4", "AMOLED, GPS, пульсоксиметр", 4299.00),
        ("Бездротова колонка JBL Flip 6", "IP67, 12 годин роботи", 3499.00),
        ("Клавіатура Logitech K380", "Bluetooth, мультипристрій", 1299.00),
        ("Веб-камера Logitech C920", "1080p, автофокус, мікрофон", 2199.00),
        ("USB-хаб Baseus 7-в-1", "HDMI, USB 3.0, SD, Type-C PD", 1099.00),
    ],
    "Одяг": [
        ("Футболка оверсайз біла", "100% бавовна, унісекс, розміри S-XXL", 599.00),
        ("Джинси Mom Fit", "Висока посадка, блакитний денім", 1299.00),
        ("Худі з капюшоном чорне", "Фліс всередині, кишеня-кенгуру", 899.00),
        ("Куртка демісезонна", "Водовідштовхувальна тканина, утеплена", 2499.00),
        ("Кросівки білі шкіряні", "Натуральна шкіра, ортопедична устілка", 2199.00),
        ("Шкарпетки набір 5 пар", "Бавовна 80%, різні кольори", 249.00),
        ("Сукня міді квіткова", "Віскоза, А-силует, довгий рукав", 1499.00),
        ("Светр в'язаний бежевий", "Вовна мериноса, оверсайз крій", 1799.00),
        ("Шапка біні чорна", "Подвійна в'язка, акрил", 349.00),
        ("Рюкзак міський 25л", "Водовідштовхувальний, відділення для ноутбука", 1199.00),
    ],
    "Дім": [
        ("Набір каструль 5 предметів", "Нержавіюча сталь, скляні кришки", 2899.00),
        ("Подушка ортопедична", "Memory foam, знімний чохол", 899.00),
        ("Комплект постільної білизни", "Сатин, 200x220, Євро розмір", 1599.00),
        ("Настільна лампа LED", "Три режими яскравості, USB зарядка", 749.00),
        ("Килимок для ванної", "Мікрофібра, нековзний, 50x80", 399.00),
        ("Набір рушників махрових", "3 штуки, 100% бавовна", 699.00),
        ("Ваза скляна декоративна", "Ручна робота, висота 30см", 549.00),
        ("Свічка ароматична соєва", "Ваніль та сандал, 40 годин горіння", 299.00),
        ("Органайзер для столу", "Бамбук, 5 відділень", 449.00),
        ("Плед флісовий 150x200", "Мікрофліс, однотонний сірий", 799.00),
    ],
    "Спорт": [
        ("Гантелі розбірні 2x10кг", "Вінілове покриття, хромований гриф", 1899.00),
        ("Килимок для йоги TPE 6мм", "Двошаровий, нековзний", 599.00),
        ("Скакалка швидкісна", "Підшипники, регульована довжина", 299.00),
        ("Фітнес-трекер Xiaomi Band 8", "Пульс, кроки, сон, водозахист", 1299.00),
        ("Пляшка для води 750мл", "Тритан, без BPA, з фільтром", 249.00),
        ("Рукавички для тренажерного залу", "Шкіра, фіксація зап'ястя", 449.00),
        ("Еспандер набір 5 штук", "Латекс, різний опір 5-25кг", 399.00),
        ("Ролик для преса", "Подвійне колесо, ручки з піни", 349.00),
        ("Спортивна сумка 40л", "Відділення для взуття, ремінь на плече", 899.00),
        ("Масажний м'яч", "Силікон, діаметр 8см, рельєфний", 199.00),
    ],
    "Краса": [
        ("Крем для обличчя зволожувальний", "Гіалуронова кислота, SPF 30", 449.00),
        ("Шампунь безсульфатний 400мл", "Для фарбованого волосся", 349.00),
        ("Набір пензлів для макіяжу 12шт", "Синтетичний ворс, чохол", 699.00),
        ("Парфумована вода 50мл", "Жіноча, квітково-фруктова композиція", 1299.00),
        ("Олія для волосся аргановa", "Натуральна, 100мл, без силіконів", 399.00),
        ("Маска для обличчя тканинна", "Набір 10 штук, різні екстракти", 299.00),
        ("Лак для нігтів гель", "UV/LED, стійкість 14 днів", 199.00),
        ("Бальзам для губ з SPF", "Масло ши та вітамін Е", 149.00),
        ("Дзеркало з підсвіткою LED", "Збільшення x5, сенсорна кнопка", 899.00),
        ("Набір для манікюру 7 предметів", "Нержавіюча сталь, шкіряний футляр", 549.00),
    ],
}


def run_seed():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] > 0:
        cur.close()
        return

    seller_ids = []
    for s in SELLERS:
        cur.execute(
            "INSERT INTO users (email, phone, password_hash, full_name, is_seller) "
            "VALUES (%s, %s, %s, %s, TRUE) RETURNING id",
            (s["email"], s["phone"], _hash(s["password"]), s["full_name"]),
        )
        seller_ids.append(cur.fetchone()[0])

    buyer_ids = []
    for b in BUYERS:
        cur.execute(
            "INSERT INTO users (email, phone, password_hash, full_name) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (b["email"], b["phone"], _hash(b["password"]), b["full_name"]),
        )
        buyer_ids.append(cur.fetchone()[0])

    cur.execute(
        "INSERT INTO users (email, phone, password_hash, full_name, is_admin) "
        "VALUES (%s, %s, %s, %s, TRUE) RETURNING id",
        (ADMIN["email"], ADMIN["phone"], _hash(ADMIN["password"]), ADMIN["full_name"]),
    )
    admin_id = cur.fetchone()[0]

    product_ids = []
    categories = list(PRODUCTS_BY_CATEGORY.keys())
    for i, (category, products) in enumerate(PRODUCTS_BY_CATEGORY.items()):
        seller_id = seller_ids[i % len(seller_ids)]
        for title, description, price in products:
            cur.execute(
                "INSERT INTO products (seller_id, title, description, price, category) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (seller_id, title, description, price, category),
            )
            product_ids.append(cur.fetchone()[0])

    order_data = [
        (buyer_ids[0], seller_ids[0], product_ids[0], "м. Одеса, вул. Дерибасівська, 1", "4242", "", "completed"),
        (buyer_ids[1], seller_ids[1], product_ids[10], "м. Київ, вул. Хрещатик, 22", "5554", "5555555555554444", "completed"),
        (buyer_ids[2], seller_ids[2], product_ids[20], "м. Львів, пл. Ринок, 5", "1234", "", "pending"),
        (buyer_ids[0], seller_ids[3], product_ids[30], "м. Харків, вул. Сумська, 10", "7890", "", "pending"),
    ]
    for buyer_id, seller_id, product_id, address, card_last4, card_plain, status in order_data:
        cur.execute(
            "INSERT INTO orders (buyer_id, seller_id, product_id, address, card_last4, card_number_plain, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (buyer_id, seller_id, product_id, address, card_last4, card_plain, status),
        )

    review_data = [
        (product_ids[0], buyer_ids[0], "Чудовий смартфон, рекомендую!", 5),
        (product_ids[0], buyer_ids[1], "Нормальний за свою ціну", 4),
        (product_ids[1], buyer_ids[2], "Шумоподавлення працює відмінно", 5),
        (product_ids[10], buyer_ids[0], "Якість тканини супер", 5),
        (product_ids[20], buyer_ids[1], "Каструлі важкуваті, але якісні", 4),
        (product_ids[30], buyer_ids[2], "Гантелі як на картинці", 5),
        (product_ids[40], buyer_ids[0], "Крем добре зволожує", 4),
        (product_ids[2], buyer_ids[1], "Ноутбук гальмує трохи", 3),
    ]
    for product_id, user_id, text, rating in review_data:
        cur.execute(
            "INSERT INTO reviews (product_id, user_id, text, rating) VALUES (%s, %s, %s, %s)",
            (product_id, user_id, text, rating),
        )

    cur.execute(
        "INSERT INTO chats (buyer_id, seller_id) VALUES (%s, %s) RETURNING id",
        (buyer_ids[0], seller_ids[0]),
    )
    chat1_id = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO chats (buyer_id, seller_id) VALUES (%s, %s) RETURNING id",
        (buyer_ids[1], seller_ids[1]),
    )
    chat2_id = cur.fetchone()[0]

    chat1_messages = [
        (chat1_id, buyer_ids[0], "Добрий день! Цікавить смартфон Samsung Galaxy A54"),
        (chat1_id, seller_ids[0], "Вітаю! Так, є в наявності. Можу відправити сьогодні"),
        (chat1_id, buyer_ids[0], "Супер, оплачу карткою. Мій номер картки 4242424242424242, можете списати?"),
        (chat1_id, seller_ids[0], "Дякую, замовлення оформлено!"),
    ]
    for chat_id, sender_id, text in chat1_messages:
        cur.execute(
            "INSERT INTO messages (chat_id, sender_id, text) VALUES (%s, %s, %s)",
            (chat_id, sender_id, text),
        )

    chat2_messages = [
        (chat2_id, buyer_ids[1], "Привіт! Футболка ще є?"),
        (chat2_id, seller_ids[1], "Так, є всі розміри!"),
        (chat2_id, buyer_ids[1], "Беру М, дякую"),
    ]
    for chat_id, sender_id, text in chat2_messages:
        cur.execute(
            "INSERT INTO messages (chat_id, sender_id, text) VALUES (%s, %s, %s)",
            (chat_id, sender_id, text),
        )

    db.commit()
    cur.close()


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from backend.app import create_app
    app = create_app()
    with app.app_context():
        run_seed()
        print("Seed-дані успішно завантажено!")
