from datetime import datetime
import pandas as pd

def formatear_fecha(fecha_str):
    """Formatea una fecha ISO a formato legible"""
    if not fecha_str:
        return "-"
    try:
        fecha = datetime.fromisoformat(fecha_str)
        return fecha.strftime('%d/%m/%Y %H:%M')
    except:
        return fecha_str

def formatear_moneda(monto):
    """Formatea un monto como moneda"""
    try:
        monto_float = float(monto) if isinstance(monto, str) else monto
        return f"S/. {monto_float:,.2f}"
    except:
        return f"S/. {monto}"

def obtener_color_estado(estado):
    """Retorna un color según el estado"""
    colores = {
        'PENDIENTE': '#808080',
        'COBRADO': '#00b50a',
        'PROMESA': '#ffa500',
        'PROMESA CAIDA': '#ff0000',
    }
    return colores.get(estado, '#808080')

def crear_dataframe_pagos(pagos):
    """Crea un DataFrame formateado de pagos"""
    if not pagos:
        return pd.DataFrame()
    
    datos = []
    for pago in pagos:
        datos.append({
            'ID': pago[0],
            'RUC': pago[1],
            'Campaña': pago[2],
            'Monto': formatear_moneda(pago[3]),
            'Fecha Registro': formatear_fecha(pago[4]),
            'Fecha Pago': formatear_fecha(pago[5]),
            'Estado': pago[6],
            'Fecha Promesa': formatear_fecha(pago[7]),
            'Observaciones': pago[8] if pago[8] else '-'
        })
    
    return pd.DataFrame(datos)

def verificar_promesas_vencidas():
    """Verifica y marca las promesas vencidas"""
    from database import (
        obtener_pagos_planilla, 
        obtener_gastos_administrativos,
        actualizar_estado_pago
    )
    from datetime import datetime
    
    hoy = datetime.now().date()
    
    # Verificar promesas de planilla
    promesas_planilla = obtener_pagos_planilla()
    for pago in promesas_planilla:
        if pago[5] == 'PROMESA' and pago[6]:  # estado == PROMESA y tiene fecha_promesa
            try:
                fecha_promesa = datetime.fromisoformat(pago[6]).date()
                if fecha_promesa < hoy:
                    actualizar_estado_pago('pagos_planilla', pago[0], 'PROMESA CAIDA')
            except:
                pass
    
    # Verificar promesas de gastos
    promesas_gastos = obtener_gastos_administrativos()
    for gasto in promesas_gastos:
        if gasto[5] == 'PROMESA' and gasto[6]:  # estado == PROMESA y tiene fecha_promesa
            try:
                fecha_promesa = datetime.fromisoformat(gasto[6]).date()
                if fecha_promesa < hoy:
                    actualizar_estado_pago('gastos_administrativos', gasto[0], 'PROMESA CAIDA')
            except:
                pass
