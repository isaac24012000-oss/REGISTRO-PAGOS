#!/usr/bin/env python3
"""
Importar datos del archivo CSV existente a la base de datos
"""

import csv
from database import agregar_ruc, DB_PATH
import sqlite3

def importar_csv_a_bd(archivo_csv='DATA ENERO 2026.csv'):
    """Importa datos del CSV a la base de datos"""
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contador = 0
            
            for fila in reader:
                try:
                    ruc = fila.get('DOCUMENTO', '').strip()
                    razon_social = fila.get('RAZON SOCIAL', '').strip()
                    deuda_total_str = fila.get('DEUDA TOTAL', '0').replace('S/ ', '').replace(',', '')
                    gastos_admin_str = fila.get('GASTOS ADMIN', '0').replace('S/ ', '').replace(',', '')
                    
                    if ruc and razon_social:
                        # Intentar agregar el RUC
                        exito, mensaje = agregar_ruc(ruc, razon_social)
                        if exito:
                            contador += 1
                            print(f"✅ {ruc} - {razon_social}")
                        
                except Exception as e:
                    print(f"⚠️ Error en fila: {str(e)}")
            
            print(f"\n✅ Se importaron {contador} RUCs correctamente")
            return contador
    
    except Exception as e:
        print(f"❌ Error al importar: {str(e)}")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("Importar datos del CSV a la base de datos")
    print("=" * 60)
    print()
    importar_csv_a_bd()
