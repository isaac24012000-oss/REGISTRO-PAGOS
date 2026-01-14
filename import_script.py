#!/usr/bin/env python3
import pandas as pd
import sys
from database import registrar_pago
from datetime import datetime

csv_file = r"C:\Users\USUARIO\Downloads\registros_pagos_20260114_124927.csv"

try:
    df = pd.read_csv(csv_file)
    print(f"✓ CSV cargado: {len(df)} registros")
    print(f"\nColumnas: {df.columns.tolist()}")
    print(f"\nPrimeras filas:")
    print(df.head(2).to_string())
    
    # Intentar mapear columnas e importar
    print("\n" + "="*60)
    print("IMPORTANDO REGISTROS...")
    print("="*60)
    
    registros_importados = 0
    errores = 0
    
    for idx, row in df.iterrows():
        try:
            registrar_pago(
                fecha_reporte=row.get('fecha_reporte', datetime.today().date()),
                ruc=str(row.get('ruc', '')),
                id_documento=str(row.get('id_documento', '')),
                campaña=str(row.get('campaña', '')),
                asesor=str(row.get('asesor', '')),
                promesa_ga=str(row.get('promesa_ga', 'COBRADO')),
                monto_gasto=float(row.get('monto_gasto', 0)) if pd.notna(row.get('monto_gasto')) else None,
                fecha_pago_gasto=str(row.get('fecha_pago_gasto', '')) if pd.notna(row.get('fecha_pago_gasto')) else None,
                promesa_planilla=str(row.get('promesa_planilla', 'COBRADO')),
                monto_planilla=float(row.get('monto_planilla', 0)) if pd.notna(row.get('monto_planilla')) else None,
                fecha_pago_planilla=str(row.get('fecha_pago_planilla', '')) if pd.notna(row.get('fecha_pago_planilla')) else None,
                observaciones=str(row.get('observaciones', ''))
            )
            registros_importados += 1
            print(f"✓ Registro {idx+1}/{len(df)}: RUC {row.get('ruc')}")
        except Exception as e:
            errores += 1
            print(f"✗ Registro {idx+1}: Error - {str(e)}")
    
    print("\n" + "="*60)
    print(f"RESULTADO: {registros_importados} registros importados, {errores} errores")
    print("="*60)

except FileNotFoundError:
    print(f"✗ Archivo no encontrado: {csv_file}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
