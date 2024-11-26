import sqlite3

connection = sqlite3.connect('test.db')
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    field_value TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS client_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    field_value TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")
connection.commit()
cursor.close()
connection.close()


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
    
    def open_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def find_user(self, username):
        self.open_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE name = ?", (username,))
        result = cur.fetchone()
        cur.close()
        return result

    def execute_transaction(self, operations):
        self.open_connection()
        cur = self.conn.cursor()
        try:
            for op in operations:
                cur.execute(*op)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

class User:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_user(self, name, role):
        self.db.open_connection()
        cur = self.db.conn.cursor()
        cur.execute("INSERT INTO users (name, role) VALUES (?, ?)", (name, role))
        self.db.conn.commit()
        cur.close()

    def get_user_id(self, user_id):
        self.db.open_connection()
        cur = self.db.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cur.fetchone()
        cur.close()
        return result

    def delete_user(self, user_id):
        self.db.open_connection()
        cur = self.db.conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.db.conn.commit()
        cur.close()

class Administrator(User):
    def add_admin_info(self, user_id, info):
        self.db.open_connection()
        cur = self.db.conn.cursor()
        cur.execute("INSERT INTO admin_fields (user_id, field_value) VALUES (?, ?)", (user_id, info))
        self.db.conn.commit()
        cur.close()

class Client(User):
    def add_client_info(self, user_id, info):
        self.db.open_connection()
        cur = self.db.conn.cursor()
        cur.execute("INSERT INTO client_fields (user_id, field_value) VALUES (?, ?)", (user_id, info))
        self.db.conn.commit()
        cur.close()


db = DatabaseManager("test.db")

user_manager = User(db)
user_manager.add_user("Игорь", "Клиент")
user_manager.add_user("Петр", "Клиент")

user = user_manager.get_user_id(1)
print(user)

user_manager.delete_user(1)

admin_manager = Administrator(db)
admin_manager.add_user("Шоха", "Администратор")
admin_manager.add_admin_info(3, "Управляет системой")

client_manager = Client(db)
client_manager.add_user("Максим", "Клиент")
client_manager.add_client_info(4, "Постоянный клиент")

db.close_connection()