#!/usr/bin/env python3
"""
Script para exportar datos de pagos a CSV
Uso: python export_data.py
"""

import os
from database import exportar_a_csv, obtener_resumen_por_ruc

def main():
    archivo_salida = r"C:\Users\USUARIO\Desktop\REGISTRO DE PAGOS\DATA ENERO 2026.csv"
    
    print("=" * 60)
    print("Sistema de Exportación de Datos de Pagos")
    print("=" * 60)
    print()
    
    try:
        # Obtener resumen
        resumen = obtener_resumen_por_ruc()
        
        if not resumen:
            print("❌ No hay datos para exportar")
            return
        
        # Exportar a CSV
        exito = exportar_a_csv(archivo_salida)
        
        if exito:
            print(f"✅ Archivo exportado exitosamente")
            print(f"📁 Ubicación: {archivo_salida}")
            print()
            
            # Mostrar resumen
            print("📊 RESUMEN DE EXPORTACIÓN")
            print("-" * 60)
            print(f"Total de RUCs: {len(resumen)}")
            
            total_debe = sum(r['Total Debe Pagar'] for r in resumen)
            total_pagado = sum(r['Total Pagado'] for r in resumen)
            total_pendiente = sum(r['Total Pendiente'] for r in resumen)
            total_caida = sum(r['Total Promesas Caídas'] for r in resumen)
            
            print(f"Total a Recaudar: S/. {total_debe:,.2f}")
            print(f"Total Recaudado: S/. {total_pagado:,.2f}")
            print(f"Total Pendiente: S/. {total_pendiente:,.2f}")
            print(f"Total Promesas Caídas: S/. {total_caida:,.2f}")
            print()
            
            # Mostrar detalle por RUC
            print("📋 DETALLE POR RUC")
            print("-" * 60)
            for registro in resumen:
                print(f"\nRUC: {registro['RUC']} - {registro['Nombre Empresa']}")
                print(f"  Planilla Total: S/. {registro['Planilla Total']:,.2f}")
                print(f"  Gastos Total: S/. {registro['Gastos Total']:,.2f}")
                print(f"  Debe Pagar: S/. {registro['Total Debe Pagar']:,.2f}")
                print(f"  Ha Pagado: S/. {registro['Total Pagado']:,.2f}")
                print(f"  Pendiente: S/. {registro['Total Pendiente']:,.2f}")
                if registro['Total Promesas Caídas'] > 0:
                    print(f"  Promesas Caídas: S/. {registro['Total Promesas Caídas']:,.2f}")
        else:
            print("❌ Error al exportar los datos")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
