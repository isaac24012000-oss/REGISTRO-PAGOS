#!/usr/bin/env python3
"""
Mantener solo los registros del CSV importado
"""

import sqlite3

conn = sqlite3.connect("pagos.db")
cursor = conn.cursor()

print("=" * 70)
print("Eliminando registros que NO están en el CSV")
print("=" * 70)

# Los registros del CSV son todos del 2026-01-13
# Vamos a eliminar los registros de otras fechas
cursor.execute('''
SELECT id, fecha_reporte, ruc, COUNT(*) as cantidad
FROM registros_pagos
WHERE fecha_reporte != '2026-01-13'
GROUP BY fecha_reporte
''')

registros_otros = cursor.fetchall()

print("\nRegistros a eliminar (no están en el CSV):")

total_a_eliminar = 0
for id_reg, fecha, ruc, cantidad in registros_otros:
    print(f"  Fecha: {fecha} - {cantidad} registro(s)")
    
    # Obtener todos los IDs de esta fecha
    cursor.execute('''
    SELECT id FROM registros_pagos
    WHERE fecha_reporte = ?
    ''', (fecha,))
    
    ids = [row[0] for row in cursor.fetchall()]
    print(f"    IDs: {ids}")
    
    # Eliminar
    for id_del in ids:
        cursor.execute('DELETE FROM registros_pagos WHERE id = ?', (id_del,))
        total_a_eliminar += 1

conn.commit()

# Contar nuevamente
cursor.execute("SELECT COUNT(*) FROM registros_pagos")
total_nuevo = cursor.fetchone()[0]

cursor.execute("SELECT fecha_reporte, COUNT(*) FROM registros_pagos GROUP BY fecha_reporte")
por_fecha = cursor.fetchall()

print(f"\n{'=' * 70}")
print(f"✅ Registros eliminados: {total_a_eliminar}")
print(f"✅ Registros restantes: {total_nuevo}")
print(f"\nRegistros por fecha:")
for fecha, cantidad in por_fecha:
    print(f"  {fecha}: {cantidad} registros")
print(f"{'=' * 70}")

conn.close()
