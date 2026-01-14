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
            deuda_total REAL,
            gasto_admin REAL,
            fecha_creacion TEXT NOT NULL
        )
        ''')
    else:
        # Agregar columnas si no existen
        cursor.execute("PRAGMA table_info(rucs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'deuda_total' not in columns:
            cursor.execute('ALTER TABLE rucs ADD COLUMN deuda_total REAL')
        
        if 'gasto_admin' not in columns:
            cursor.execute('ALTER TABLE rucs ADD COLUMN gasto_admin REAL')
    
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
            estado_ga TEXT DEFAULT 'A VENCER',
            promesa_planilla TEXT,
            monto_planilla REAL,
            fecha_pago_planilla TEXT,
            estado_planilla TEXT DEFAULT 'A VENCER',
            observaciones TEXT,
            fecha_registro TEXT NOT NULL
        )
        ''')
    else:
        # Agregar columnas de estado si no existen
        cursor.execute("PRAGMA table_info(registros_pagos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'estado_ga' not in columns:
            cursor.execute('ALTER TABLE registros_pagos ADD COLUMN estado_ga TEXT DEFAULT "A VENCER"')
        
        if 'estado_planilla' not in columns:
            cursor.execute('ALTER TABLE registros_pagos ADD COLUMN estado_planilla TEXT DEFAULT "A VENCER"')
    
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
    
    cursor.execute('SELECT id, ruc, id_documento, razon_social, campaña, asesor, deuda_total, gasto_admin FROM rucs WHERE ruc = ?', (ruc,))
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
    
    # Determinar estado de promesas automáticamente
    estado_ga = 'A VENCER'
    estado_planilla = 'A VENCER'
    
    # Si la fecha de pago ya pasó y aún no hay cobro registrado
    hoy = date.today()
    if fecha_pago_gasto and promesa_ga:
        try:
            fecha_pago = datetime.strptime(fecha_pago_gasto, '%Y-%m-%d').date()
            if fecha_pago < hoy:
                estado_ga = 'PROMESA CAIDA'
        except:
            pass
    
    if fecha_pago_planilla and promesa_planilla:
        try:
            fecha_pago = datetime.strptime(fecha_pago_planilla, '%Y-%m-%d').date()
            if fecha_pago < hoy:
                estado_planilla = 'PROMESA CAIDA'
        except:
            pass
    
    cursor.execute('''
    INSERT INTO registros_pagos 
    (fecha_reporte, ruc, id_documento, campaña, asesor, 
     promesa_ga, monto_gasto, fecha_pago_gasto, estado_ga,
     promesa_planilla, monto_planilla, fecha_pago_planilla, estado_planilla,
     observaciones, fecha_registro)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fecha_reporte, ruc, id_documento, campaña, asesor,
          promesa_ga, monto_gasto, fecha_pago_gasto, estado_ga,
          promesa_planilla, monto_planilla, fecha_pago_planilla, estado_planilla,
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

def detectar_duplicado_exacto(fecha_reporte, ruc, id_documento, campaña, asesor,
                              promesa_ga=None, monto_gasto=None, fecha_pago_gasto=None,
                              promesa_planilla=None, monto_planilla=None, fecha_pago_planilla=None,
                              observaciones=""):
    """
    Detecta si existe un registro exactamente igual (mismo RUC, fecha y todos los datos)
    Retorna: (existe_duplicado, id_duplicado, mensaje)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id FROM registros_pagos
    WHERE 
        fecha_reporte = ?
        AND ruc = ?
        AND id_documento = ?
        AND campaña = ?
        AND COALESCE(asesor, '') = COALESCE(?, '')
        AND COALESCE(promesa_ga, '') = COALESCE(?, '')
        AND COALESCE(monto_gasto, 0) = COALESCE(?, 0)
        AND COALESCE(fecha_pago_gasto, '') = COALESCE(?, '')
        AND COALESCE(promesa_planilla, '') = COALESCE(?, '')
        AND COALESCE(monto_planilla, 0) = COALESCE(?, 0)
        AND COALESCE(fecha_pago_planilla, '') = COALESCE(?, '')
        AND COALESCE(observaciones, '') = COALESCE(?, '')
    LIMIT 1
    ''', (fecha_reporte, ruc, id_documento, campaña, asesor,
          promesa_ga, monto_gasto, fecha_pago_gasto,
          promesa_planilla, monto_planilla, fecha_pago_planilla,
          observaciones))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return True, resultado[0], f"⚠️ Duplicado detectado: Este registro ya existe (ID: {resultado[0]})"
    else:
        return False, None, None

def obtener_ranking_asesores(fecha_inicio=None, fecha_fin=None):
    """Obtiene ranking de asesores por total cobrado en el período"""
    if fecha_inicio is None:
        fecha_inicio = date.today().isoformat()
    
    if fecha_fin is None:
        fecha_fin = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        COALESCE(asesor, 'SIN ASESOR') as asesor,
        COUNT(DISTINCT ruc) as total_rucs,
        COUNT(DISTINCT CASE WHEN monto_gasto > 0 THEN ruc END) as rucs_ga,
        COUNT(DISTINCT CASE WHEN monto_planilla > 0 THEN ruc END) as rucs_planilla,
        COALESCE(SUM(CASE WHEN monto_gasto > 0 THEN monto_gasto ELSE 0 END), 0) as total_ga,
        COALESCE(SUM(CASE WHEN monto_planilla > 0 THEN monto_planilla ELSE 0 END), 0) as total_planilla,
        COALESCE(SUM(CASE WHEN monto_gasto > 0 THEN monto_gasto ELSE 0 END), 0) 
        + COALESCE(SUM(CASE WHEN monto_planilla > 0 THEN monto_planilla ELSE 0 END), 0) as total_cobrado
    FROM registros_pagos
    WHERE fecha_reporte BETWEEN ? AND ?
    GROUP BY asesor
    ORDER BY total_cobrado DESC
    ''', (fecha_inicio, fecha_fin))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return resultados

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

def obtener_resumen_asesores_diario(fecha=None):
    """Obtiene resumen diario de lo cobrado por cada asesor (GA + Planilla)"""
    if fecha is None:
        fecha = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        COALESCE(asesor, 'SIN ASESOR') as asesor,
        COUNT(DISTINCT CASE WHEN monto_gasto > 0 THEN ruc END) as rucs_ga,
        COUNT(DISTINCT CASE WHEN monto_planilla > 0 THEN ruc END) as rucs_planilla,
        COALESCE(SUM(CASE WHEN fecha_pago_gasto = ? AND monto_gasto > 0 THEN monto_gasto ELSE 0 END), 0) as total_ga,
        COALESCE(SUM(CASE WHEN fecha_pago_planilla = ? AND monto_planilla > 0 THEN monto_planilla ELSE 0 END), 0) as total_planilla
    FROM registros_pagos
    WHERE (fecha_pago_gasto = ? OR fecha_pago_planilla = ?)
    GROUP BY asesor
    ORDER BY (total_ga + total_planilla) DESC
    ''', (fecha, fecha, fecha, fecha))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return resultados

