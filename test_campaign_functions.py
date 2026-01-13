from database import obtener_rucs_con_campanas, obtener_campanas

print("📌 Obteniendo RUCs con campañas...")
rucs_campanas = obtener_rucs_con_campanas()

print(f"\n✅ Total de RUC-Campaña combinaciones: {len(rucs_campanas)}")
print("\nPrimeros 10 ejemplos:")
for rc in rucs_campanas[:10]:
    print(f"  RUC: {rc[1]}, Nombre: {rc[2]}, Campaña: {rc[3]}")

print("\n📌 Obteniendo campañas disponibles...")
campanas = obtener_campanas()
print(f"Campañas: {campanas}")

print("\n✅ Funciones de campaña verificadas correctamente")
