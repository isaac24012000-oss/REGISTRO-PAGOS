import sqlite3

ruc_buscar = "20609059541"

conn = sqlite3.connect('pagos.db')
cursor = conn.cursor()

# Buscar en pagos_planilla
cursor.execute('SELECT COUNT(*) FROM pagos_planilla WHERE ruc = ?', (ruc_buscar,))
count_planilla = cursor.fetchone()[0]

# Buscar en gastos_administrativos
cursor.execute('SELECT COUNT(*) FROM gastos_administrativos WHERE ruc = ?', (ruc_buscar,))
count_gastos = cursor.fetchone()[0]

print(f"RUC {ruc_buscar}:")
print(f"  - En pagos_planilla: {count_planilla} registros")
print(f"  - En gastos_administrativos: {count_gastos} registros")

if count_planilla == 0 and count_gastos == 0:
    print(f"\nEl RUC {ruc_buscar} NO existe en la BD")
    print("\nPrimeros 10 RUCs en la BD:")
    cursor.execute('SELECT DISTINCT ruc FROM pagos_planilla LIMIT 10')
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
else:
    print(f"\nEl RUC {ruc_buscar} SÍ existe en la BD")

conn.close()
