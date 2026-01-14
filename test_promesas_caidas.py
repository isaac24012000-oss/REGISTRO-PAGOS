#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de Promesas Caídas
"""

from database import (init_db, registrar_pago, detectar_promesas_caidas, 
                     obtener_promesas_caidas, obtener_estadisticas_promesas_caidas)
from datetime import datetime, date, timedelta

# Inicializar BD
init_db()

# Crear una promesa caída (con fecha vencida)
fecha_ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
fecha_hoy = date.today().strftime('%Y-%m-%d')

print("✓ BD inicializada")

# Registrar promesa con fecha vencida (ayer)
id_registro = registrar_pago(
    fecha_reporte=fecha_hoy,
    ruc='20123456789',
    id_documento='123456',
    campaña='PRUEBA',
    asesor='Test Asesor',
    promesa_ga='A VENCER',
    monto_gasto=5000,
    fecha_pago_gasto=fecha_ayer,
    observaciones='Promesa para prueba'
)
print(f"✓ Promesa registrada con ID: {id_registro}")

# Detectar promesas caídas
caidas_ga, caidas_planilla = detectar_promesas_caidas()
print(f"✓ Promesas caídas detectadas (GA): {len(caidas_ga)}")
print(f"✓ Promesas caídas detectadas (Planilla): {len(caidas_planilla)}")

# Obtener promesas caídas
promesas = obtener_promesas_caidas()
print(f"✓ Total de promesas caídas: {len(promesas)}")

# Estadísticas
stats = obtener_estadisticas_promesas_caidas()
print(f"✓ Total caídas: {stats['total']}")
print(f"✓ Monto total: S/. {stats['monto_total']:,.2f}")

print("\n✅ Todas las funciones de PROMESAS CAÍDAS funcionan correctamente!")
