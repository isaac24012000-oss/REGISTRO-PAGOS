#!/usr/bin/env python3
"""
Detectar y eliminar registros duplicados
"""

import sqlite3

conn = sqlite3.connect("pagos.db")
cursor = conn.cursor()

print("=" * 70)
print("Detectando registros duplicados")
print("=" * 70)

# Obtener todos los registros
cursor.execute('''
SELECT id, fecha_reporte, ruc, id_documento, campaña, asesor, 
       promesa_ga, monto_gasto, fecha_pago_gasto,
       promesa_planilla, monto_planilla, fecha_pago_planilla,
       observaciones
FROM registros_pagos
ORDER BY ruc, fecha_reporte
''')

registros = cursor.fetchall()

# Agrupar por (RUC, fecha_reporte) para detectar duplicados
duplicados_dict = {}
for registro in registros:
    id_reg = registro[0]
    fecha = registro[1]
    ruc = registro[2]
    
    key = (ruc, fecha)
    
    if key not in duplicados_dict:
        duplicados_dict[key] = []
    
    duplicados_dict[key].append(registro)

# Encontrar duplicados
registros_a_eliminar = []
for key, regs in duplicados_dict.items():
    if len(regs) > 1:
        ruc, fecha = key
        print(f"\n🔍 RUC {ruc} en fecha {fecha}: {len(regs)} registros")
        for i, reg in enumerate(regs, 1):
            print(f"   {i}. ID: {reg[0]}")
        
        # Mantener el primero, eliminar los demás
        for reg in regs[1:]:
            registros_a_eliminar.append(reg[0])
            print(f"   ❌ Marcar para eliminar ID: {reg[0]}")

print(f"\n{'=' * 70}")
print(f"Total de registros duplicados encontrados: {len(registros_a_eliminar)}")
print(f"{'=' * 70}")

if registros_a_eliminar:
    print(f"\n⚠️ Se eliminarán {len(registros_a_eliminar)} registros duplicados...")
    
    # Eliminar duplicados
    for id_reg in registros_a_eliminar:
        cursor.execute('DELETE FROM registros_pagos WHERE id = ?', (id_reg,))
    
    conn.commit()
    print("✅ Registros duplicados eliminados")
    
    # Contar nuevamente
    cursor.execute("SELECT COUNT(*) FROM registros_pagos")
    total_nuevo = cursor.fetchone()[0]
    
    print(f"\n📊 Resumen:")
    print(f"   Registros antes: {len(registros)}")
    print(f"   Registros eliminados: {len(registros_a_eliminar)}")
    print(f"   Registros después: {total_nuevo}")
else:
    print("\n✅ No se encontraron registros duplicados")

conn.close()
