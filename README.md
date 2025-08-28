Este proyecto implementa un sistema de gestión de una librería utilizando SQLite y datos provenientes de un archivo JSON. 
El esquema de la base de datos está normalizado e incluye tres tablas principales: libros, autores y libro_autor. 
La relación entre libros y autores es de muchos a muchos, resuelta mediante la tabla intermedia libro_autor. 
El script automatiza la creación de las tablas, la carga de información desde el JSON y la inserción de relaciones entre entidades, 
garantizando consistencia de datos y evitando duplicados de autores.
