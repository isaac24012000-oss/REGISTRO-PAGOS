#!/usr/bin/env python3
import csv

archivo = r"C:\Users\USUARIO\Downloads\registros_pagos_20260114_124927.csv"
with open(archivo, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    registros = list(reader)
    
print(f"Total de registros en CSV: {len(registros)}")
print("\nDesglose por fecha en el CSV:")

por_fecha = {}
for reg in registros:
    fecha = reg.get('fecha_reporte', 'SIN FECHA')
    if fecha not in por_fecha:
        por_fecha[fecha] = 0
    por_fecha[fecha] += 1

for fecha in sorted(por_fecha.keys()):
    print(f"  {fecha}: {por_fecha[fecha]} registros")
