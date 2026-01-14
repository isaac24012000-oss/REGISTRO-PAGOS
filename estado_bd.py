#!/usr/bin/env python3
"""
Script para verificar el estado de la BD
"""

import sqlite3
from database import DB_PATH

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Contar registros en ambas tablas
    cursor.execute("SELECT COUNT(*) FROM rucs")
    count_rucs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM registros_pagos")
    count_pagos = cursor.fetchone()[0]
    
    print("=" * 50)
    print("📊 ESTADO DE LA BASE DE DATOS")
    print("=" * 50)
    print(f"✓ Registros en tabla 'rucs': {count_rucs}")
    print(f"✓ Registros en tabla 'registros_pagos': {count_pagos}")
    print("=" * 50)
    
    if count_rucs > 0:
        print("\n✓ La BD tiene datos")
    else:
        print("\n⚠️ La BD está vacía")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
