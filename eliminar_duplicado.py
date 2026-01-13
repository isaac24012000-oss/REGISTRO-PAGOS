#!/usr/bin/env python3
"""
Script para eliminar un registro duplicado de la base de datos
"""

import sqlite3
from database import DB_PATH

def eliminar_ruc_duplicado(ruc):
    """Elimina un RUC y todos sus registros de pago asociados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si existe en tabla rucs
        cursor.execute("SELECT id, razon_social FROM rucs WHERE ruc = ?", (ruc,))
        ruc_record = cursor.fetchone()
        
        if ruc_record:
            print(f"✓ Encontrado en tabla 'rucs':")
            print(f"  RUC: {ruc}")
            print(f"  Razón Social: {ruc_record[1]}")
            
            # Contar registros de pago
            cursor.execute("SELECT COUNT(*) FROM registros_pagos WHERE ruc = ?", (ruc,))
            count_pagos = cursor.fetchone()[0]
            print(f"  Registros de pago asociados: {count_pagos}")
            
            # Eliminar
            cursor.execute("DELETE FROM registros_pagos WHERE ruc = ?", (ruc,))
            cursor.execute("DELETE FROM rucs WHERE ruc = ?", (ruc,))
            conn.commit()
            
            print(f"\n✓ Registro eliminado correctamente")
            print(f"  - {count_pagos} registros de pago eliminados")
            print(f"  - 1 registro de RUC eliminado")
        else:
            print(f"⚠ No se encontró el RUC: {ruc}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error al eliminar: {e}")

if __name__ == "__main__":
    ruc_a_eliminar = "20179523745"
    eliminar_ruc_duplicado(ruc_a_eliminar)
