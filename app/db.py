import sqlite3
from typing import Optional

from app.config import load_config
from app.texts import PRODUCTS

config = load_config()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            photo TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER NOT NULL,
            telegram_username TEXT,
            customer_id_code TEXT NOT NULL,
            full_name TEXT NOT NULL,
            product_slug TEXT NOT NULL,
            product_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            country TEXT NOT NULL,
            region TEXT NOT NULL,
            address TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for slug, data in PRODUCTS.items():
        cur.execute("""
            INSERT OR IGNORE INTO products (slug, name, stock, photo)
            VALUES (?, ?, ?, ?)
        """, (slug, data["name"], data["stock"], data["photo"]))

    conn.commit()
    conn.close()


def get_all_products() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT slug, name, stock, photo FROM products ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product(slug: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT slug, name, stock, photo FROM products WHERE slug = ?", (slug,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def decrease_stock(slug: str, amount: int = 1) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT stock FROM products WHERE slug = ?", (slug,))
    row = cur.fetchone()

    if not row or row["stock"] < amount:
        conn.close()
        return False

    cur.execute(
        "UPDATE products SET stock = stock - ? WHERE slug = ?",
        (amount, slug)
    )
    conn.commit()
    conn.close()
    return True


def increase_stock(slug: str, amount: int = 1) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE products SET stock = stock + ? WHERE slug = ?",
        (amount, slug)
    )
    conn.commit()
    conn.close()


def create_order(
    telegram_user_id: int,
    telegram_username: str | None,
    customer_id_code: str,
    full_name: str,
    product_slug: str,
    product_name: str,
    phone: str,
    country: str,
    region: str,
    address: str,
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (
            telegram_user_id, telegram_username, customer_id_code, full_name,
            product_slug, product_name, phone, country, region, address
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        telegram_user_id,
        telegram_username,
        customer_id_code,
        full_name,
        product_slug,
        product_name,
        phone,
        country,
        region,
        address,
    ))
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def get_order(order_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_order_status(order_id: int, status: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def get_all_user_ids() -> list[int]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT telegram_user_id FROM orders")
    rows = cur.fetchall()
    conn.close()
    return [row["telegram_user_id"] for row in rows]
