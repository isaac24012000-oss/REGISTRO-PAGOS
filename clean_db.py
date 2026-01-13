#!/usr/bin/env python3
"""
Script para limpiar la BD y crear nueva estructura
"""

import sqlite3
import os
from datetime import datetime
import openpyxl

DB_PATH = "pagos.db"

def crear_nueva_bd():
    """Crea una nueva BD con la estructura correcta"""
    
    # Eliminar BD anterior
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"✓ Base de datos anterior eliminada")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de RUCs base (sin pagos)
    cursor.execute('''
    CREATE TABLE rucs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ruc TEXT UNIQUE NOT NULL,
        id_documento TEXT UNIQUE NOT NULL,
        razon_social TEXT NOT NULL,
        campaña TEXT NOT NULL,
        asesor TEXT,
        fecha_creacion TEXT NOT NULL
    )
    ''')
    
    # Tabla ÚNICA de registros de pagos diarios
    cursor.execute('''
    CREATE TABLE registros_pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_reporte TEXT NOT NULL,
        ruc TEXT NOT NULL,
        id_documento TEXT NOT NULL,
        campaña TEXT NOT NULL,
        asesor TEXT,
        promesa_ga TEXT,
        monto_gasto REAL,
        fecha_pago_gasto TEXT,
        promesa_planilla TEXT,
        monto_planilla REAL,
        fecha_pago_planilla TEXT,
        observaciones TEXT,
        fecha_registro TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Nueva base de datos creada: {DB_PATH}")

def importar_rucs_desde_excel(archivo_excel=r'DATA ENERO 2026.xlsx'):
    """Importa solo los RUCs únicos del Excel"""
    
    print(f"\nImportando RUCs desde: {archivo_excel}")
    
    try:
        wb = openpyxl.load_workbook(archivo_excel)
        ws = wb.active
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        rucs_procesados = set()
        count = 0
        
        # Procesar filas (saltando encabezado)
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 1):
            try:
                if row_idx > 1 and row_idx % 1000 == 0:
                    print(f"  Procesados {row_idx-1} registros...")
                
                campaña = row[0]
                documento = str(int(row[1])) if row[1] else None
                razon_social = row[2]
                deuda_total = float(row[3]) if row[3] else 0
                gastos_admin = float(row[4]) if row[4] else 0
                periodos = row[5]
                asesor = row[6]
                
                if not documento or not razon_social or not campaña:
                    continue
                
                # Usar documento como RUC
                ruc = documento
                
                # Evitar duplicados
                if (ruc, campaña) in rucs_procesados:
                    continue
                
                rucs_procesados.add((ruc, campaña))
                
                try:
                    cursor.execute('''
                    INSERT INTO rucs (ruc, id_documento, razon_social, campaña, asesor, fecha_creacion)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (ruc, documento, razon_social, campaña, asesor, datetime.now().isoformat()))
                    count += 1
                except sqlite3.IntegrityError:
                    pass
                
            except Exception as e:
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✓ {count} RUCs únicos importados correctamente")
        return count
        
    except Exception as e:
        print(f"✗ Error al importar: {e}")
        return 0

if __name__ == "__main__":
    print("=" * 70)
    print("HERRAMIENTA DE LIMPIEZA Y REINICIO DE BASE DE DATOS")
    print("=" * 70)
    
    crear_nueva_bd()
    count = importar_rucs_desde_excel()
    
    print("\n" + "=" * 70)
    print(f"✓ PROCESO COMPLETADO - {count} RUCs en la base de datos")
    print("=" * 70)
    print("\nAhora puedes usar la app para registrar pagos diarios.")
