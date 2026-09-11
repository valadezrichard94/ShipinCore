import os
import sys
import mysql.connector
from seguridad import login, registrar
from lotes import registrar_lote, consultar_lotes_general, consultar_lotes_por_modelo
from Embarque import captura_datos, descontar_stock
from db import conectar_base_datos


def mostrar_logo():
    """Imprime el logo oficial de ShipinCore en arte ASCII."""
    print("═" * 78)
    print("""
  ██████  ██   ██ ██ ██████  ██ ███    ██  ██████  ██████  ██████  ███████ 
 ██       ██   ██ ██ ██   ██ ██ ████   ██ ██      ██    ██ ██   ██ ██      
 ██████   ███████ ██ ██████  ██ ██ ██  ██ ██      ██    ██ ██████  █████   
      ██  ██   ██ ██ ██      ██ ██  ██ ██ ██      ██    ██ ██   ██ ██      
  ██████  ██   ██ ██ ██      ██ ██   ████  ██████  ██████  ██   ██ ███████ 
    """)
    print("  [ SISTEMA CENTRAL DE EMBARQUES ]  v1.2 - TERMINAL APP" )
    print("═" * 78)


def limpiar_pantalla():
    """Mantiene la terminal limpia y ordenada durante la navegación."""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu_principal():
    """Menú que ven los supervisores una vez que ya se loguearon."""
    limpiar_pantalla()
    print("====================================================")
    print("         SISTEMA DE AUTOMATIZACIÓN DE EMBARQUES      ")
    print("====================================================")
    print(" [1] ENTRAR AL MÓDULO DE CONTROL DE INVENTARIO")
    print(" [2] [MÓDULO 2 - ESPACIO LIBRE PARA PROGRAMAR]")
    print(" [3] [MÓDULO 3 - ESPACIO LIBRE PARA PROGRAMAR]")
    print(" [0] SALIR DEL SISTEMA")
    print("====================================================")

def submenu_inventario(user, conexion):
    """Módulo 1: Operaciones directas en el Patio de Contenedores"""
    while True:
        limpiar_pantalla()
        mostrar_logo()
        print("====================================================")
        print("            MÓDULO: CONTROL DE INVENTARIO           ")
        print("====================================================")
        print(" [1] Espacio listo para programar...")
        print(" [2] Salida Embarque")
        print(" [3] Buscar por modelo")
        print(" [4] Consultar historial")
        print(" [5] Registrar nuevo lote")
        print(" [0] Volver al Menú Principal")
        print("====================================================")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            print("\n[Ejecutando: Ver Catálogo de Clientes...]")
            input("\nPresiona Enter para continuar...")
        elif opcion == "2":
            print("\n[Ejecutando: Salida Embarque")
            cliente, lista_modelos = captura_datos(conexion, user)
            if lista_modelos:
                for item in lista_modelos:
                    id_producto = item["id_modelo"]
                    cantidad_a_restar = item["cantidad_modelo"]
                    descontar_stock(conexion, id_producto, cantidad_a_restar, user)
                print("Proceso de salida y descuento finalizado.")
            else:
                print("No se proceso ningun descuento (captura vacia o cancelada)")
            input("Presiona enter para continuar...")
        elif opcion == "3":
            print("\n[Buscando por modelo...]")
            consultar_lotes_por_modelo(conexion) 
        elif opcion == "4":
            print("\n[Ejecutando: Consultar historial...]")
            consultar_lotes_general(conexion)
        elif opcion == "5":
            registrar_lote(user)
        elif opcion == "0":
            break
        else:
            input("\nOpción no válida. Presiona Enter...")


# ====================================================================
# ORQUESTADOR PRINCIPAL
# ====================================================================
def sistema_inicio(conexion):
    """Pantalla de bienvenida inicial para control de acceso y registros."""
    while True:
        limpiar_pantalla()
        mostrar_logo()
        print("====================================================")
        print("             ¡BIENVENIDO A SHIPINCORE!    ")
        print("====================================================")
        print(" [1] Iniciar Sesión.")
        print(" [2] Registrar Nuevo Usuario.")
        print(" [0] Salir.")
        print("====================================================")
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
        
            usuario_activo = login(conexion)
            
        
            if usuario_activo:
            
                submenu_inventario(usuario_activo, conexion)
            else:
                print("-" * 50)
                input("Presione Enter para volver al menú de inicio...")
                
        elif opcion == "2":
        
            registrar() 
            input("\nUsuario registrado con éxito. Presione Enter para continuar...")
            
        elif opcion == "0":
            print("\nCerrando sistema... ¡Excelente turno!")
            sys.exit()
            
        else:
            input("\n Opción no válida. Presiona Enter...")

    # ====================================================================
    # ZONA INVIOLABLE: Solo se activa si el login de arriba fue exitoso
    # ====================================================================
    while True:
        mostrar_menu_principal()
        opcion = input("Selecciona una opción para trabajar: ")
        
        if opcion == "1":
            submenu_inventario(user)
        elif opcion == "2":
            limpiar_pantalla()
            print("\n====================================================")
            print(" [Módulo seleccionado - Espacio listo para programar]")
            print("====================================================")
            input("\nPresiona Enter para volver...")
        elif opcion == "0":
            limpiar_pantalla()
            print("\n====================================================")
            print("  Saliendo del sistema de Embarques... ¡Buen turno!")
            print("====================================================\n")
            sys.exit()
        else:
            input("\nOpción no válida. Presiona Enter...")
                

if __name__ == "__main__":
    conexion = conectar_base_datos()
    if conexion:
        sistema_inicio(conexion)
    else:
        print("Error crítico: No se pudo conectar a la base de datos.")