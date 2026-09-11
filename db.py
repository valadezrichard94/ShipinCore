import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def conectar_base_datos(incluir_db=True):
    """Centraliza la conexión a MySQL usando variables de entorno.

    :param incluir_db: True para conectar directo a DB_NAME, False para
    conexión global.
    :return: Objeto conexión o None si ocurre un fallo.
    """
    try:
        config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD"),
        }

        if incluir_db:
            config["database"] = os.getenv("DB_NAME", "container")

        conexion = mysql.connector.connect(**config)
        return conexion

    except mysql.connector.Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None