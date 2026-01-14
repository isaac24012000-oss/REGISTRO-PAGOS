#!/usr/bin/env python3
"""
Script para detectar y eliminar duplicados exactos en la BD
"""

import sqlite3
from database import DB_PATH

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔍 BUSCANDO DUPLICADOS EXACTOS")
    print("=" * 80)
    
    # Buscar duplicados exactos (todos los campos iguales excepto ID)
    query = """
    SELECT 
        fecha_reporte, ruc, id_documento, campaña, asesor,
        promesa_ga, monto_gasto, fecha_pago_gasto,
        promesa_planilla, monto_planilla, fecha_pago_planilla,
        observaciones,
        COUNT(*) as cantidad,
        GROUP_CONCAT(id) as ids
    FROM registros_pagos
    GROUP BY 
        fecha_reporte, ruc, id_documento, campaña, asesor,
        promesa_ga, monto_gasto, fecha_pago_gasto,
        promesa_planilla, monto_planilla, fecha_pago_planilla,
        observaciones
    HAVING COUNT(*) > 1
    """
    
    cursor.execute(query)
    duplicados = cursor.fetchall()
    
    if duplicados:
        print(f"\n✓ Se encontraron {len(duplicados)} grupos de registros duplicados\n")
        
        for idx, dup in enumerate(duplicados, 1):
            ids = dup[-1].split(',')
            print(f"Duplicado #{idx}:")
            print(f"  RUC: {dup[1]}")
            print(f"  Fecha: {dup[0]}")
            print(f"  Asesor: {dup[4]}")
            print(f"  Cantidad: {dup[-2]} registros")
            print(f"  IDs: {ids}")
            print(f"  → Conservando ID: {ids[0]}, eliminando: {ids[1:]}\n")
            
            # Eliminar todos excepto el primero
            for id_a_eliminar in ids[1:]:
                cursor.execute("DELETE FROM registros_pagos WHERE id = ?", (int(id_a_eliminar),))
                print(f"    ✓ Eliminado ID {id_a_eliminar}")
        
        conn.commit()
        print(f"\n✓ Se eliminaron {sum(len(dup[-1].split(','))-1 for dup in duplicados)} registros duplicados")
    else:
        print("\n✓ No se encontraron duplicados exactos en la BD")
    
    # Mostrar total final
    cursor.execute("SELECT COUNT(*) FROM registros_pagos")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total de registros después de la limpieza: {total}")
    print("=" * 80)
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
