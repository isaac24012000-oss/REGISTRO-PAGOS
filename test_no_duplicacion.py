#!/usr/bin/env python3
"""
Script de prueba para verificar que no hay duplicación de pagos
"""

import sqlite3
from database import init_db, registrar_pago_planilla, registrar_gasto_administrativo

def verificar_no_duplicacion():
    """Verifica que al registrar un pago, solo se registre en una tabla"""
    
    # Contar registros antes
    conn = sqlite3.connect("pagos.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM pagos_planilla")
    count_planilla_antes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gastos_administrativos")
    count_gastos_antes = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Registros ANTES del test:")
    print(f"  - Pagos de Planilla: {count_planilla_antes}")
    print(f"  - Gastos Administrativos: {count_gastos_antes}")
    print()
    
    # Registrar un pago de planilla
    print("Registrando un pago de PLANILLA...")
    registrar_pago_planilla(
        ruc_id="9999999",
        ruc="9999999",
        campana="PRUEBA",
        monto=1000.00,
        estado="COBRADO",
        observaciones="Pago de prueba"
    )
    
    # Contar registros después
    conn = sqlite3.connect("pagos.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM pagos_planilla")
    count_planilla_despues = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gastos_administrativos")
    count_gastos_despues = cursor.fetchone()[0]
    
    conn.close()
    
    print()
    print(f"Registros DESPUES del pago de PLANILLA:")
    print(f"  - Pagos de Planilla: {count_planilla_despues} (aumentó {count_planilla_despues - count_planilla_antes})")
    print(f"  - Gastos Administrativos: {count_gastos_despues} (aumentó {count_gastos_despues - count_gastos_antes})")
    print()
    
    # Verificar
    if (count_planilla_despues - count_planilla_antes) == 1 and (count_gastos_despues - count_gastos_antes) == 0:
        print("✅ CORRECTO: El pago se registró SOLO en pagos_planilla")
    else:
        print("❌ ERROR: El pago se registró en más de una tabla (duplicación)")
    
    # Registrar un gasto administrativo
    print()
    print("Registrando un gasto ADMINISTRATIVO...")
    registrar_gasto_administrativo(
        ruc_id="8888888",
        ruc="8888888",
        campana="PRUEBA",
        monto=500.00,
        estado="COBRADO",
        observaciones="Gasto de prueba"
    )
    
    # Contar registros después
    conn = sqlite3.connect("pagos.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM pagos_planilla WHERE ruc_id = '8888888'")
    count_planilla_nuevo = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gastos_administrativos WHERE ruc_id = '8888888'")
    count_gastos_nuevo = cursor.fetchone()[0]
    
    conn.close()
    
    print()
    print(f"Registros del gasto ADMINISTRATIVO:")
    print(f"  - En pagos_planilla: {count_planilla_nuevo}")
    print(f"  - En gastos_administrativos: {count_gastos_nuevo}")
    print()
    
    if count_planilla_nuevo == 0 and count_gastos_nuevo == 1:
        print("✅ CORRECTO: El gasto se registró SOLO en gastos_administrativos")
    else:
        print("❌ ERROR: El gasto se registró en más de una tabla (duplicación)")

if __name__ == "__main__":
    verificar_no_duplicacion()
