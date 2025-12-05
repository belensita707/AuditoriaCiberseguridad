import sqlite3
from werkzeug.security import generate_password_hash
import os

# Eliminar base anterior si existe (opcional pero recomendado)
if os.path.exists("example.db"):
    os.remove("example.db")
    print("Base de datos antigua eliminada.")

# Crear la conexión
conn = sqlite3.connect("example.db")
c = conn.cursor()

# Crear tabla de usuarios
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Crear tabla de comentarios
c.execute('''
    CREATE TABLE comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Insertar usuarios con contraseña segura (hash + salt)
admin_pass = generate_password_hash("password123")
user_pass  = generate_password_hash("usuario123")

c.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ("admin", admin_pass, "admin")
)

c.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ("user", user_pass, "user")
)

# Guardar cambios
conn.commit()
conn.close()

print("Base de datos creada con éxito.")
print("Usuarios disponibles:")
print(" - admin / password123")
print(" - user / usuario123")
