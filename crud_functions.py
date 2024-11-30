import sqlite3

class DataError(Exception):
    pass

def initiate_db():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price INT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            balance INTEGER NOT NULL
        )
        ''')
        connection.commit()
    put_products()

def put_products():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products")
        if cursor.fetchone()[0] == 0:
            for i in range(1, 5):
                cursor.execute('''
                INSERT INTO Products(title, description, price)
                VALUES(?, ?, ?)
                ''', (f"Продукт{i}", f"Описание{i}", i * 100))
        connection.commit()

def get_connection():
    return sqlite3.connect('data_products.db')

    # данные из таблицы Products сохраняем в переменную all_data
def get_all_products():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Products")
        all_data = cursor.fetchall()
    return all_data

def add_user(username, email, age, balance=1000):
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            # Проверяем, существует ли пользователь
            cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise DataError(f'Пользователь {username} уже есть в базе.')
            # Создаем нового пользователя
            cursor.execute('''
            INSERT INTO Users(username, email, age, balance) VALUES(?, ?, ?, ?)
            ''', (username, email, age, balance))
            connection.commit()
        except sqlite3.IntegrityError:
            raise DataError(f"Пользователь {username} уже существует.")

def is_included(username):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        return cursor.fetchone() is not None










