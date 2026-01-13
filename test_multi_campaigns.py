import sqlite3

conn = sqlite3.connect('pagos.db')
cursor = conn.cursor()

# Find RUCs in multiple campaigns
cursor.execute('''
SELECT ruc, COUNT(DISTINCT campana) as campana_count
FROM pagos_planilla
GROUP BY ruc
HAVING campana_count > 1
LIMIT 10
''')

print("🔍 RUCs que existen en múltiples campañas:")
for row in cursor.fetchall():
    ruc = row[0]
    count = row[1]
    cursor.execute('SELECT DISTINCT campana FROM pagos_planilla WHERE ruc = ?', (ruc,))
    campanas = [c[0] for c in cursor.fetchall()]
    print(f"  RUC {ruc}: {campanas} ({count} campañas)")

conn.close()
