#!/usr/bin/env python3
"""
Módulo de base de datos para Sistema de Registro de Pagos Diarios
Estructura: Tabla de RUCs base + Tabla de registros de pagos diarios
"""

import sqlite3
from datetime import datetime, date
import pandas as pd

DB_PATH = "pagos.db"

def init_db():
    """Inicializa la base de datos (ya fue creada por clean_db.py)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar que las tablas existan
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rucs'")
    if not cursor.fetchone():
        # Si no existe, crearlas
        cursor.execute('''
        CREATE TABLE rucs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ruc TEXT UNIQUE NOT NULL,
            id_documento TEXT UNIQUE NOT NULL,
            razon_social TEXT NOT NULL,
            campaña TEXT NOT NULL,
            asesor TEXT,
            fecha_creacion TEXT NOT NULL
        )
        ''')
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registros_pagos'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE registros_pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_reporte TEXT NOT NULL,
            ruc TEXT NOT NULL,
            id_documento TEXT NOT NULL,
            campaña TEXT NOT NULL,
            asesor TEXT,
            promesa_ga TEXT,
            monto_gasto REAL,
            fecha_pago_gasto TEXT,
            promesa_planilla TEXT,
            monto_planilla REAL,
            fecha_pago_planilla TEXT,
            observaciones TEXT,
            fecha_registro TEXT NOT NULL
        )
        ''')
    
    conn.commit()
    conn.close()

def obtener_rucs():
    """Obtiene todos los RUCs base"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, ruc, razon_social, campaña, asesor FROM rucs ORDER BY ruc')
    rucs = cursor.fetchall()
    conn.close()
    return rucs

def obtener_ruc_por_numero(ruc):
    """Obtiene información de un RUC específico"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, ruc, id_documento, razon_social, campaña, asesor FROM rucs WHERE ruc = ?', (ruc,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def obtener_rucs_con_campanas():
    """Obtiene todos los RUCs con sus campañas asociadas como lista de tuplas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT DISTINCT ruc, campaña FROM rucs ORDER BY ruc
    ''')
    
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def obtener_campanas():
    """Obtiene todas las campañas únicas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT campaña FROM rucs ORDER BY campaña')
    campanas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return campanas

def registrar_pago(fecha_reporte, ruc, id_documento, campaña, asesor,
                   promesa_ga=None, monto_gasto=None, fecha_pago_gasto=None,
                   promesa_planilla=None, monto_planilla=None, fecha_pago_planilla=None,
                   observaciones=""):
    """Registra un pago diario con la estructura especificada"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    fecha_registro = datetime.now().isoformat()
    
    cursor.execute('''
    INSERT INTO registros_pagos 
    (fecha_reporte, ruc, id_documento, campaña, asesor, 
     promesa_ga, monto_gasto, fecha_pago_gasto,
     promesa_planilla, monto_planilla, fecha_pago_planilla,
     observaciones, fecha_registro)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fecha_reporte, ruc, id_documento, campaña, asesor,
          promesa_ga, monto_gasto, fecha_pago_gasto,
          promesa_planilla, monto_planilla, fecha_pago_planilla,
          observaciones, fecha_registro))
    
    conn.commit()
    registro_id = cursor.lastrowid
    conn.close()
    return registro_id

