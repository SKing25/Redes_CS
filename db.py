import sqlite3

DB_NAME = 'productos.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def obtener_productos():
    conn = sqlite3.connect(DB_NAME)
    productos = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()
    return productos

def crear_producto(nombre, cantidad, precio):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)',
                 (nombre, cantidad, precio))
    conn.commit()
    conn.close()

def eliminar_producto(id_producto):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('DELETE FROM productos WHERE id = ?', (id_producto,))
    conn.commit()
    conn.close()

def modificar_producto(id_producto, nombre, cantidad, precio):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('UPDATE productos SET nombre = ?, cantidad = ?, precio = ? WHERE id = ?',
                 (nombre, cantidad, precio, id_producto))
    conn.commit()
    conn.close()
