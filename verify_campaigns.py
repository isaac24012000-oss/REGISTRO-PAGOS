import sqlite3
conn = sqlite3.connect('pagos.db')
cursor = conn.cursor()

# Check campaigns
cursor.execute('SELECT DISTINCT campana FROM pagos_planilla ORDER BY campana')
campanas = cursor.fetchall()
print('📌 Campañas en pagos_planilla:')
for c in campanas:
    print(f'  - {c[0]}')

print('\n📊 Registros por campaña:')
cursor.execute('SELECT COUNT(*) as total, campana FROM pagos_planilla GROUP BY campana')
for row in cursor.fetchall():
    print(f'  {row[1]}: {row[0]} registros')

# Check RUCs with campaigns
print('\n🔍 Primeros 5 RUCs con sus campañas:')
cursor.execute('SELECT DISTINCT r.ruc, r.nombre, p.campana FROM rucs r LEFT JOIN pagos_planilla p ON r.id = p.ruc_id WHERE p.campana IS NOT NULL LIMIT 5')
for row in cursor.fetchall():
    print(f'  RUC: {row[0]}, Nombre: {row[1]}, Campaña: {row[2]}')

conn.close()
print('\n✅ Base de datos verificada correctamente')
