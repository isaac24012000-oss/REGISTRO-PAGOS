#!/usr/bin/env python3
"""
Restaurar la base de datos con solo los 18 registros del CSV
"""

import sqlite3
import csv

# Primero, limpiar la base de datos
conn = sqlite3.connect("pagos.db")
cursor = conn.cursor()

print("=" * 70)
print("Limpiando la base de datos...")
print("=" * 70)

cursor.execute('DELETE FROM registros_pagos')
conn.commit()

print("✅ Base de datos limpiada\n")

# Leer el CSV
archivo = r"C:\Users\USUARIO\Downloads\registros_pagos_20260114_124927.csv"
with open(archivo, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    registros = list(reader)

print(f"Importando {len(registros)} registros del CSV...")
print("=" * 70)

contador = 0
for reg in registros:
    try:
        cursor.execute('''
        INSERT INTO registros_pagos 
        (fecha_reporte, ruc, id_documento, campaña, asesor, 
         promesa_ga, monto_gasto, fecha_pago_gasto,
         promesa_planilla, monto_planilla, fecha_pago_planilla,
         observaciones, fecha_registro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reg.get('fecha_reporte', ''),
            reg.get('ruc', ''),
            reg.get('id_documento', ''),
            reg.get('campaña', ''),
            reg.get('asesor', '') or None,
            reg.get('promesa_ga', '') or None,
            float(reg.get('monto_gasto', 0)) if reg.get('monto_gasto') else None,
            reg.get('fecha_pago_gasto', '') or None,
            reg.get('promesa_planilla', '') or None,
            float(reg.get('monto_planilla', 0)) if reg.get('monto_planilla') else None,
            reg.get('fecha_pago_planilla', '') or None,
            reg.get('observaciones', ''),
            reg.get('fecha_registro', '')
        ))
        contador += 1
        fecha = reg.get('fecha_reporte', 'SIN FECHA')
        ruc = reg.get('ruc', 'SIN RUC')
        print(f"✅ {ruc} - {fecha}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

conn.commit()

# Verificar
cursor.execute("SELECT COUNT(*) FROM registros_pagos")
total = cursor.fetchone()[0]

cursor.execute("SELECT fecha_reporte, COUNT(*) FROM registros_pagos GROUP BY fecha_reporte ORDER BY fecha_reporte")
por_fecha = cursor.fetchall()

print(f"\n{'=' * 70}")
print(f"✅ Registros importados: {contador}")
print(f"✅ Total en base de datos: {total}")
print(f"\nRegistros por fecha:")
for fecha, cantidad in por_fecha:
    print(f"  {fecha}: {cantidad} registros")
print(f"{'=' * 70}")

conn.close()
