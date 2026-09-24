import psycopg2
import pandas as pd
from contextlib import contextmanager

# Kendi PostgreSQL şifreni buraya yazmayı unutma!
DB_HOST = "localhost"
DB_NAME = "diyetisyen_db"
DB_USER = "postgres"
DB_PASS = "123456" 
DB_PORT = "5432"

@contextmanager
def get_db_connection():
    """Veri tabanına güvenli bağlantı açıp kapatır."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Gerekli tüm tabloları oluşturur."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS foods (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    meal_time VARCHAR(50),
                    unit VARCHAR(20),
                    calories NUMERIC(6,2) DEFAULT 0,
                    protein NUMERIC(6,2) DEFAULT 0,
                    fat NUMERIC(6,2) DEFAULT 0,
                    carbs NUMERIC(6,2) DEFAULT 0,
                    allergens VARCHAR(100),
                    notes TEXT
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS diets (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    target_calories NUMERIC(6,2),
                    target_protein NUMERIC(6,2),
                    target_fat NUMERIC(6,2),
                    target_carbs NUMERIC(6,2)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS diet_items (
                    id SERIAL PRIMARY KEY,
                    diet_id INTEGER REFERENCES diets(id) ON DELETE CASCADE,
                    food_id INTEGER REFERENCES foods(id) ON DELETE CASCADE,
                    meal_time VARCHAR(50)
                );
            """)
            
            conn.commit()

def get_all_foods():
    """Veritabanındaki tüm besinleri tablo formatında (DataFrame) çeker."""
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM foods ORDER BY id DESC", conn)

def add_food(name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes):
    """Veritabanına yeni bir besin ekler."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO foods (name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes))
            conn.commit()

def get_all_clients():
    """Veritabanındaki tüm danışanları alfabetik sırayla çeker."""
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM clients ORDER BY name ASC", conn)

def add_client(name):
    """Sisteme yeni bir danışan ekler. Aynı isim varsa hata vermemesi için kontrol yapar."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO clients (name) VALUES (%s)", (name,))
                conn.commit()
                return True
            except psycopg2.IntegrityError:
                conn.rollback() 
                return False

if __name__ == "__main__":
    init_db()
    print("Harika! Veri tabanı ve tablolar başarıyla oluşturuldu.")

def delete_food(food_id):
    """Veritabanından besini siler."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM foods WHERE id = %s", (food_id,))
            conn.commit()

def update_food(food_id, name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes):
    """Mevcut bir besinin bilgilerini günceller."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE foods 
                SET name=%s, category=%s, meal_time=%s, unit=%s, calories=%s, protein=%s, fat=%s, carbs=%s, allergens=%s, notes=%s
                WHERE id=%s
            """, (name, category, meal_time, unit, calories, protein, fat, carbs, allergens, notes, food_id))
            conn.commit()