import sqlite3
import pandas as pd
import os
from contextlib import contextmanager

DB_NAME = "diyetisyen.db"

@contextmanager
def get_db_connection():
    """Veri tabanına güvenli bağlantı açıp kapatır."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Gerekli tüm tabloları oluşturur ve varsa CSV'den verileri yükler."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Tabloları oluştur (SERIAL yerine INTEGER PRIMARY KEY AUTOINCREMENT)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                meal_time TEXT,
                unit TEXT,
                calories REAL DEFAULT 0,
                protein REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                allergens TEXT,
                notes TEXT
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS diets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                target_calories REAL,
                target_protein REAL,
                target_fat REAL,
                target_carbs REAL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS diet_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                diet_id INTEGER REFERENCES diets(id) ON DELETE CASCADE,
                food_id INTEGER REFERENCES foods(id) ON DELETE CASCADE,
                meal_time TEXT
            );
        """)
        conn.commit()

        # Eğer tablo boşsa ve foods.csv dosyası varsa, verileri içeri aktar!
        cur.execute("SELECT COUNT(*) FROM foods")
        count = cur.fetchone()[0]
        
        if count == 0 and os.path.exists("foods.csv"):
            print("foods.csv dosyası bulundu, besin verileri SQLite'a aktarılıyor...")
            df = pd.read_csv("foods.csv")
            # CSV'deki verileri doğrudan veritabanına yaz
            df.to_sql('foods', conn, if_exists='append', index=False)
            print(f"{len(df)} adet besin başarıyla aktarıldı!")

def get_all_foods():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM foods ORDER BY id DESC", conn)

def add_food(name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes):
    with get_db_connection() as conn:
        cur = conn.cursor()
        # PostgreSQL'deki %s yerine SQLite'da ? kullanılır
        cur.execute("""
            INSERT INTO foods (name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes))
        conn.commit()

def get_all_clients():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM clients ORDER BY name ASC", conn)

def add_client(name):
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO clients (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def delete_food(food_id):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM foods WHERE id = ?", (food_id,))
        conn.commit()

def update_food(food_id, name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE foods 
            SET name=?, category=?, meal_time=?, unit=?, calories=?, protein=?, fat=?, carbs=?, allergens=?, notes=?
            WHERE id=?
        """, (name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes, food_id))
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Harika! Veri tabanı ve tablolar başarıyla oluşturuldu (SQLite).")