def obtener_registros_por_fecha(fecha):
    """Obtiene todos los registros de una fecha específica"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, fecha_reporte, ruc, id_documento, campaña, asesor,
           promesa_ga, monto_gasto, fecha_pago_gasto,
           promesa_planilla, monto_planilla, fecha_pago_planilla,
           observaciones
    FROM registros_pagos
    WHERE fecha_reporte = ?
    ORDER BY ruc
    ''', (fecha,))
    
    registros = cursor.fetchall()
    conn.close()
    return registros

def obtener_registros_hoy():
    """Obtiene los registros de hoy"""
    hoy = date.today().isoformat()
    return obtener_registros_por_fecha(hoy)

def obtener_todos_registros():
    """Obtiene todos los registros"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, fecha_reporte, ruc, id_documento, campaña, asesor,
           promesa_ga, monto_gasto, fecha_pago_gasto,
           promesa_planilla, monto_planilla, fecha_pago_planilla,
           observaciones
    FROM registros_pagos
    ORDER BY fecha_reporte DESC, ruc
    ''')
    
    registros = cursor.fetchall()
    conn.close()
    return registros

def actualizar_registro(registro_id, **campos):
    """Actualiza un registro de pago existente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Construir query dinámicamente
    campos_permitidos = [
        'promesa_ga', 'monto_gasto', 'fecha_pago_gasto',
        'promesa_planilla', 'monto_planilla', 'fecha_pago_planilla',
        'observaciones'
    ]
    
    campos_update = {k: v for k, v in campos.items() if k in campos_permitidos}
    
    if campos_update:
        set_clause = ', '.join([f"{k} = ?" for k in campos_update.keys()])
        valores = list(campos_update.values()) + [registro_id]
        
        cursor.execute(f'UPDATE registros_pagos SET {set_clause} WHERE id = ?', valores)
        conn.commit()
    
    conn.close()

def eliminar_registro(registro_id):
    """Elimina un registro de pago"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM registros_pagos WHERE id = ?', (registro_id,))
    conn.commit()
    conn.close()

def obtener_estadisticas_hoy():
    """Obtiene estadísticas de pagos de hoy"""
    hoy = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total de montos registrados
    cursor.execute('''
    SELECT 
        COUNT(*) as total_registros,
        SUM(CASE WHEN monto_gasto > 0 THEN 1 ELSE 0 END) as registros_gasto,
        SUM(CASE WHEN monto_planilla > 0 THEN 1 ELSE 0 END) as registros_planilla,
        SUM(COALESCE(monto_gasto, 0)) as total_gasto,
        SUM(COALESCE(monto_planilla, 0)) as total_planilla,
        SUM(COALESCE(monto_gasto, 0) + COALESCE(monto_planilla, 0)) as total_cobrado
    FROM registros_pagos
    WHERE fecha_reporte = ?
    ''', (hoy,))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        'total_registros': stats[0] or 0,
        'registros_gasto': stats[1] or 0,
        'registros_planilla': stats[2] or 0,
        'total_gasto': stats[3] or 0,
        'total_planilla': stats[4] or 0,
        'total_cobrado': stats[5] or 0
    }

def obtener_ruc_por_id(ruc_id):
    """Obtiene información del RUC basado en ruc_id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, ruc, id_documento, razon_social, campaña FROM rucs WHERE id = ?', (ruc_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def obtener_resumen_por_ruc():
    """Obtiene un resumen de registros por RUC"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        ruc,
        COUNT(*) as total_registros,
        SUM(COALESCE(monto_gasto, 0)) as total_gasto,
        SUM(COALESCE(monto_planilla, 0)) as total_planilla,
        SUM(COALESCE(monto_gasto, 0) + COALESCE(monto_planilla, 0)) as total_cobrado
    FROM registros_pagos
    GROUP BY ruc
    ORDER BY ruc
    ''')
    
    resumen = cursor.fetchall()
    conn.close()
    return resumen

def exportar_a_csv():
    """Exporta registros a CSV"""
    df = pd.read_sql_query('SELECT * FROM registros_pagos ORDER BY fecha_reporte DESC', 
                          sqlite3.connect(DB_PATH))
    filename = f"registros_pagos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8')
    return filename

def importar_excel(file_path):
    """Ya no se usa - los RUCs se importaron con clean_db.py"""
    pass

def obtener_campanas_unicas():
    """Obtiene las campañas únicas de los RUCs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT campaña FROM rucs ORDER BY campaña')
    campanas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return campanas

def obtener_asesores_unicos():
    """Obtiene los asesores únicos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT asesor FROM rucs WHERE asesor IS NOT NULL ORDER BY asesor')
    asesores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return asesores

