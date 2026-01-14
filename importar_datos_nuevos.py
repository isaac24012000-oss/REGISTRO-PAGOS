#!/usr/bin/env python3
"""
Importar datos desde el archivo CSV de descargas
"""

import csv
from database import registrar_pago, DB_PATH, init_db
import sqlite3
import os

def importar_csv_nuevos(archivo_csv):
    """Importa datos del CSV a la base de datos"""
    
    init_db()  # Asegurar que la BD existe
    
    if not os.path.exists(archivo_csv):
        print(f"❌ Archivo no encontrado: {archivo_csv}")
        return 0
    
    print(f"📁 Leyendo archivo: {archivo_csv}\n")
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Mostrar columnas disponibles
            print(f"Columnas disponibles: {reader.fieldnames}\n")
            
            contador = 0
            errores = 0
            
            for fila in reader:
                try:
                    # Extraer datos del CSV
                    ruc = fila.get('ruc', '').strip()
                    id_documento = fila.get('id_documento', ruc).strip()
                    fecha_reporte = fila.get('fecha_reporte', '2026-01-14').strip()
                    campana = fila.get('campaña', 'ENERO 2026').strip()
                    asesor = fila.get('asesor', '').strip()
                    
                    promesa_ga = fila.get('promesa_ga', '').strip()
                    monto_gasto = fila.get('monto_gasto', '').strip()
                    fecha_pago_gasto = fila.get('fecha_pago_gasto', '').strip()
                    
                    promesa_planilla = fila.get('promesa_planilla', '').strip()
                    monto_planilla = fila.get('monto_planilla', '').strip()
                    fecha_pago_planilla = fila.get('fecha_pago_planilla', '').strip()
                    
                    observaciones = fila.get('observaciones', '').strip()
                    
                    # Convertir montos a float
                    try:
                        monto_gasto = float(monto_gasto) if monto_gasto else None
                    except:
                        monto_gasto = None
                    
                    try:
                        monto_planilla = float(monto_planilla) if monto_planilla else None
                    except:
                        monto_planilla = None
                    
                    if not ruc:
                        print(f"⚠️ Fila incompleta (sin RUC)")
                        errores += 1
                        continue
                    
                    # Intentar registrar el pago
                    try:
                        registro_id = registrar_pago(
                            fecha_reporte=fecha_reporte,
                            ruc=ruc,
                            id_documento=id_documento,
                            campaña=campana,
                            asesor=asesor if asesor else None,
                            promesa_ga=promesa_ga if promesa_ga else None,
                            monto_gasto=monto_gasto,
                            fecha_pago_gasto=fecha_pago_gasto if fecha_pago_gasto else None,
                            promesa_planilla=promesa_planilla if promesa_planilla else None,
                            monto_planilla=monto_planilla,
                            fecha_pago_planilla=fecha_pago_planilla if fecha_pago_planilla else None,
                            observaciones=observaciones if observaciones else ""
                        )
                        if registro_id:
                            contador += 1
                            print(f"✅ RUC {ruc} - Fecha: {fecha_reporte}")
                        else:
                            print(f"⚠️ RUC {ruc} (no se pudo registrar)")
                            errores += 1
                    except Exception as e:
                        print(f"⚠️ Error al registrar {ruc}: {str(e)}")
                        errores += 1
                    
                except Exception as e:
                    print(f"⚠️ Error procesando fila: {str(e)}")
                    errores += 1
            
            print(f"\n{'='*60}")
            print(f"✅ Se importaron {contador} registros correctamente")
            print(f"⚠️  {errores} registros con errores")
            print(f"{'='*60}")
            return contador
    
    except Exception as e:
        print(f"❌ Error al importar: {str(e)}")
        return 0

if __name__ == "__main__":
    archivo = r"C:\Users\USUARIO\Downloads\registros_pagos_20260114_124927.csv"
    print("=" * 60)
    print("Importar datos desde CSV a pagos.db")
    print("=" * 60)
    print()
    importar_csv_nuevos(archivo)
