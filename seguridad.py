import os
from dotenv import load_dotenv
import mysql.connector  
import getpass          
import bcrypt

load_dotenv()           

import os
from dotenv import load_dotenv
import mysql.connector
import getpass
import bcrypt

load_dotenv()

def configurar_sistema():
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD")
    )

    cursor = conexion.cursor()  # Crea el cursor para enviar comandos SQL

    cursor.execute("CREATE DATABASE IF NOT EXISTS container")
    cursor.execute("USE container")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    return conexion, cursor  # Devuelve la conexión y el cursor para usarlos en otras funciones  # Devuelve la conexión y el cursor para usarlos en otras funciones

def registrar():
    db, cursor = configurar_sistema()  # Llama a la configuración para abrir la conexión
    print("\n--- REGISTRO DE USUARIO ---")
    
    while True: # Inicia ciclo para validar que el nombre no esté repetido
        nombre = input("Elige un nombre de usuario: ").strip().lower() # Limpia espacios y pasa a minúsculas
        # Busca en la tabla si ya existe un usuario con ese mismo nombre
        cursor.execute("SELECT * FROM usuarios WHERE nombre = %s", (nombre,))
        if cursor.fetchone(): # Si fetchone devuelve algo, es que el nombre ya existe
            print("Ese nombre ya está ocupado. Intenta con otro.")
        else: # Si no encuentra nada, el nombre está libre y sale del ciclo
            break
    
    print("\n---¡Por seguridad del sistema, no se veran caracteres al momento que escribas tu contraseña!---")
    
    # ============================================================
    
    while True:
        password_input = getpass.getpass("Crea tu contraseña: ").strip()
        
        if password_input != "":
            
            password = password_input.encode('utf-8')
            break
        else:
            print("La contraseña no puede estar vacía o contener solo espacios. Intenta de nuevo.")
    # ============================================================
    
    # Genera el hash (cifrado) de la contraseña usando una semilla aleatoria (salt)
    password_hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    
    # Prepara la sentencia SQL para insertar el nuevo usuario y su hash
    sql = "INSERT INTO usuarios (nombre, password) VALUES (%s, %s)"
    # Ejecuta la inserción pasando los valores de forma segura
    cursor.execute(sql, (nombre, password_hashed))
    
    db.commit() # Confirma los cambios en la base de datos (indispensable para INSERT)
    print(f"Usuario '{nombre}' registrado con éxito en MySQL.")
    db.close()  # Cierra la conexión para liberar recursos del sistema


def login(conexion):
    db, cursor = configurar_sistema() # Abre la conexión con la base de datos
    print("\n--- INICIO DE SESIÓN ---")
    
    user = input("Usuario: ").lower().strip() # Le agregamos .strip() por seguridad
    
    # ============================================================
    
    while True:
        password_raw = getpass.getpass("Contraseña: ").strip()
        
        if password_raw != "":
            # Si escribió algo real, lo pasamos a bytes para dárselo a bcrypt
            password_input = password_raw.encode('utf-8')
            break
        else:
            print("Por favor, ingresa tu contraseña. No puede estar vacía.")
    # ============================================================
    
    # Busca el hash de la contraseña asociado a ese nombre de usuario
    cursor.execute("SELECT password FROM usuarios WHERE nombre = %s", (user,))
    resultado = cursor.fetchone() # Captura la fila encontrada (o None si no existe)
    
    if resultado: # Si el usuario existe en la tabla.
        password_db = resultado[0] # Extrae el hash guardado en la primera columna seleccionada
        
        # Compara la contraseña escrita con el hash de la base de datos
        # checkpw se encarga de verificar si coinciden matemáticamente
        if bcrypt.checkpw(password_input, password_db.encode('utf-8') if isinstance(password_db, str) else password_db):
            print(f"¡Acceso concedido! Bienvenido, {user}.")
            db.close() # Cierra la conexión antes de salir
            return user # Retorna éxito para entrar al sistema
        else:
            print("Contraseña incorrecta.") # El usuario existe pero la clave no coincide
    else:
        print("El usuario no existe.") # No se encontró el nombre en la tabla
    
    db.close() # Cierra la conexión en caso de fallo
    return None # Retorna None si no se pudo iniciar sesión