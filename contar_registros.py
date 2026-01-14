#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("pagos.db")
cursor = conn.cursor()

# Contar registros totales
cursor.execute("SELECT COUNT(*) FROM registros_pagos")
total = cursor.fetchone()[0]

# Contar por fecha
cursor.execute("SELECT fecha_reporte, COUNT(*) FROM registros_pagos GROUP BY fecha_reporte ORDER BY fecha_reporte DESC")
por_fecha = cursor.fetchall()

print(f"Total de registros: {total}\n")
print("Desglose por fecha:")
for fecha, count in por_fecha:
    print(f"  {fecha}: {count} registros")

conn.close()
