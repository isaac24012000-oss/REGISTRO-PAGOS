#!/usr/bin/env python3
"""
Script para importar datos del Excel a la base de datos
"""

import openpyxl
from database import init_db
from datetime import datetime
import os
import sqlite3

def importar_excel_a_bd(archivo_excel=None):
    """Importa RUCs base desde Excel a la base de datos"""
    
    # Si no se especifica ruta, usar ruta relativa
    if archivo_excel is None:
        archivo_excel = os.path.join(os.path.dirname(__file__), 'DATA ENERO 2026.xlsx')
    
    print("=" * 70)
    print("IMPORTADOR DE RUCs - SISTEMA DE REGISTRO DE PAGOS")
    print("=" * 70)
    print()
    
    # Inicializar BD
    init_db()
    
    try:
        print(f"Leyendo archivo: {archivo_excel}\n")
        
        if not os.path.exists(archivo_excel):
            print(f"❌ Archivo no encontrado: {archivo_excel}")
            return False
        
        wb = openpyxl.load_workbook(archivo_excel)
        ws = wb.active
        
        conn = sqlite3.connect("pagos.db")
        cursor = conn.cursor()
        
        rucs_count = 0
        duplicados = 0
        
        # Procesar filas (saltando encabezado)
        total_filas = ws.max_row - 1
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 1):
            try:
                campaña = row[0]
                documento = str(int(row[1])) if row[1] else None
                razon_social = row[2]
                asesor = row[6] if len(row) > 6 else None
                
                if not documento or not razon_social or not campaña:
                    continue
                
                # Intentar insertar RUC
                try:
                    cursor.execute('''
                    INSERT INTO rucs (ruc, id_documento, razon_social, campaña, asesor, fecha_creacion)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (documento, documento, razon_social, campaña, asesor, datetime.now().isoformat()))
                    rucs_count += 1
                except sqlite3.IntegrityError:
                    # RUC duplicado, ignorar
                    duplicados += 1
                
                if row_idx % 500 == 0:
                    print(f"  Procesadas {row_idx}/{total_filas} filas...")
            
            except Exception as e:
                print(f"  Error en fila {row_idx}: {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        
        print()
        print("=" * 70)
        print("✅ IMPORTACION COMPLETADA")
        print("=" * 70)
        print(f"RUCs importados: {rucs_count}")
        print(f"RUCs duplicados (ignorados): {duplicados}")
        print()
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    importar_excel_a_bd()
