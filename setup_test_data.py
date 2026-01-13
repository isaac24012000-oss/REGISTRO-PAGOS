#!/usr/bin/env python3
"""
Script para agregar datos de prueba y exportar CSV
"""

from database import init_db, agregar_ruc, registrar_pago_planilla, registrar_gasto_administrativo, exportar_a_csv

# Inicializar BD
init_db()

# Agregar RUCs de prueba
print("Agregando RUCs de prueba...")
rucs = [
    ("12345678", "EMPRESA TEST S.A.C."),
    ("87654321", "COMERCIAL NUEVO S.A."),
    ("11111111", "DISTRIBUIDORA ABC"),
]

for ruc, nombre in rucs:
    exito, msg = agregar_ruc(ruc, nombre)
    if exito:
        print(f"✅ {ruc} - {nombre}")

print("\nAgregando pagos de prueba...")

# Agregar pagos de prueba
registrar_pago_planilla(1, "12345678", 1000.00, "COBRADO", observaciones="Pago realizado")
registrar_pago_planilla(1, "12345678", 500.00, "PROMESA", "2026-02-15", "Pago aplazado")
registrar_gasto_administrativo(1, "12345678", 200.00, "COBRADO")

registrar_pago_planilla(2, "87654321", 2000.00, "COBRADO")
registrar_pago_planilla(2, "87654321", 1000.00, "PROMESA", "2026-01-20")
registrar_gasto_administrativo(2, "87654321", 300.00, "PROMESA", "2026-01-18")

registrar_pago_planilla(3, "11111111", 1500.00, "COBRADO")
registrar_gasto_administrativo(3, "11111111", 250.00, "COBRADO")

print("✅ Pagos registrados")

# Exportar a CSV
print("\nExportando a CSV...")
ruta = r'C:\Users\USUARIO\Desktop\REGISTRO DE PAGOS\Resumen_Pagos_Enero_2026.csv'
try:
    exportar_a_csv(ruta)
    print(f"✅ CSV exportado exitosamente")
    print(f"📁 Ubicación: {ruta}")
except Exception as e:
    print(f"❌ Error: {e}")
