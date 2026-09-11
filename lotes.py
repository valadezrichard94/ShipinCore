import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def conectar_base_datos():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conexion
    except mysql.connector.Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def registrar_lote(user):
    
    limpiar_pantalla()
    conexion = conectar_base_datos()
    
    if conexion is None:
        print("Error: No se pudo conectar con el servidor MySQL de la planta.")
        input("\nPresiona Enter para regresar al menú...")
        return

    cursor = conexion.cursor()
    
    print("====================================================")
    print("        MÓDULO: REGISTRO DE EMBARQUE (CHECKLIST)    ")
    print("====================================================")
    print(f"👤 OPERADOR ACTIVO: {user}")
    print("====================================================")
    
    # 1. CAPTURA DE DATOS GENERALES DEL VIAJE
    while True:
        codigo_lote = input("Código o Número de Lote/Viaje (ej. L-33): ").strip().upper()
        if not codigo_lote:
            print("El código de lote no puede estar vacío.")
            continue
        break

    while True:
        try:
            id_cliente = int(input("ID del Cliente que envía el material: "))
            break
        except ValueError:
            print("El cliente no existe")

    # 2. BUSCAR LOS MODELOS ASOCIADOS A ESTE CLIENTE
    try:
        query_modelos = """
            SELECT id_modelo, nombre_modelo 
            FROM modelos_contenedores 
            WHERE id_cliente = %s
        """
        cursor.execute(query_modelos, (id_cliente,))
        lista_modelos = cursor.fetchall()
        
        if not lista_modelos:
            print(f"\nNo se encontraron modelos registrados para el Cliente ID {id_cliente}.")
            cursor.close()
            conexion.close()
            input("\nPresiona Enter para regresar...")
            return

        print(f"\n¡Se encontraron {len(lista_modelos)} modelos para este cliente!")
        input("Presiona Enter para iniciar la captura...")
        
    except Exception as e:
        print(f"Error al consultar los modelos del cliente: {e}")
        cursor.close()
        conexion.close()
        input("\nPresiona Enter para regresar...")
        return

    # 3. CICLO EN CADENA PARA REGISTRAR CADA MODELO
    registros_exitosos = 0
    
    for modelo in lista_modelos:
        id_modelo = modelo[0]
        nombre_modelo = modelo[1]
        
        
        print("=========================================================================")
        print(f" LOTE: {codigo_lote}  |  CLIENTE ID: {id_cliente}  |  REGISTRA: {user}")
        print("==========================================================================")
        print(f"REGISTRAR: {nombre_modelo} (ID: {id_modelo})")
        print("---------------------------------------------------------------------------")
        
        # Cantidad de piezas
        while True:
            entrada_piezas = input("Cantidad de piezas/contenedores físicos (Enter para 0): ").strip()
            if entrada_piezas == "":
                cantidad_piezas = 0
                break
            try:
                cantidad_piezas = int(entrada_piezas)
                if cantidad_piezas >= 0:
                    break
                print("La cantidad de piezas no puede ser negativa.")
            except ValueError:
                print("Ingresa un número entero válido o presiona Enter.")
        
        # Guardar datos del lote
        try:
            sql_insert = """
                INSERT INTO lote_contenedores 
                (codigo_lote, id_cliente, id_modelo, cantidad_piezas, usuario) 
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (codigo_lote, id_cliente, id_modelo, cantidad_piezas, user)
            cursor.execute(sql_insert, valores)
            conexion.commit()
            registros_exitosos 
        except Exception as e:
            print(f"Error al guardar el desglose de este modelo: {e}")
            conexion.rollback()
            
            
    print("\n====================================================")
    print(f"¡Proceso terminado! Datos guardados en el lote '{codigo_lote}' por {user}.")
    print("====================================================")
    input("\nPresione ENTER para regresar al menu principal")
    
def consultar_lotes_general(conexion):
    """Consulta y muestra el historial completo de lotes ingresados."""
    try:
        
        if not conexion or not conexion.is_connected():
            print("\nError: La conexión a MySQL se ha perdido. Reinicie el sistema.")
            input("\nPresione ENTER para continuar...")
            return

        cursor = conexion.cursor()
        query = """
            SELECT 
                l.codigo_lote, 
                m.nombre_modelo, 
                l.cantidad_piezas, 
                l.fecha_registro, 
                l.usuario 
            FROM lote_contenedores l
            INNER JOIN modelos_contenedores m ON l.id_modelo = m.id_modelo
            WHERE l.cantidad_piezas > 0
            ORDER BY l.fecha_registro DESC;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close() 
        
        print("\n" + "="*85)
        print("REPORTES GENERAL DE EMBARQUES INGRESADOS".center(85))
        print("="*85)
        
        if not resultados:
            print("\nNo se encontraron lotes registrados en el sistema.\n")
        else:
            print(f"{'LOTE':<15} | {'MODELO':<20} | {'STOCK':<8} | {'FECHA INGRESO':<19} | {'OPERADOR':<12}")
            print("-" * 85)
            for fila in resultados:
                lote, modelo, stock, fecha, operador = fila
                fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{lote:<15} | {modelo:<20} | {stock:<8} | {fecha_str:<19} | {operador:<12}")
                
        print("="*85)
        input("Presiona ENTER para regresar al menu...")
        
        
    except Exception as e:
        print(f"\nError al consultar los datos: {e}")
        



def consultar_lotes_por_modelo(conexion):
    """Filtra y muestra el historial de embarques de un modelo específico."""
    try:
        if not conexion or not conexion.is_connected():
            print("\nError: La conexión a MySQL se ha perdido. Reinicie el sistema.")
            input("\nPresione ENTER para continuar...")
            return

        print("\n" + "="*50)
        modelo_buscado = input("Ingrese ID del modelo: ").strip()
        print("="*50)
        
        cursor = conexion.cursor()
        query = """
            SELECT 
                l.codigo_lote, 
                m.nombre_modelo, 
                l.cantidad_piezas, 
                l.fecha_registro, 
                l.usuario 
            FROM lote_contenedores l
            INNER JOIN modelos_contenedores m ON l.id_modelo = m.id_modelo
            WHERE l.id_modelo = %s
            AND l.cantidad_piezas > 0
            ORDER BY l.fecha_registro DESC;
        """
        cursor.execute(query, (modelo_buscado,))
        resultados = cursor.fetchall()
        
        total_piezas_modelo = 0
        
        print("\n" + "="*85)
        print(f"REPORTE ESPECÍFICO - MODELO: {modelo_buscado}".center(85))
        print("="*85)
        
        
        
        if not resultados:
            print(f"\nNo se encontraron movimientos ni stock para el modelo '{modelo_buscado}'.\n")
        else:
            print(f"{'LOTE':<15} | {'MODELO':<20} | {'STOCK':<8} | {'FECHA INGRESO':<19} | {'OPERADOR':<12}")
            print("-" * 85)
            for fila in resultados:
                lote, modelo, stock, fecha, operador = fila
                fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
                total_piezas_modelo += stock
                
                print(f"{lote:<15} | {modelo:<20} | {stock:<8} | {fecha_str:<19} | {operador:<12}")   
                
            
            
            print("=" * 75)
            print(f"STOCK TOTAL ACUMULADO DEL MODELO [{modelo_buscado}]: {total_piezas_modelo} piezas")
            print("=" * 75)
                    
                
        print("="*85)
        input("\nPresione ENTER para regresar al menú...")
        
    except Exception as e:
        print(f"\nError al filtrar los datos: {e}")
        