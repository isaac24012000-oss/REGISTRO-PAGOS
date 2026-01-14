#!/usr/bin/env python3
"""
Script para verificar que todas las importaciones funcionan
"""

print("Verificando importaciones...")

try:
    from database import (
        init_db,
        obtener_rucs,
        obtener_ruc_por_numero,
        registrar_pago,
        obtener_registros_hoy,
        obtener_todos_registros,
        obtener_estadisticas_hoy,
        actualizar_registro,
        eliminar_registro,
        exportar_a_csv,
        obtener_campanas_unicas,
        obtener_asesores_unicos,
        obtener_registros_por_fecha,
        obtener_promesas_hoy,
        obtener_estadisticas_promesas_hoy,
        obtener_resumen_por_asesor_promesa,
        obtener_resumen_total_por_promesa,
        obtener_resumen_diario_asesores
    )
    print("✓ Todas las importaciones son correctas")
    
    # Verificar que la función nueva funciona
    resultados = obtener_resumen_diario_asesores()
    print(f"✓ Función obtener_resumen_diario_asesores() funciona correctamente")
    print(f"  Registros encontrados: {len(resultados)}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