def obtener_promesas_pendientes(fecha_inicio=None, fecha_fin=None):
    """Obtiene promesas pendientes (A VENCER) con fecha de pago entre dos fechas"""
    if fecha_inicio is None:
        fecha_inicio = date.today().isoformat()
    
    if fecha_fin is None:
        # Por defecto, mostrar los próximos 30 días
        fecha_fin = (date.today() + __import__('datetime').timedelta(days=30)).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # RUCs con promesas A VENCER que tengan fecha de pago en el rango especificado
    cursor.execute('''
    SELECT DISTINCT
        ruc,
        id_documento,
        asesor,
        campaña,
        promesa_ga,
        promesa_planilla,
        CASE 
            WHEN promesa_ga = 'A VEN...' AND fecha_pago_gasto != '' AND fecha_pago_gasto IS NOT NULL THEN fecha_pago_gasto
            WHEN promesa_planilla = 'A VEN...' AND fecha_pago_planilla != '' AND fecha_pago_planilla IS NOT NULL THEN fecha_pago_planilla
            ELSE NULL
        END as fecha_pago_pendiente,
        MAX(fecha_reporte) as ultima_fecha
    FROM registros_pagos
    WHERE 
        (promesa_ga = 'A VEN...' OR promesa_planilla = 'A VEN...')
        AND (
            (promesa_ga = 'A VEN...' AND fecha_pago_gasto BETWEEN ? AND ? AND fecha_pago_gasto != '')
            OR (promesa_planilla = 'A VEN...' AND fecha_pago_planilla BETWEEN ? AND ? AND fecha_pago_planilla != '')
        )
    GROUP BY ruc
    ORDER BY fecha_pago_pendiente, asesor, ruc
    ''', (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return resultados

def obtener_estadisticas_montos():
    """Obtiene estadísticas de montos para detectar valores anormales"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Estadísticas de Gasto Administrativo
    cursor.execute('''
    SELECT 
        AVG(monto_gasto) as promedio_ga,
        MIN(monto_gasto) as min_ga,
        MAX(monto_gasto) as max_ga,
        COUNT(*) as count_ga
    FROM registros_pagos
    WHERE monto_gasto > 0
    ''')
    
    stats_ga = cursor.fetchone()
    
    # Estadísticas de Planilla
    cursor.execute('''
    SELECT 
        AVG(monto_planilla) as promedio_plan,
        MIN(monto_planilla) as min_plan,
        MAX(monto_planilla) as max_plan,
        COUNT(*) as count_plan
    FROM registros_pagos
    WHERE monto_planilla > 0
    ''')
    
    stats_plan = cursor.fetchone()
    
    conn.close()
    
    return {
        'ga': stats_ga if stats_ga[0] else (0, 0, 0, 0),
        'planilla': stats_plan if stats_plan[0] else (0, 0, 0, 0)
    }

def detectar_monto_anormal(monto, tipo_pago='ga'):
    """
    Detecta si un monto es anormalmente alto o bajo
    tipo_pago: 'ga' o 'planilla'
    Retorna: (es_anormal, tipo_anomalia, mensaje)
    """
    if monto <= 0:
        return False, None, None
    
    stats = obtener_estadisticas_montos()
    
    if tipo_pago == 'ga':
        promedio, minimo, maximo, count = stats['ga']
    else:
        promedio, minimo, maximo, count = stats['planilla']
    
    # Si no hay suficientes datos, no alertar
    if count == 0 or promedio == 0:
        return False, None, None
    
    # Calcular rangos tolerables (50% - 150% del promedio)
    rango_bajo = promedio * 0.5
    rango_alto = promedio * 1.5
    
    # Casos de alerta
    if monto < rango_bajo:
        porcentaje = (monto / promedio * 100) if promedio > 0 else 0
        return True, "BAJO", (
            f"⚠️ **Monto ANORMALMENTE BAJO**\n\n"
            f"Monto ingresado: S/. {monto:,.2f}\n"
            f"Promedio histórico: S/. {promedio:,.2f}\n"
            f"Porcentaje del promedio: {porcentaje:.1f}%\n\n"
            f"Este monto es **{100-porcentaje:.0f}% menor** al promedio."
        )
    
    elif monto > rango_alto:
        porcentaje = (monto / promedio * 100) if promedio > 0 else 0
        return True, "ALTO", (
            f"⚠️ **Monto ANORMALMENTE ALTO**\n\n"
            f"Monto ingresado: S/. {monto:,.2f}\n"
            f"Promedio histórico: S/. {promedio:,.2f}\n"
            f"Porcentaje del promedio: {porcentaje:.1f}%\n\n"
            f"Este monto es **{porcentaje-100:.0f}% mayor** al promedio."
        )
    
    return False, None, None

def actualizar_rucs_desde_excel(excel_path="DATA ENERO 2026.xlsx"):
    """Actualiza los datos de deuda_total y gasto_admin desde el Excel"""
    try:
        # Leer Excel
        df = pd.read_excel(excel_path)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Mapear columnas del Excel
        for _, row in df.iterrows():
            documento = str(row.get('DOCUMENTO', '')).strip()
            deuda_total = float(row.get('DEUDA TOTAL', 0)) if pd.notna(row.get('DEUDA TOTAL')) else None
            gasto_admin = float(row.get('GASTOS ADMIN', 0)) if pd.notna(row.get('GASTOS ADMIN')) else None
            
            # Buscar RUC por ID Documento
            cursor.execute('SELECT id FROM rucs WHERE id_documento = ?', (documento,))
            resultado = cursor.fetchone()
            
            if resultado:
                ruc_id = resultado[0]
                cursor.execute('''
                    UPDATE rucs 
                    SET deuda_total = ?, gasto_admin = ?
                    WHERE id = ?
                ''', (deuda_total, gasto_admin, ruc_id))
        
        conn.commit()
        conn.close()
        return True, "Datos del Excel actualizados correctamente"
    except Exception as e:
        return False, f"Error al actualizar datos: {str(e)}"
def detectar_promesas_caidas(fecha_actual=None):
    """Detecta promesas que vencieron pero no fueron cobradas (PROMESAS CAIDAS)
    y actualiza su estado automáticamente. También revierte el estado de promesas
    que se marcaron como caídas pero cuya fecha aún no ha pasado."""
    if fecha_actual is None:
        fecha_actual = date.today()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener promesas que están en estado 'A VENCER' o 'PROMESA CAIDA'
    cursor.execute('''
    SELECT id, fecha_pago_gasto, estado_ga, fecha_pago_planilla, estado_planilla
    FROM registros_pagos
    WHERE (estado_ga IN ('A VENCER', 'PROMESA CAIDA') OR estado_planilla IN ('A VENCER', 'PROMESA CAIDA'))
    ''')
    
    registros = cursor.fetchall()
    caidas_ga = []
    caidas_planilla = []
    
    for registro in registros:
        registro_id, fecha_ga, estado_ga, fecha_planilla, estado_planilla = registro
        
        # Verificar promesa GA
        if fecha_ga and estado_ga in ('A VENCER', 'PROMESA CAIDA'):
            try:
                fecha_pago = datetime.strptime(fecha_ga, '%Y-%m-%d').date()
                
                if fecha_pago < fecha_actual and estado_ga == 'A VENCER':
                    # La fecha pasó y aún está "A VENCER" → Marcar como CAIDA
                    cursor.execute('UPDATE registros_pagos SET estado_ga = ? WHERE id = ?', 
                                 ('PROMESA CAIDA', registro_id))
                    caidas_ga.append(registro_id)
                elif fecha_pago >= fecha_actual and estado_ga == 'PROMESA CAIDA':
                    # La fecha aún no pasa pero está marcada como CAIDA → Revertir a "A VENCER"
                    cursor.execute('UPDATE registros_pagos SET estado_ga = ? WHERE id = ?', 
                                 ('A VENCER', registro_id))
            except:
                pass
        
        # Verificar promesa Planilla
        if fecha_planilla and estado_planilla in ('A VENCER', 'PROMESA CAIDA'):
            try:
                fecha_pago = datetime.strptime(fecha_planilla, '%Y-%m-%d').date()
                
                if fecha_pago < fecha_actual and estado_planilla == 'A VENCER':
                    # La fecha pasó y aún está "A VENCER" → Marcar como CAIDA
                    cursor.execute('UPDATE registros_pagos SET estado_planilla = ? WHERE id = ?', 
                                 ('PROMESA CAIDA', registro_id))
                    caidas_planilla.append(registro_id)
                elif fecha_pago >= fecha_actual and estado_planilla == 'PROMESA CAIDA':
                    # La fecha aún no pasa pero está marcada como CAIDA → Revertir a "A VENCER"
                    cursor.execute('UPDATE registros_pagos SET estado_planilla = ? WHERE id = ?', 
                                 ('A VENCER', registro_id))
            except:
                pass
    
    conn.commit()
    conn.close()
    
    return caidas_ga, caidas_planilla

def obtener_promesas_caidas(fecha_inicio=None, fecha_fin=None):
    """Obtiene todas las promesas caídas en un rango de fechas
    Solo muestra promesas que están como CAIDA pero cuyo estado original era A VENCER"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if fecha_inicio is None:
        fecha_inicio = (date.today() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')
    if fecha_fin is None:
        fecha_fin = date.today().strftime('%Y-%m-%d')
    
    # Promesas GA caídas (excluir si ALGUNO de los dos está COBRADO)
    cursor.execute('''
    SELECT id, fecha_reporte, ruc, id_documento, campaña, asesor,
           'GASTO ADMINISTRATIVO' as tipo_promesa,
           promesa_ga as estado_promesa, monto_gasto as monto,
           fecha_pago_gasto as fecha_vencimiento, observaciones
    FROM registros_pagos
    WHERE estado_ga = 'PROMESA CAIDA'
    AND estado_ga != 'COBRADO' AND estado_planilla != 'COBRADO'
    AND fecha_reporte BETWEEN ? AND ?
    ORDER BY fecha_pago_gasto DESC
    ''', (fecha_inicio, fecha_fin))
    
    caidas_ga = cursor.fetchall()
    
    # Promesas Planilla caídas (excluir si ALGUNO de los dos está COBRADO)
    cursor.execute('''
    SELECT id, fecha_reporte, ruc, id_documento, campaña, asesor,
           'PLANILLA' as tipo_promesa,
           promesa_planilla as estado_promesa, monto_planilla as monto,
           fecha_pago_planilla as fecha_vencimiento, observaciones
    FROM registros_pagos
    WHERE estado_planilla = 'PROMESA CAIDA'
    AND estado_ga != 'COBRADO' AND estado_planilla != 'COBRADO'
    AND fecha_reporte BETWEEN ? AND ?
    ORDER BY fecha_pago_planilla DESC
    ''', (fecha_inicio, fecha_fin))
    
    caidas_planilla = cursor.fetchall()
    
    conn.close()
    
    # Combinar resultados
    todas_caidas = caidas_ga + caidas_planilla
    return sorted(todas_caidas, key=lambda x: x[9] if x[9] else '', reverse=True)

def marcar_promesa_cobrada(registro_id, tipo_promesa):
    """Marca una promesa caída como cobrada"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if tipo_promesa == 'GASTO ADMINISTRATIVO':
        cursor.execute('UPDATE registros_pagos SET estado_ga = ? WHERE id = ?',
                     ('COBRADO', registro_id))
    else:
        cursor.execute('UPDATE registros_pagos SET estado_planilla = ? WHERE id = ?',
                     ('COBRADO', registro_id))
    
    conn.commit()
    conn.close()
    return True

def obtener_estadisticas_promesas_caidas():
    """Obtiene estadísticas de promesas caídas
    Los pagos de PLANILLA y GASTO ADMINISTRATIVO son independientes
    Se cuentan solo si su estado es PROMESA CAIDA
    Excluye si ALGUNO está COBRADO
    Los RUCs se cuentan sin duplicados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Filtro: mostrar si CUALQUIERA es PROMESA CAIDA, PERO excluir si ALGUNO está COBRADO
    filtro_caidas = "(estado_ga = 'PROMESA CAIDA' OR estado_planilla = 'PROMESA CAIDA') AND estado_ga != 'COBRADO' AND estado_planilla != 'COBRADO'"
    
    # Total de promesas caídas
    cursor.execute(f'''
    SELECT COUNT(*) FROM registros_pagos
    WHERE {filtro_caidas}
    ''')
    total_caidas = cursor.fetchone()[0]
    
    # RUCs únicos con promesas caídas
    cursor.execute(f'''
    SELECT COUNT(DISTINCT ruc) FROM registros_pagos
    WHERE {filtro_caidas}
    ''')
    rucs_unicos = cursor.fetchone()[0]
    
    # Monto total de promesas caídas
    cursor.execute(f'''
    SELECT COALESCE(SUM(CASE WHEN estado_ga = 'PROMESA CAIDA'
                             THEN monto_gasto ELSE 0 END), 0) +
           COALESCE(SUM(CASE WHEN estado_planilla = 'PROMESA CAIDA'
                             THEN monto_planilla ELSE 0 END), 0)
    FROM registros_pagos
    WHERE estado_ga != 'COBRADO' AND estado_planilla != 'COBRADO'
    '''
    )
    monto_total = cursor.fetchone()[0] or 0
    
    # Por asesor (RUCs únicos)
    cursor.execute(f'''
    SELECT asesor, COUNT(DISTINCT ruc) as cantidad
    FROM registros_pagos
    WHERE {filtro_caidas}
    GROUP BY asesor
    ORDER BY cantidad DESC
    ''')
    por_asesor = cursor.fetchall()
    
    # Por campaña (RUCs únicos)
    cursor.execute(f'''
    SELECT campaña, COUNT(DISTINCT ruc) as cantidad
    FROM registros_pagos
    WHERE {filtro_caidas}
    GROUP BY campaña
    ORDER BY cantidad DESC
    ''')
    por_campana = cursor.fetchall()
    
    conn.close()
    
    return {
        'total': total_caidas,
        'rucs_unicos': rucs_unicos,
        'monto_total': monto_total,
        'por_asesor': por_asesor,
        'por_campana': por_campana
    }


def convertir_a_vencer_a_caidas(registros):
    """
    Convierte 'A VENCER' a 'PROMESA CAIDA' si la fecha de vencimiento ya pasó.
    
    Recibe: lista de tuplas con registros
    Retorna: lista modificada donde 'A VENCER' con fecha pasada se convierte a 'PROMESA CAIDA'
    """
    if not registros:
        return registros
    
    registros_procesados = []
    hoy = date.today()
    
    for registro in registros:
        # Convertir tupla a lista para poder modificarla
        registro_list = list(registro)
        
        # Índices esperados: 6=Promesa GA, 8=Fecha Pago GA, 9=Promesa Planilla, 11=Fecha Pago Planilla
        
        # Procesar Promesa Gastos Admin (índice 6) y su fecha (índice 8)
        if len(registro_list) > 8:
            promesa_ga = registro_list[6]
            fecha_pago_ga = registro_list[8]
            
            if promesa_ga == "A VENCER" and fecha_pago_ga:
                try:
                    if isinstance(fecha_pago_ga, str):
                        fecha_obj = datetime.fromisoformat(fecha_pago_ga).date()
                    else:
                        fecha_obj = fecha_pago_ga
                    
                    if fecha_obj < hoy:
                        registro_list[6] = "PROMESA CAIDA"
                except (ValueError, TypeError):
                    pass  # Si hay error parsing la fecha, dejar como está
        
        # Procesar Promesa Planilla (índice 9) y su fecha (índice 11)
        if len(registro_list) > 11:
            promesa_planilla = registro_list[9]
            fecha_pago_planilla = registro_list[11]
            
            if promesa_planilla == "A VENCER" and fecha_pago_planilla:
                try:
                    if isinstance(fecha_pago_planilla, str):
                        fecha_obj = datetime.fromisoformat(fecha_pago_planilla).date()
                    else:
                        fecha_obj = fecha_pago_planilla
                    
                    if fecha_obj < hoy:
                        registro_list[9] = "PROMESA CAIDA"
                except (ValueError, TypeError):
                    pass  # Si hay error parsing la fecha, dejar como está
        
        registros_procesados.append(tuple(registro_list))
    
    return registros_procesados