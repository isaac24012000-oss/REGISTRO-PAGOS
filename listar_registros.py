#!/usr/bin/env python3
"""
Script para listar todos los registros de pagos
"""

import sqlite3
from database import DB_PATH
import pandas as pd

try:
    conn = sqlite3.connect(DB_PATH)
    
    # Obtener todos los registros
    query = """
    SELECT 
        id, fecha_reporte, ruc, id_documento, campaña, asesor,
        promesa_ga, monto_gasto, promesa_planilla, monto_planilla
    FROM registros_pagos
    ORDER BY fecha_reporte DESC, id DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    print("=" * 100)
    print("📋 REGISTROS DE PAGOS EN LA BD")
    print("=" * 100)
    print(df.to_string(index=False))
    print("=" * 100)
    print(f"\n✓ Total de registros: {len(df)}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