def obtener_promesas_por_fecha(fecha):
    """Obtiene los pagos prometidos para una fecha específica (solo A VENCER)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Pagos de gasto prometidos para esa fecha (solo A VENCER)
    cursor.execute('''
    SELECT id, fecha_reporte, ruc, id_documento, campaña, asesor,
           promesa_ga, monto_gasto, fecha_pago_gasto,
           'GASTO' as tipo_pago, observaciones
    FROM registros_pagos
    WHERE fecha_pago_gasto = ? AND promesa_ga = 'A VEN...'
    UNION ALL
    SELECT id, fecha_reporte, ruc, id_documento, campaña, asesor,
           promesa_planilla, monto_planilla, fecha_pago_planilla,
           'PLANILLA' as tipo_pago, observaciones
    FROM registros_pagos
    WHERE fecha_pago_planilla = ? AND promesa_planilla = 'A VEN...'
    ORDER BY ruc
    ''', (fecha, fecha))
    
    registros = cursor.fetchall()
    conn.close()
    return registros

def obtener_promesas_hoy():
    """Obtiene los pagos prometidos para hoy"""
    hoy = date.today().isoformat()
    return obtener_promesas_por_fecha(hoy)

def obtener_estadisticas_promesas_hoy():
    """Obtiene estadísticas de promesas para hoy (solo A VENCER)"""
    hoy = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Promesas de Gasto para hoy (solo A VENCER)
    cursor.execute('''
    SELECT COUNT(*), SUM(COALESCE(monto_gasto, 0))
    FROM registros_pagos
    WHERE fecha_pago_gasto = ? AND promesa_ga = 'A VEN...'
    ''', (hoy,))
    
    gasto_result = cursor.fetchone()
    gasto_count = gasto_result[0] or 0
    gasto_monto = gasto_result[1] or 0
    
    # Promesas de Planilla para hoy (solo A VENCER)
    cursor.execute('''
    SELECT COUNT(*), SUM(COALESCE(monto_planilla, 0))
    FROM registros_pagos
    WHERE fecha_pago_planilla = ? AND promesa_planilla = 'A VEN...'
    ''', (hoy,))
    
    planilla_result = cursor.fetchone()
    planilla_count = planilla_result[0] or 0
    planilla_monto = planilla_result[1] or 0
    
    conn.close()
    
    return {
        'promesas_gasto_count': gasto_count,
        'promesas_gasto_monto': gasto_monto,
        'promesas_planilla_count': planilla_count,
        'promesas_planilla_monto': planilla_monto,
        'total_promesas': gasto_count + planilla_count,
        'total_monto_promesas': gasto_monto + planilla_monto
    }

def obtener_resumen_por_asesor_promesa(tipo_pago='gasto', fecha=None):
    """
    Obtiene resumen agrupado por Asesor y Promesa
    tipo_pago: 'gasto' o 'planilla'
    fecha: fecha específica o None para hoy
    """
    if fecha is None:
        fecha = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if tipo_pago == 'gasto':
        # Resumen de Gasto Administrativo
        cursor.execute('''
        SELECT 
            asesor,
            promesa_ga as promesa,
            COUNT(*) as count_ruc,
            SUM(COALESCE(monto_gasto, 0)) as monto
        FROM registros_pagos
        WHERE fecha_pago_gasto = ? AND monto_gasto > 0
        GROUP BY asesor, promesa_ga
        ORDER BY asesor, promesa_ga
        ''', (fecha,))
    else:
        # Resumen de Planilla
        cursor.execute('''
        SELECT 
            asesor,
            promesa_planilla as promesa,
            COUNT(*) as count_ruc,
            SUM(COALESCE(monto_planilla, 0)) as monto
        FROM registros_pagos
        WHERE fecha_pago_planilla = ? AND monto_planilla > 0
        GROUP BY asesor, promesa_planilla
        ORDER BY asesor, promesa_planilla
        ''', (fecha,))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return resultados

def obtener_resumen_total_por_promesa(tipo_pago='gasto', fecha=None):
    """Obtiene totales por Promesa (A VENCER, COBRADO, Total)"""
    if fecha is None:
        fecha = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if tipo_pago == 'gasto':
        cursor.execute('''
        SELECT 
            promesa_ga as promesa,
            COUNT(*) as count_ruc,
            SUM(COALESCE(monto_gasto, 0)) as monto
        FROM registros_pagos
        WHERE fecha_pago_gasto = ? AND monto_gasto > 0
        GROUP BY promesa_ga
        ORDER BY promesa_ga
        ''', (fecha,))
    else:
        cursor.execute('''
        SELECT 
            promesa_planilla as promesa,
            COUNT(*) as count_ruc,
            SUM(COALESCE(monto_planilla, 0)) as monto
        FROM registros_pagos
        WHERE fecha_pago_planilla = ? AND monto_planilla > 0
        GROUP BY promesa_planilla
        ORDER BY promesa_planilla
        ''', (fecha,))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return resultados

