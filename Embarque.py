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

# =====================================================================
# FUNCIÓN DE CAPTURA Y VALIDACIÓN
# =====================================================================
def captura_datos(conexion, user):
    limpiar_pantalla()
    
    if conexion is None or not conexion.is_connected():
        conexion = conectar_base_datos()
        if conexion is None:
            print("Error: No se pudo conectar con el servidor MySQL.")
            input("\nPresiona Enter para regresar al menú...")
            return None, []

    cursor = conexion.cursor()
    modelos_capturados = []
    
    print("=" * 80)
    print("                    INICIANDO CAPTURA DE DATOS                    ")
    print("=" * 80)
    
    # 1. Validación de Cliente
    cliente_valido = None
    while True:
        id_cliente= input("ID cliente: ").strip()
        try:
            cliente_valido = int(id_cliente)
        except ValueError:
            print("Debes ingresar un número entero válido para el cliente.\n")
            continue

        # Consulta con tupla correcta (cliente_valido,)
        cursor.execute("SELECT 1 FROM clientes WHERE id_cliente = %s", (cliente_valido,))
        if cursor.fetchone():
            print(f"El cliente {cliente_valido} fue validado con éxito.\n")
            break
        else:
            print(f"El cliente {cliente_valido} no existe en la base de datos. Intenta de nuevo.\n")

    # 2. Captura y Validación de Modelos y Cantidades
    while True:
        id_modelo_input = input("ID contenedor (o presiona 0 para terminar): ").strip()
        if id_modelo_input == "0":
            break
            
        try:
            id_modelo = int(id_modelo_input)
        except ValueError:
            print("Debes ingresar solo números enteros.\n")
            continue
        
        # Candado contra duplicados
        if any(item["id_modelo"] == id_modelo for item in modelos_capturados):
            print(f"¡CUIDADO! El modelo con ID {id_modelo} ya fue registrado en este embarque.\n")
            continue
        
        # Validar si el modelo existe en el catálogo
        query_modelo = "SELECT nombre_modelo FROM modelos_contenedores WHERE id_modelo = %s"
        cursor.execute(query_modelo, (id_modelo,))
        resultado_modelo = cursor.fetchone()
        
        if not resultado_modelo:
            print(f"ERROR: El modelo {id_modelo} no existe en el catálogo.\n")
            continue
            
        nombre_modelo = resultado_modelo[0]
        
        # Solicitar la cantidad a despachar de este modelo
        while True:
            try:
                cantidad_input = input(f"Cantidad a embarcar de '{nombre_modelo}': ").strip()
                cantidad = int(cantidad_input)
                if cantidad <= 0:
                    print("La cantidad debe ser mayor a 0.")
                    continue
                break
            except ValueError:
                print("Ingresa un número entero válido.")

        # Guardar estructura completa para el algoritmo de descuento
        modelos_capturados.append({
            "id_modelo": id_modelo,
            "nombre_modelo": nombre_modelo,
            "cantidad_modelo": cantidad
        })
        print(f"{cantidad} pzas de '{nombre_modelo}' agregadas a la cola.\n")
        
    cursor.close()

    # 3. Resumen en pantalla
    print("=" * 80)        
    print("                      RESUMEN DE LA CAPTURA                      ")
    print("=" * 80)
    print(f"Operador: {user} | Cliente asignado: {cliente_valido}")
    print("-" * 80)
    for m in modelos_capturados:
        print(f"• ID: {m['id_modelo']} | Modelo: {m['nombre_modelo']} | Cantidad: {m['cantidad_modelo']}")
    print("=" * 80)
    
    # Retorna tanto el cliente como la lista con cantidades para procesar_descuento_embarque
    return cliente_valido, modelos_capturados

def descontar_stock(conexion, id_producto, cantidad_a_restar, user):
    cursor = conexion.cursor(buffered=True)
    
    try:
        if not conexion.in_transaction:
            conexion.start_transaction()

        id_mod_int = int(id_producto)
        piezas_solicitadas = int(cantidad_a_restar)

        # 1. Buscamos todas las entradas de este modelo específico usando su id_detalle
        query_registros = """
            SELECT id_detalle, cantidad_piezas, codigo_lote 
            FROM lote_contenedores 
            WHERE id_modelo = %s AND cantidad_piezas > 0
            FOR UPDATE
        """
        cursor.execute(query_registros, (id_mod_int,))
        filas = cursor.fetchall()

        if not filas:
            print(f"Error: No hay piezas disponibles para el modelo {id_mod_int}.")
            return False

        # 2. Python calcula el stock total acumulado de ese modelo
        stock_total_memoria = sum(int(fila[1]) for fila in filas)

        print(f"\n--- Stock Global en Patio (Modelo {id_mod_int}) ---")
        print(f"Total disponible en sistema: {stock_total_memoria} pzas.")
        print(f"Cantidad a despachar:        {piezas_solicitadas} pzas.")

        if piezas_solicitadas > stock_total_memoria:
            print(f"Stock insuficiente. Hay {stock_total_memoria} pzas y solicitaste {piezas_solicitadas}.")
            return False

        # 3. Descontamos actualizando mediante id_detalle (clave primaria)
        piezas_pendientes = piezas_solicitadas
        query_update = """
            UPDATE lote_contenedores 
            SET cantidad_piezas = %s 
            WHERE id_detalle = %s
        """

        for fila in filas:
            if piezas_pendientes == 0:
                break

            id_detalle = int(fila[0])
            stock_fila = int(fila[1])
            codigo_lote = str(fila[2])

            if stock_fila >= piezas_pendientes:
                nuevo_stock = stock_fila - piezas_pendientes
                restadas = piezas_pendientes
                piezas_pendientes = 0
            else:
                nuevo_stock = 0
                restadas = stock_fila
                piezas_pendientes -= stock_fila

            # Ejecuta la actualización segura por id_detalle
            cursor.execute(query_update, (nuevo_stock, id_detalle))
            print(f"   ↳ Registro #{id_detalle} (Lote {codigo_lote}): -{restadas} pzas. Quedan: {nuevo_stock}")

        conexion.commit()
        nuevo_saldo_total = stock_total_memoria - piezas_solicitadas
        print(f"Descuento completado. Stock restante del modelo {id_mod_int}: {nuevo_saldo_total} pzas.\n")
        return True

    except Exception as e:
        conexion.rollback()
        print(f"Error al descontar inventario: {e}")
        return False

    finally:
        cursor.close()
            
            
                
        
    
    
            
                
                
        
    

        
    
    
    
    