#!/usr/bin/env python3
"""
Script para verificar si el RUC fue eliminado
"""

import sqlite3
from database import DB_PATH

def verificar_ruc(ruc):
    """Verifica si un RUC existe en la BD"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM rucs WHERE ruc = ?", (ruc,))
        count_rucs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM registros_pagos WHERE ruc = ?", (ruc,))
        count_pagos = cursor.fetchone()[0]
        
        print(f"RUC: {ruc}")
        print(f"  En tabla 'rucs': {count_rucs} registros")
        print(f"  En tabla 'registros_pagos': {count_pagos} registros")
        
        if count_rucs == 0 and count_pagos == 0:
            print(f"\n✓ El RUC fue eliminado correctamente de la BD")
        else:
            print(f"\n⚠ El RUC aún existe en la BD")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    verificar_ruc("20179523745")
