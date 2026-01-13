#!/usr/bin/env python3
"""
Script para registrar múltiples pagos de ejemplo en la BD
"""

from database import registrar_pago

# Datos de pagos a registrar (del screenshot)
pagos = [
    {
        'fecha_reporte': '2026-01-09',
        'ruc': '10040852943',
        'id_documento': '76666241',
        'campaña': 'FLUJO',
        'asesor': 'Laura ...',
        'promesa_ga': 'A VEN...',
        'monto_gasto': 66.1,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'A VEN...',
        'monto_planilla': 342.4,
        'fecha_pago_planilla': '2026-01-13',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-09',
        'ruc': '10088604666',
        'id_documento': '76666286',
        'campaña': 'FLUJO',
        'asesor': 'Laura ...',
        'promesa_ga': 'A VEN...',
        'monto_gasto': 190,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'A VEN...',
        'monto_planilla': 1070.24,
        'fecha_pago_planilla': '2026-01-13',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-09',
        'ruc': '23899664',
        'id_documento': '76666395',
        'campaña': 'FLUJO',
        'asesor': 'Lesly ...',
        'promesa_ga': 'A VEN...',
        'monto_gasto': 101.06,
        'fecha_pago_gasto': '2026-01-12',
        'promesa_planilla': 'A VEN...',
        'monto_planilla': 570.96,
        'fecha_pago_planilla': '2026-01-12',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-12',
        'ruc': '4700231',
        'id_documento': '76666613',
        'campaña': 'FLUJO',
        'asesor': 'Lesly ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 121.32,
        'fecha_pago_gasto': '2026-01-12',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 684.78,
        'fecha_pago_planilla': '2026-01-12',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-09',
        'ruc': '20529438843',
        'id_documento': '76667745',
        'campaña': 'REDI...',
        'asesor': 'Tereza ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 213.43,
        'fecha_pago_gasto': '2026-01-09',
        'promesa_planilla': 'A VEN...',
        'monto_planilla': 1205.82,
        'fecha_pago_planilla': '2026-01-28',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-09',
        'ruc': '20470389363',
        'id_documento': '76636120',
        'campaña': 'PRES...',
        'asesor': 'Carla ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 223.24,
        'fecha_pago_gasto': '2026-01-12',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 1264.19,
        'fecha_pago_planilla': '2026-01-19',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-09',
        'ruc': '2050970848',
        'id_documento': '76676857',
        'campaña': 'REDI...',
        'asesor': 'Carla ...',
        'promesa_ga': 'A VEN...',
        'monto_gasto': 755,
        'fecha_pago_gasto': '2026-01-16',
        'promesa_planilla': 'A VEN...',
        'monto_planilla': 3330.51,
        'fecha_pago_planilla': '2026-01-16',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-09',
        'ruc': '20179523745',
        'id_documento': '76666746',
        'campaña': 'FLUJO',
        'asesor': 'Lesly ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 130,
        'fecha_pago_gasto': '2026-01-09',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 735,
        'fecha_pago_planilla': '2026-01-09',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-13',
        'ruc': '6919452',
        'id_documento': '76666258',
        'campaña': 'FLUJO',
        'asesor': 'Lesly ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 73.25,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 415,
        'fecha_pago_planilla': '2026-01-13',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-12',
        'ruc': '20557377892',
        'id_documento': '76668331',
        'campaña': 'FLUJO',
        'asesor': 'Lesly ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 66.1,
        'fecha_pago_gasto': '2026-01-12',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 259.78,
        'fecha_pago_planilla': '2026-01-12',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-12',
        'ruc': '20607538809',
        'id_documento': '76670444',
        'campaña': 'FLUJO',
        'asesor': 'Lesly ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 66.1,
        'fecha_pago_gasto': '2026-01-12',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 257.22,
        'fecha_pago_planilla': '2026-01-12',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-12',
        'ruc': '10703532174',
        'id_documento': '76666634',
        'campaña': 'FLUJO',
        'asesor': 'Laura ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 66.1,
        'fecha_pago_gasto': '2026-01-12',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 233.35,
        'fecha_pago_planilla': '2026-01-12',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-13',
        'ruc': '20611154322',
        'id_documento': '76671371',
        'campaña': 'FLUJO',
        'asesor': 'Laura ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 82,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 459.8,
        'fecha_pago_planilla': '2026-01-13',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-13',
        'ruc': '20610053689',
        'id_documento': '76671088',
        'campaña': 'FLUJO',
        'asesor': 'Lesly ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 66.1,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 206.91,
        'fecha_pago_planilla': '2026-01-14',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-13',
        'ruc': '20547121628',
        'id_documento': '76668067',
        'campaña': 'FLUJO',
        'asesor': 'Laura ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 174.86,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 997.78,
        'fecha_pago_planilla': '2026-01-13',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-13',
        'ruc': '20609420031',
        'id_documento': '76670897',
        'campaña': 'FLUJO',
        'asesor': 'Laura ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 66.1,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 259.78,
        'fecha_pago_planilla': '2026-01-08',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-13',
        'ruc': '20609059541',
        'id_documento': '76670806',
        'campaña': 'FLUJO',
        'asesor': 'Laura ...',
        'promesa_ga': 'COBR...',
        'monto_gasto': 84,
        'fecha_pago_gasto': '2026-01-13',
        'promesa_planilla': 'COBR...',
        'monto_planilla': 473.27,
        'fecha_pago_planilla': '2026-01-13',
        'observaciones': ''
    },
    {
        'fecha_reporte': '2026-01-13',
        'ruc': '20498791728',
        'id_documento': '76676455',
        'campaña': 'REDI...',
        'asesor': 'Carla ...',
        'promesa_ga': 'A VEN...',
        'monto_gasto': 311.45,
        'fecha_pago_gasto': '2026-01-15',
        'promesa_planilla': 'A VEN...',
        'monto_planilla': 1759.55,
        'fecha_pago_planilla': '2026-01-19',
        'observaciones': 'convenio 2 tramos'
    }
]

contador = 0
for pago in pagos:
    try:
        registro_id = registrar_pago(**pago)
        contador += 1
        print(f"✅ [{contador}] Registrado - RUC: {pago['ruc']} - Total: S/. {pago['monto_gasto'] + pago['monto_planilla']:,.2f}")
    except Exception as e:
        print(f"❌ Error en RUC {pago['ruc']}: {e}")

print(f"\n{'='*60}")
print(f"✅ TOTAL: {contador} pagos registrados exitosamente")
print(f"{'='*60}")
