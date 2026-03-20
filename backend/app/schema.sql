CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) DEFAULT '',
    avatar_url TEXT DEFAULT '',
    is_seller BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    bio TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    price NUMERIC(10, 2) NOT NULL,
    category VARCHAR(100) DEFAULT '',
    image_url TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL REFERENCES users(id),
    seller_id INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    address TEXT DEFAULT '',
    card_last4 VARCHAR(4) DEFAULT '',
    card_number_plain TEXT DEFAULT '',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    text TEXT DEFAULT '',
    rating INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL REFERENCES users(id),
    seller_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES chats(id),
    sender_id INTEGER NOT NULL REFERENCES users(id),
    text TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS flags (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    vuln_id VARCHAR(50) NOT NULL,
    flag_value VARCHAR(100) NOT NULL,
    found_at TIMESTAMP DEFAULT NOW()
);

DO $$ BEGIN
    ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT DEFAULT '';
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;
