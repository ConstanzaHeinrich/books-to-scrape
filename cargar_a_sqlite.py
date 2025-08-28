import sqlite3
import json

JSON_FILE = "books_data_completo.json" #de aca salen los datos scrapeados
DB_FILE = "libreria.db" #aca se crea y se guarda la base de datos

# --Conexión ---
conexion = sqlite3.connect(DB_FILE) #Abre/crea libreria.db
cursor = conexion.cursor() #con el que se ejecuta los comandos de sql

# --- Crear tablas ---
cursor.execute("DROP TABLE IF EXISTS libro_autor")
cursor.execute("DROP TABLE IF EXISTS autores")
cursor.execute("DROP TABLE IF EXISTS libros")

cursor.execute("""
CREATE TABLE libros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    precio TEXT,
    disponibilidad TEXT,
    estrellas TEXT,
    descripcion TEXT,
    imagen_url TEXT,
    categoria TEXT
)
""")

cursor.execute("""
CREATE TABLE autores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE libro_autor (
    libro_id INTEGER,
    autor_id INTEGER,
    PRIMARY KEY (libro_id, autor_id),
    FOREIGN KEY (libro_id) REFERENCES libros(id),
    FOREIGN KEY (autor_id) REFERENCES autores(id)
)
""")

conexion.commit() #Guarda en disco los cambios del esquema

# --- Cargar datos desde JSON ---
with open(JSON_FILE, "r", encoding="utf-8") as f: #Abre el archivo JSON y lo convierte en estructuras Python.
    libros = json.load(f)

# --- Insertar libros y autores ---
for libro in libros:
    # Insertar libro
    cursor.execute("""
        INSERT INTO libros (titulo, precio, disponibilidad, estrellas, descripcion, imagen_url, categoria)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        libro.get("title"),
        libro.get("price"),
        libro.get("availability"),
        libro.get("stars"),
        libro.get("description"),
        libro.get("image_url"),
        libro.get("category")
    ))
    libro_id = cursor.lastrowid #lastrowid da el id autogenerado del libro recién insertado, recupera el id 

    # Procesar autores (pueden venir separados por comas)
    autores = libro.get("author", "").split(",")
    for autor in autores:
        autor = autor.strip()
        if not autor:
            continue

        # Insertar autor si no existe
        cursor.execute("INSERT OR IGNORE INTO autores (nombre) VALUES (?)", (autor,))
        conexion.commit() #verifica si existe o no el eauto y si no mete y guarad la info

        # Obtener id del autor
        cursor.execute("SELECT id FROM autores WHERE nombre = ?", (autor,))
        autor_id = cursor.fetchone()[0] #fetchono trae una fila de resultados pero con [0] lo qu ehace es traer el primer elemento qu ees el id
        #trae solo el nombre y no la tupla con la , 

        # Insertar relación libro-autor
        cursor.execute("""
            INSERT INTO libro_autor (libro_id, autor_id) VALUES (?, ?)
        """, (libro_id, autor_id))

conexion.commit()


conexion.close()
print(f"✅ Datos cargados en '{DB_FILE}' con tablas normalizadas y relación muchos-a-muchos.")
