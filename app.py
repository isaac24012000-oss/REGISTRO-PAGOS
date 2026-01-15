#!/usr/bin/env python3
"""
Sistema de Registro de Pagos Diarios
Interfaz Streamlit para registrar pagos según la estructura especificada
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
import os
from database import (
    init_db,
    obtener_rucs,
    obtener_ruc_por_numero,
    registrar_pago,
    obtener_registros_hoy,
    obtener_todos_registros,
    obtener_estadisticas_hoy,
    actualizar_registro,
    eliminar_registro,
    exportar_a_csv,
    obtener_campanas_unicas,
    obtener_asesores_unicos,
    obtener_registros_por_fecha,
    obtener_promesas_hoy,
    obtener_estadisticas_promesas_hoy,
    obtener_resumen_por_asesor_promesa,
    obtener_resumen_total_por_promesa,
    obtener_resumen_asesores_diario,
    obtener_promesas_pendientes,
    detectar_duplicado_exacto,
    obtener_ranking_asesores,
    detectar_monto_anormal,
    actualizar_rucs_desde_excel,
    detectar_promesas_caidas
)

# Configuración
st.set_page_config(
    page_title="📊 Registro de Pagos Diarios",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado - Tema azul/celeste
st.markdown("""
    <style>
    /* Variables de colores */
    :root {
        --primary-blue: #4A90E2;
        --secondary-blue: #357ABD;
        --light-blue: #E8F4F8;
        --sky-blue: #F0F8FF;
        --accent-cyan: #00BCD4;
    }
    
    /* Fondo general */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #F5FAFB 0%, #E8F4F8 100%);
    }
    
    /* Botones del menú */
    .menu-button {
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 600;
        border: 2px solid;
        transition: all 0.3s ease;
    }
    
    /* Tarjetas de métricas */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.1);
        border-left: 5px solid #4A90E2;
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        box-shadow: 0 8px 25px rgba(74, 144, 226, 0.2);
        transform: translateY(-2px);
    }
    
    /* Headers de secciones */
    h2 {
        color: #357ABD;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    h3 {
        color: #4A90E2;
        font-weight: 600;
    }
    
    /* Dividers */
    hr {
        border: 1px solid rgba(74, 144, 226, 0.2);
        margin: 20px 0;
    }
    
    /* Contenedores de secciones */
    .section-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-top: 4px solid #4A90E2;
    }
    
    /* Botones estilizados */
    button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
    }
    
    /* Tablas */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Info boxes */
    [data-testid="stInfo"] {
        background: linear-gradient(135deg, #E3F2FD 0%, #F0F8FF 100%);
        border-left: 4px solid #4A90E2;
        border-radius: 8px;
    }
    
    [data-testid="stSuccess"] {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
    }
    
    [data-testid="stWarning"] {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFFDE7 100%);
        border-left: 4px solid #FF9800;
        border-radius: 8px;
    }
    
    [data-testid="stError"] {
        background: linear-gradient(135deg, #FFEBEE 0%, #FCE4EC 100%);
        border-left: 4px solid #F44336;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# JavaScript para cerrar el sidebar automáticamente
st.markdown("""
    <script>
    function closeSidebar() {
        const buttons = document.querySelectorAll('button');
        for (let button of buttons) {
            const ariaLabel = button.getAttribute('aria-label');
            if (ariaLabel && ariaLabel.includes('Toggle')) {
                button.click();
                break;
            }
        }
    }
    setTimeout(closeSidebar, 100);
    </script>
""", unsafe_allow_html=True)

# Inicializar BD
init_db()

# Actualizar datos de Deuda Total y Gasto Admin desde Excel
actualizar_rucs_desde_excel()

# Cargar RUCs desde Excel si la BD está vacía
@st.cache_resource
def cargar_rucs_si_necesario():
    """Carga los RUCs desde Excel si la BD está vacía"""
    conn = sqlite3.connect("pagos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rucs")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        # BD vacía, importar datos
        try:
            from import_excel import importar_excel_a_bd
            importar_excel_a_bd()
        except Exception as e:
            st.warning(f"⚠️ No se pudieron cargar los RUCs: {e}")

# Ejecutar carga de RUCs
cargar_rucs_si_necesario()

# Inicializar sesión para mantener estado del formulario
if 'ruc_registrado' not in st.session_state:
    st.session_state.ruc_registrado = None
if 'ruc_info_encontrada' not in st.session_state:
    st.session_state.ruc_info_encontrada = None
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "📊 Dashboard"

# Título principal
st.title("💰 Sistema de Registro de Pagos Diarios")

# Botón Registrar Pago flotante a la derecha
col_title, col_btn = st.columns([0.85, 0.15])
with col_btn:
    if st.button("📝 Registrar\nPago", use_container_width=True, 
                help="Registrar nuevo pago"):
        st.session_state.pagina_actual = "📝 Registrar Pago"
        st.rerun()

st.markdown("---")

menu_opciones = [
    "📊 Dashboard",
    "👥 Resumen de Asesores",
    "🏆 Ranking de Asesores",
    "⏳ Promesas Pendientes",
    "🎯 Promesas de Hoy",
    " Ver Registros",
    "📂 Exportar Datos"
]

# Colores para cada botón
colores_botones = {
    "📊 Dashboard": "#4A90E2",
    "👥 Resumen de Asesores": "#9C27B0",
    "🏆 Ranking de Asesores": "#FF9800",
    "⏳ Promesas Pendientes": "#F44336",
    "🎯 Promesas de Hoy": "#E91E63",
    "📝 Registrar Pago": "#2196F3",
    "📋 Ver Registros": "#009688",
    "📂 Exportar Datos": "#FFC107"
}

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #E3F2FD 0%, #F0F8FF 100%); 
                    border-radius: 12px; padding: 15px; margin: 10px 0;
                    border-left: 5px solid #4A90E2;'>
            <h3 style='margin: 0; color: #357ABD;'>🎯 Menú</h3>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    
    # Botones de navegación en el sidebar
    for opcion_btn in menu_opciones:
        if st.button(opcion_btn, use_container_width=True, key=f"btn_{opcion_btn}",
                    help=f"Ir a {opcion_btn}"):
            st.session_state.pagina_actual = opcion_btn
            st.rerun()
    
    st.divider()
    st.markdown("**📅 FILTROS**")
    st.markdown("")
    
    # Mostrar estado de la BD
    registros_total = len(obtener_todos_registros())
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric("📊 Registros", registros_total)
    with col2:
        st.info("✓ Guardado")
    
    st.divider()
    st.markdown("")

opcion = st.session_state.pagina_actual

# ======================== DASHBOARD ========================
if opcion == "📊 Dashboard":
    st.markdown("""
        <div style='background: linear-gradient(135deg, #E3F2FD 0%, #F0F8FF 100%); 
                    border-radius: 12px; padding: 20px; margin: 10px 0;
                    border-left: 5px solid #4A90E2;'>
            <h2 style='margin: 0; color: #357ABD;'>📊 Dashboard de Pagos</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Filtro de fecha en la barra lateral
    with st.sidebar:
        fecha_filtro = st.date_input(
            "📅 Selecciona fecha:",
            value=date.today(),
            key="fecha_dashboard"
        )
    
    # Convertir promesas vencidas a PROMESA CAIDA antes de obtener datos
    detectar_promesas_caidas()
    
    # Obtener datos con la fecha seleccionada
    resumen_gasto = obtener_resumen_total_por_promesa(tipo_pago='gasto', fecha=fecha_filtro)
    resumen_planilla = obtener_resumen_total_por_promesa(tipo_pago='planilla', fecha=fecha_filtro)
    resumen_asesor_gasto = obtener_resumen_por_asesor_promesa(tipo_pago='gasto', fecha=fecha_filtro)
    resumen_asesor_planilla = obtener_resumen_por_asesor_promesa(tipo_pago='planilla', fecha=fecha_filtro)
    
    # Obtener todos los registros de la fecha para contar RUCs únicos
    registros_fecha = obtener_registros_por_fecha(fecha_filtro)
    
    # Calcular totales
    total_gasto = sum(r[2] for r in resumen_gasto) if resumen_gasto else 0
    total_planilla = sum(r[2] for r in resumen_planilla) if resumen_planilla else 0
    
    # Contar RUCs únicos (no duplicados)
    rucs_unicos = set(r[2] for r in registros_fecha)  # r[2] es el RUC
    total_rucs_unicos = len(rucs_unicos)
    
    # Mantener conteos separados por promesa para las tablas
    total_rucs_gasto = sum(r[1] for r in resumen_gasto) if resumen_gasto else 0
    total_rucs_planilla = sum(r[1] for r in resumen_planilla) if resumen_planilla else 0
    total_general = total_gasto + total_planilla
    
    # Mostrar fecha seleccionada
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    mes_nombre = meses[fecha_filtro.month - 1]
    fecha_texto = f"{fecha_filtro.day} de {mes_nombre} de {fecha_filtro.year}"
    st.subheader(fecha_texto)
    
    # ===== RESUMEN GENERAL =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Gasto Admin", f"S/. {total_gasto:,.2f}")
    
    with col2:
        st.metric("📋 Planilla", f"S/. {total_planilla:,.2f}")
    
    with col3:
        st.metric("📦 RUCs Gasto", total_rucs_gasto)
    
    with col4:
        st.metric("📦 RUCs Planilla", total_rucs_planilla)
    
    st.markdown("---")
    
    # ===== COLUMNAS LADO A LADO =====
    col_gasto, col_planilla = st.columns(2)
    
    # ===== GASTO ADMINISTRATIVO (COLUMNA IZQUIERDA) =====
    with col_gasto:
        st.subheader("💵 GASTO ADMINISTRATIVO")
        
        if resumen_gasto:
            # Métricas de gasto
            a_vencer_gasto = [r for r in resumen_gasto if r[0] == 'A VEN...']
            promesas_caidas_gasto = [r for r in resumen_gasto if r[0] == 'PROMESA CAIDA']
            cobrado_gasto = [r for r in resumen_gasto if r[0] == 'COBR...']
            
            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                if promesas_caidas_gasto:
                    # Mostrar Promesas Caídas en rojo
                    st.markdown(
                        f"<div style='background-color: #ffcccc; border-left: 4px solid #ff0000; padding: 15px; border-radius: 8px;'>"
                        f"<p style='margin: 0; font-size: 18px; font-weight: bold; color: #cc0000;'>⚠️ Promesas Caídas</p>"
                        f"<p style='margin: 5px 0; font-size: 24px; color: #cc0000; font-weight: bold;'>S/. {promesas_caidas_gasto[0][2]:,.2f}</p>"
                        f"<p style='margin: 5px 0; color: #990000;'>📦 {promesas_caidas_gasto[0][1]} RUCs</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                elif a_vencer_gasto:
                    st.info(f"⏳ A Vencer\n\n💰 S/. {a_vencer_gasto[0][2]:,.2f}\n\n📦 {a_vencer_gasto[0][1]} RUCs")
                else:
                    st.warning("⏳ A Vencer: Sin datos")
            
            with m_col2:
                if cobrado_gasto:
                    st.success(f"✅ Cobrado\n\n💰 S/. {cobrado_gasto[0][2]:,.2f}\n\n📦 {cobrado_gasto[0][1]} RUCs")
                else:
                    st.warning("✅ Cobrado: Sin datos")
            
            st.markdown("")
            
            # Tabla detalle por asesor
            if resumen_asesor_gasto:
                st.write("**Detalle por Asesor:**")
                tabla_gasto = []
                for asesor, promesa, count, monto in resumen_asesor_gasto:
                    if promesa == 'PROMESA CAIDA':
                        estado_icon = '⚠️'
                    elif promesa == 'A VEN...':
                        estado_icon = '⏳'
                    else:
                        estado_icon = '✅'
                    
                    tabla_gasto.append({
                        'Asesor': asesor.split()[0] if asesor else 'N/A',  # Nombre corto
                        'Estado': estado_icon,
                        'Monto': f"S/. {monto:,.0f}",
                        'RUCs': count
                    })
                
                df_gasto_display = pd.DataFrame(tabla_gasto)
                st.dataframe(df_gasto_display, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Sin registros de gasto administrativo")
    
    # ===== PLANILLA (COLUMNA DERECHA) =====
    with col_planilla:
        st.subheader("📋 PLANILLA")
        
        if resumen_planilla:
            # Métricas de planilla
            a_vencer_plan = [r for r in resumen_planilla if r[0] == 'A VEN...']
            promesas_caidas_plan = [r for r in resumen_planilla if r[0] == 'PROMESA CAIDA']
            cobrado_plan = [r for r in resumen_planilla if r[0] == 'COBR...']
            
            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                if promesas_caidas_plan:
                    # Mostrar Promesas Caídas en rojo
                    st.markdown(
                        f"<div style='background-color: #ffcccc; border-left: 4px solid #ff0000; padding: 15px; border-radius: 8px;'>"
                        f"<p style='margin: 0; font-size: 18px; font-weight: bold; color: #cc0000;'>⚠️ Promesas Caídas</p>"
                        f"<p style='margin: 5px 0; font-size: 24px; color: #cc0000; font-weight: bold;'>S/. {promesas_caidas_plan[0][2]:,.2f}</p>"
                        f"<p style='margin: 5px 0; color: #990000;'>📦 {promesas_caidas_plan[0][1]} RUCs</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                elif a_vencer_plan:
                    st.info(f"⏳ A Vencer\n\n💰 S/. {a_vencer_plan[0][2]:,.2f}\n\n📦 {a_vencer_plan[0][1]} RUCs")
                else:
                    st.warning("⏳ A Vencer: Sin datos")
            
            with m_col2:
                if cobrado_plan:
                    st.success(f"✅ Cobrado\n\n💰 S/. {cobrado_plan[0][2]:,.2f}\n\n📦 {cobrado_plan[0][1]} RUCs")
                else:
                    st.warning("✅ Cobrado: Sin datos")
            
            st.markdown("")
            
            # Tabla detalle por asesor
            if resumen_asesor_planilla:
                st.write("**Detalle por Asesor:**")
                tabla_planilla = []
                for asesor, promesa, count, monto in resumen_asesor_planilla:
                    if promesa == 'PROMESA CAIDA':
                        estado_icon = '⚠️'
                    elif promesa == 'A VEN...':
                        estado_icon = '⏳'
                    else:
                        estado_icon = '✅'
                    
                    tabla_planilla.append({
                        'Asesor': asesor.split()[0] if asesor else 'N/A',  # Nombre corto
                        'Estado': estado_icon,
                        'Monto': f"S/. {monto:,.0f}",
                        'RUCs': count
                    })
                
                df_planilla_display = pd.DataFrame(tabla_planilla)
                st.dataframe(df_planilla_display, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Sin registros de planilla")
    
    st.markdown("---")
    
    # ===== RESUMEN TOTAL =====
    st.subheader("💼 Resumen General del Día")
    
    resumen_col1, resumen_col2, resumen_col3, resumen_col4 = st.columns(4)
    
    with resumen_col1:
        st.metric("💵 Total Gasto Admin", f"S/. {total_gasto:,.2f}")
    
    with resumen_col2:
        st.metric("📋 Total Planilla", f"S/. {total_planilla:,.2f}")
    
    with resumen_col3:
        st.metric("👥 Total RUCs", total_rucs_unicos)
    
    with resumen_col4:
        st.metric("📝 Registros", len(registros_fecha))

# ======================== RESUMEN DE ASESORES ========================
elif opcion == "👥 Resumen de Asesores":
    st.header("👥 Resumen Diario de Asesores")
    
    # Filtro de fecha en la barra lateral
    with st.sidebar:
        st.markdown("### 📅 Filtros")
        fecha_filtro_asesores = st.date_input(
            "Selecciona fecha:",
            value=date.today(),
            key="fecha_asesores"
        )
    
    # Obtener datos de asesores
    resumen_asesores = obtener_resumen_asesores_diario(fecha=fecha_filtro_asesores)
    
    # Mostrar fecha seleccionada
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    mes_nombre = meses[fecha_filtro_asesores.month - 1]
    fecha_texto = f"{fecha_filtro_asesores.day} de {mes_nombre} de {fecha_filtro_asesores.year}"
    st.subheader(fecha_texto)
    
    if resumen_asesores:
        # Calcular totales
        total_general_ga = sum(r[3] for r in resumen_asesores)
        total_general_planilla = sum(r[4] for r in resumen_asesores)
        total_general_combined = total_general_ga + total_general_planilla
        
        # Mostrar métricas de resumen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💵 Total Gasto Admin", f"S/. {total_general_ga:,.2f}")
        
        with col2:
            st.metric("📋 Total Planilla", f"S/. {total_general_planilla:,.2f}")
        
        with col3:
            st.metric("💰 Total Cobrado", f"S/. {total_general_combined:,.2f}")
        
        st.markdown("---")
        
        # Tabla detallada
        st.subheader("📊 Desglose por Asesor")
        
        tabla_asesores = []
        for asesor, rucs_ga, rucs_planilla, total_ga, total_planilla in resumen_asesores:
            total_asesor = total_ga + total_planilla
            tabla_asesores.append({
                'Asesor': asesor,
                'GA (RUCs)': f"{rucs_ga}",
                'GA (Monto)': f"S/. {total_ga:,.2f}",
                'Planilla (RUCs)': f"{rucs_planilla}",
                'Planilla (Monto)': f"S/. {total_planilla:,.2f}",
                'Total': f"S/. {total_asesor:,.2f}"
            })
        
        df_asesores = pd.DataFrame(tabla_asesores)
        st.dataframe(df_asesores, use_container_width=True, hide_index=True)
        
        # Gráfico de comparación
        st.markdown("---")
        st.subheader("📈 Gráficos de Comparación")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Gráfico de barras - Total por asesor
            datos_chart = []
            for asesor, rucs_ga, rucs_planilla, total_ga, total_planilla in resumen_asesores:
                datos_chart.append({
                    'Asesor': asesor.split()[0] if asesor and asesor != 'SIN ASESOR' else asesor,
                    'GA': total_ga,
                    'Planilla': total_planilla
                })
            
            df_chart = pd.DataFrame(datos_chart)
            st.bar_chart(df_chart.set_index('Asesor'))
        
        with col_chart2:
            # Gráfico de pie - Distribución total
            datos_pie = []
            for asesor, rucs_ga, rucs_planilla, total_ga, total_planilla in resumen_asesores:
                total_asesor = total_ga + total_planilla
                if total_asesor > 0:
                    datos_pie.append({
                        'Asesor': asesor.split()[0] if asesor and asesor != 'SIN ASESOR' else asesor,
                        'Total': total_asesor
                    })
            
            if datos_pie:
                df_pie = pd.DataFrame(datos_pie)
                st.bar_chart(df_pie.set_index('Asesor'))
    
    else:
        st.info("ℹ️ No hay datos de pagos registrados para esta fecha")

# ======================== RANKING DE ASESORES ========================
elif opcion == "🏆 Ranking de Asesores":
    st.header("🏆 Ranking de Asesores por Cobros")
    
    st.markdown("")
    
    # Opciones de período
    col1, col2 = st.columns([2, 2])
    
    with col1:
        periodo = st.radio(
            "",
            ["Hoy", "Este Mes", "Personalizado"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    st.markdown("")
    
    # Determinar rango de fechas según el período seleccionado
    if periodo == "Hoy":
        fecha_inicio = date.today()
        fecha_fin = date.today()
        titulo_periodo = "Hoy"
    elif periodo == "Este Mes":
        hoy = date.today()
        fecha_inicio = date(hoy.year, hoy.month, 1)
        fecha_fin = hoy
        titulo_periodo = f"Enero 2026"  # Mes actual
    else:  # Personalizado
        col_fecha1, col_fecha2 = st.columns(2)
        with col_fecha1:
            fecha_inicio = st.date_input("📅 Desde:", value=date.today())
        with col_fecha2:
            fecha_fin = st.date_input("📅 Hasta:", value=date.today())
        titulo_periodo = f"{fecha_inicio} a {fecha_fin}"
    
    # Obtener ranking
    ranking = obtener_ranking_asesores(
        fecha_inicio=fecha_inicio.isoformat(),
        fecha_fin=fecha_fin.isoformat()
    )
    
    if ranking:
        # Calcular totales generales
        total_general = sum(r[6] for r in ranking)
        total_rucs = sum(r[1] for r in ranking)
        
        # Mostrar título con período
        st.subheader(f"Período: {titulo_periodo}")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💰 Total Cobrado", f"S/. {total_general:,.2f}")
        
        with col2:
            st.metric("👥 Asesores Activos", len(ranking))
        
        with col3:
            st.metric("📦 Total RUCs", total_rucs)
        
        st.markdown("---")
        
        # Tabla de ranking
        st.subheader("🥇 Ranking Detallado")
        
        tabla_ranking = []
        for idx, (asesor, total_rucs, rucs_ga, rucs_plan, total_ga, total_plan, total_cobrado) in enumerate(ranking, 1):
            porcentaje = (total_cobrado / total_general * 100) if total_general > 0 else 0
            
            # Medalla
            if idx == 1:
                medal = "🥇"
            elif idx == 2:
                medal = "🥈"
            elif idx == 3:
                medal = "🥉"
            else:
                medal = f"#{idx}"
            
            tabla_ranking.append({
                'Posición': medal,
                'Asesor': asesor,
                'Total Cobrado': f"S/. {total_cobrado:,.2f}",
                '% del Total': f"{porcentaje:.1f}%",
                'RUCs': total_rucs,
                'GA': f"{rucs_ga} (S/. {total_ga:,.0f})",
                'Planilla': f"{rucs_plan} (S/. {total_plan:,.0f})"
            })
        
        df_ranking = pd.DataFrame(tabla_ranking)
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Gráfico comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Gráfico de Cobros por Asesor")
            chart_data = []
            for asesor, _, _, _, _, _, total_cobrado in ranking:
                chart_data.append({'Asesor': asesor.split()[0] if asesor and asesor != 'SIN ASESOR' else asesor, 'Cobrado': total_cobrado})
            
            if chart_data:
                df_chart = pd.DataFrame(chart_data)
                st.bar_chart(df_chart.set_index('Asesor'))
        
        with col2:
            st.subheader("📈 Composición: GA vs Planilla")
            chart_composicion = []
            for asesor, _, _, _, total_ga, total_plan, _ in ranking:
                chart_composicion.append({
                    'Asesor': asesor.split()[0] if asesor and asesor != 'SIN ASESOR' else asesor,
                    'GA': total_ga,
                    'Planilla': total_plan
                })
            
            if chart_composicion:
                df_comp = pd.DataFrame(chart_composicion)
                st.bar_chart(df_comp.set_index('Asesor'))
        
        st.markdown("---")
        
        # Descargar datos
        csv_ranking = df_ranking.to_csv(index=False)
        st.download_button(
            label="📥 Descargar Ranking (CSV)",
            data=csv_ranking,
            file_name=f"ranking_asesores_{fecha_inicio.isoformat()}.csv",
            mime="text/csv"
        )
    
    else:
        st.info("ℹ️ No hay datos de cobros para el período seleccionado")

# ======================== PROMESAS PENDIENTES ========================
elif opcion == "⏳ Promesas Pendientes":
    st.markdown("""
        <style>
        .promesa-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.header("⏳ Promesas Pendientes por Cobrar")
    
    # Convertir promesas vencidas a PROMESA CAIDA antes de obtener datos
    detectar_promesas_caidas()
    
    # Filtros en la barra lateral
    with st.sidebar:
        st.markdown("")
        fecha_inicio = st.date_input(
            "📅 Desde:",
            value=date.today(),
            key="promesas_inicio"
        )
        
        fecha_fin = st.date_input(
            "📅 Hasta:",
            value=date.today() + __import__('datetime').timedelta(days=30),
            key="promesas_fin"
        )
    
    promesas_pendientes = obtener_promesas_pendientes(
        fecha_inicio=fecha_inicio.isoformat(),
        fecha_fin=fecha_fin.isoformat()
    )
    
    if promesas_pendientes:
        # Los datos ya han sido actualizados por detectar_promesas_caidas() al inicio
        
        # Calcular estadísticas
        total_promesas = len(promesas_pendientes)
        
        # Agrupar por asesor
        por_asesor = {}
        for ruc, id_doc, asesor, campana, promesa_ga, promesa_planilla, fecha_pago_pendiente, fecha in promesas_pendientes:
            if asesor not in por_asesor:
                por_asesor[asesor] = 0
            por_asesor[asesor] += 1
        
        # Métricas principales con mejor visual
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "⏳ Promesas Pendientes", 
                total_promesas,
                delta=None,
                delta_color="normal"
            )
        
        with col2:
            asesores_count = len(por_asesor)
            st.metric(
                "👥 Asesores Involucrados", 
                asesores_count,
                delta=None
            )
        
        with col3:
            asesor_top = max(por_asesor.items(), key=lambda x: x[1])[0]
            asesor_top_count = por_asesor[asesor_top]
            st.metric("🏆 Mayor Cantidad", f"{asesor_top_count} RUCs")
        
        st.divider()
        
        # Tabla detallada mejorada
        st.subheader("📋 Detalle de RUCs con Promesas Pendientes")
        
        tabla_pendientes = []
        for ruc, id_doc, asesor, campana, promesa_ga, promesa_planilla, fecha_pago_pendiente, fecha in promesas_pendientes:
            promesa_tipo = ""
            if promesa_ga == "A VEN...":
                promesa_tipo = "Gastos Admin"
            elif promesa_planilla == "A VEN...":
                promesa_tipo = "Planilla"
            
            tabla_pendientes.append({
                'Asesor': asesor if asesor else 'SIN ASESOR',
                'RUC': ruc,
                'Campaña': campana,
                'Tipo Promesa': promesa_tipo.strip(),
                'Fecha Pago Programada': fecha_pago_pendiente,
                'Última Fecha': fecha
            })
        
        df_pendientes = pd.DataFrame(tabla_pendientes)
        
        # Aplicar estilos a la tabla
        st.dataframe(
            df_pendientes, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                'Asesor': st.column_config.TextColumn(width="medium"),
                'RUC': st.column_config.TextColumn(width="small"),
                'Campaña': st.column_config.TextColumn(width="small"),
                'Tipo Promesa': st.column_config.TextColumn(width="medium"),
                'Fecha Pago Programada': st.column_config.TextColumn(width="small"),
                'Última Fecha': st.column_config.TextColumn(width="small"),
            }
        )
        
        # Resumen por asesor
        st.markdown("---")
        st.subheader("📊 Resumen por Asesor")
        
        tabla_asesor = []
        for asesor, cantidad in sorted(por_asesor.items(), key=lambda x: x[1], reverse=True):
            tabla_asesor.append({
                'Asesor': asesor if asesor else 'SIN ASESOR',
                'Cantidad de Promesas': cantidad
            })
        
        df_asesor = pd.DataFrame(tabla_asesor)
        st.dataframe(df_asesor, use_container_width=True, hide_index=True)
        
        # Gráfico
        st.markdown("---")
        st.subheader("📈 Gráfico de Promesas por Asesor")
        
        chart_data = pd.DataFrame({
            'Asesor': [a if a else 'SIN ASESOR' for a in por_asesor.keys()],
            'Cantidad': por_asesor.values()
        }).sort_values('Cantidad', ascending=False)
        
        st.bar_chart(chart_data.set_index('Asesor'))
        
        # Acción: Descargar lista
        st.markdown("---")
        csv_pendientes = df_pendientes.to_csv(index=False)
        st.download_button(
            label="📥 Descargar Lista de Pendientes (CSV)",
            data=csv_pendientes,
            file_name="promesas_pendientes.csv",
            mime="text/csv"
        )
    
    else:
        st.info("ℹ️ No hay promesas pendientes en el rango de fechas seleccionado.")

# ======================== PROMESAS DE HOY ========================
elif opcion == "🎯 Promesas de Hoy":
    st.header("🎯 Pagos Prometidos para HOY")
    
    # Convertir promesas vencidas a PROMESA CAIDA antes de obtener datos
    detectar_promesas_caidas()
    
    promesas_stats = obtener_estadisticas_promesas_hoy()
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Promesas Gasto", promesas_stats['promesas_gasto_count'])
    
    with col2:
        st.metric("💰 Monto Gasto", f"S/. {promesas_stats['promesas_gasto_monto']:,.2f}")
    
    with col3:
        st.metric("📊 Promesas Planilla", promesas_stats['promesas_planilla_count'])
    
    with col4:
        st.metric("💵 Monto Planilla", f"S/. {promesas_stats['promesas_planilla_monto']:,.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Total Promesas: {promesas_stats['total_promesas']}")
    with col2:
        st.info(f"💎 Total a Cobrar: S/. {promesas_stats['total_monto_promesas']:,.2f}")
    
    st.markdown("---")
    st.subheader("📋 Detalle de Promesas")
    
    promesas = obtener_promesas_hoy()
    
    if promesas:
        # Los datos ya han sido actualizados por detectar_promesas_caidas() al inicio
        
        df_promesas = pd.DataFrame(promesas, columns=[
            'ID', 'Fecha Reporte', 'RUC', 'ID Doc', 'Campaña', 'Asesor',
            'Promesa', 'Monto', 'Fecha Pago', 'Tipo Pago', 'Observaciones'
        ])
        
        # Formatear montos
        df_promesas['Monto'] = df_promesas['Monto'].apply(lambda x: f"S/. {x:,.2f}" if pd.notna(x) and x > 0 else "-")
        
        # Colorear por tipo
        def colorear_fila(row):
            if row['Tipo Pago'] == 'GASTO':
                return ['background-color: #ffe6e6'] * len(row)
            else:
                return ['background-color: #e6f3ff'] * len(row)
        
        st.dataframe(
            df_promesas.style.apply(colorear_fila, axis=1),
            use_container_width=True,
            height=400
        )
        
        st.success(f"✓ Total de promesas: {len(promesas)}")
    else:
        st.info("ℹ️ No hay promesas de pago para hoy")

# ======================== REGISTRAR PAGO ========================
elif opcion == "📝 Registrar Pago":
    st.header("📝 Registrar Nuevo Pago")
    
    st.subheader("Información del Registro")
    
    # Fila 1: Fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_reporte = st.date_input("📅 Fecha Reporte", value=date.today())
    
    # Fila 2: Búsqueda de RUC
    col1, col2 = st.columns(2)
    with col1:
        # Si no hay RUC registrado, mostrar input activo
        if st.session_state.ruc_registrado is None:
            ruc_numero = st.text_input("🔍 Número RUC", placeholder="Ingresa RUC y presiona Enter")
            
            if ruc_numero:
                # Buscar RUC en BD
                ruc_info_list = obtener_ruc_por_numero(ruc_numero)
                
                if ruc_info_list:
                    st.session_state.ruc_registrado = ruc_numero
                    st.session_state.ruc_info_encontrada = ruc_info_list
                    st.rerun()
                else:
                    st.error("❌ RUC no encontrado en la base de datos")
        else:
            # Mostrar RUC deshabilitado
            st.text_input("🔍 Número RUC", value=st.session_state.ruc_registrado, disabled=True)
            
            if st.button("🔄 Cambiar RUC", use_container_width=False):
                st.session_state.ruc_registrado = None
                st.session_state.ruc_info_encontrada = None
                st.rerun()
    
    # Si hay RUC registrado, mostrar datos y opciones
    if st.session_state.ruc_registrado and st.session_state.ruc_info_encontrada:
        ruc_info_list = st.session_state.ruc_info_encontrada
        primer_ruc = ruc_info_list[0]
        
        # Si hay múltiples campañas, permitir seleccionar
        if len(ruc_info_list) > 1:
            st.info(f"✓ Se encontraron {len(ruc_info_list)} campañas para este RUC")
            campanas_disponibles = [ruc[4] for ruc in ruc_info_list]
            idx_campana = st.selectbox(
                "Selecciona la Campaña a registrar:",
                range(len(ruc_info_list)),
                format_func=lambda i: f"{campanas_disponibles[i]}",
                key="select_campana"
            )
            ruc_seleccionado = ruc_info_list[idx_campana]
        else:
            ruc_seleccionado = primer_ruc
        
        st.success(f"✓ RUC encontrado: {ruc_seleccionado[3]}")
        
        # Mostrar información adicional del RUC (Deuda Total y Gasto Admin)
        deuda_total = ruc_seleccionado[6]  # índice 6 = deuda_total
        gasto_admin = ruc_seleccionado[7]  # índice 7 = gasto_admin
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            if deuda_total and deuda_total > 0:
                st.metric("💰 Deuda Total", f"S/. {deuda_total:,.2f}")
            else:
                st.metric("💰 Deuda Total", "No registrada")
        
        with col_info2:
            if gasto_admin and gasto_admin > 0:
                st.metric("📊 Gasto Admin", f"S/. {gasto_admin:,.2f}")
            else:
                st.metric("📊 Gasto Admin", "No registrada")
        
        st.divider()
        asesores_disponibles = obtener_asesores_unicos()
        asesor_original = ruc_seleccionado[5] or ""
        
        # Agregar el asesor original al inicio si no está
        if asesor_original and asesor_original not in asesores_disponibles:
            asesores_lista = [asesor_original] + asesores_disponibles
        else:
            asesores_lista = asesores_disponibles
        
        # Seleccionar índice del asesor original
        idx_asesor = asesores_lista.index(asesor_original) if asesor_original in asesores_lista else 0
        
        with col2:
            asesor = st.selectbox(
                "Asesor",
                asesores_lista,
                index=idx_asesor,
                help="Selecciona el asesor para este registro. Puedes cambiar del original."
            )
        
        # Guardar valores para el registro
        id_documento = ruc_seleccionado[2]
        campaña = ruc_seleccionado[4]
        
        st.markdown("---")
        st.subheader("💵 Gasto Administrativo")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            promesa_ga = st.selectbox(
                "Promesa GA",
                ["", "A VEN...", "COBR..."],
                key="promesa_ga"
            )
        with col2:
            monto_gasto = st.number_input("Monto Gasto", min_value=0.0, value=0.0, step=0.01)
        with col3:
            fecha_pago_gasto = st.date_input("Fecha de Pago", value=None, key="fecha_gasto")
        
        st.markdown("---")
        st.subheader("📊 Planilla")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            promesa_planilla = st.selectbox(
                "Promesa Planilla",
                ["", "A VEN...", "COBR..."],
                key="promesa_plan"
            )
        with col2:
            monto_planilla = st.number_input("Monto Planilla", min_value=0.0, value=0.0, step=0.01)
        with col3:
            fecha_pago_planilla = st.date_input("Fecha de Pago", value=None, key="fecha_plan")
        
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            observaciones = st.text_area("Observaciones", height=80)
        
        st.markdown("---")
        
        # Botón de envío
        if st.button("✅ Registrar Pago", use_container_width=True):
            if monto_gasto == 0 and monto_planilla == 0:
                st.error("❌ Ingresa al menos un monto (Gasto o Planilla)")
            else:
                try:
                    promesa_ga_val = promesa_ga if promesa_ga else None
                    promesa_planilla_val = promesa_planilla if promesa_planilla else None
                    
                    monto_gasto_val = monto_gasto if monto_gasto > 0 else None
                    monto_planilla_val = monto_planilla if monto_planilla > 0 else None
                    
                    fecha_pago_gasto_str = fecha_pago_gasto.isoformat() if fecha_pago_gasto else None
                    fecha_pago_planilla_str = fecha_pago_planilla.isoformat() if fecha_pago_planilla else None
                    
                    # VALIDAR DUPLICADOS EXACTOS
                    es_duplicado, id_dup, msg_dup = detectar_duplicado_exacto(
                        fecha_reporte=fecha_reporte.isoformat(),
                        ruc=st.session_state.ruc_registrado,
                        id_documento=id_documento,
                        campaña=campaña,
                        asesor=asesor,
                        promesa_ga=promesa_ga_val,
                        monto_gasto=monto_gasto_val,
                        fecha_pago_gasto=fecha_pago_gasto_str,
                        promesa_planilla=promesa_planilla_val,
                        monto_planilla=monto_planilla_val,
                        fecha_pago_planilla=fecha_pago_planilla_str,
                        observaciones=observaciones
                    )
                    
                    if es_duplicado:
                        st.warning(f"⚠️ **ALERTA DE DUPLICADO**\n\n{msg_dup}\n\n"
                                  f"Los datos del registro que intentas crear ya existen en la BD.\n\n"
                                  f"📅 Fecha: {fecha_reporte}\n"
                                  f"🔢 RUC: {st.session_state.ruc_registrado}\n"
                                  f"👤 Asesor: {asesor}")
                    else:
                        registro_id = registrar_pago(
                            fecha_reporte=fecha_reporte.isoformat(),
                            ruc=st.session_state.ruc_registrado,
                            id_documento=id_documento,
                            campaña=campaña,
                            asesor=asesor,
                            promesa_ga=promesa_ga_val,
                            monto_gasto=monto_gasto_val,
                            fecha_pago_gasto=fecha_pago_gasto_str,
                            promesa_planilla=promesa_planilla_val,
                            monto_planilla=monto_planilla_val,
                            fecha_pago_planilla=fecha_pago_planilla_str,
                            observaciones=observaciones
                        )
                        
                        st.success(f"✅ ¡Pago registrado exitosamente!")
                        st.balloons()
                        
                        # Mostrar resumen
                        st.markdown("---")
                        st.subheader("📋 Resumen del Registro")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("ID Registro", registro_id)
                        with col2:
                            st.metric("Total Cobrado", f"S/. {(monto_gasto_val or 0) + (monto_planilla_val or 0):,.2f}")
                        with col3:
                            st.metric("RUC", st.session_state.ruc_registrado)
                        
                        st.info(f"👤 Asesor: {asesor} | 📊 Campaña: {campaña}")
                        
                        # Esperar 2 segundos y redirigir al dashboard
                        st.info("⏳ Redirigiendo al Dashboard en 2 segundos...")
                        import time
                        time.sleep(2)
                        st.session_state.pagina_actual = "📊 Dashboard"
                        st.rerun()
                        
                        # Limpiar formulario para nuevo registro
                        import time
                        time.sleep(2)  # Mostrar el resumen por 2 segundos
                        st.session_state.ruc_registrado = None
                        st.session_state.ruc_info_encontrada = None
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error al registrar: {str(e)}")

# ======================== VER REGISTROS ========================
elif opcion == "📋 Ver Registros":
    st.header("📋 Ver Registros de Pagos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_tipo = st.radio("Mostrar registros:", ["Hoy", "Por Fecha", "Todos"])
    
    registros = None
    
    if filtro_tipo == "Hoy":
        registros = obtener_registros_hoy()
        st.subheader(f"Registros de {date.today().isoformat()}")
    
    elif filtro_tipo == "Por Fecha":
        fecha_seleccionada = st.date_input("Selecciona una fecha")
        registros = obtener_registros_por_fecha(fecha_seleccionada.isoformat())
        st.subheader(f"Registros de {fecha_seleccionada.isoformat()}")
    
    else:
        registros = obtener_todos_registros()
        st.subheader("Todos los registros")
    
    if registros:
        # Los datos ya han sido actualizados por detectar_promesas_caidas() al inicio
        
        # Crear DataFrame
        df = pd.DataFrame(registros, columns=[
            'ID', 'Fecha Reporte', 'RUC', 'ID Doc', 'Campaña', 'Asesor',
            'Promesa Gastos Admin', 'Monto Gastos Admin', 'Fecha Pago Gastos Admin', 'Estado Gastos Admin',
            'Promesa Planilla', 'Monto Planilla', 'Fecha Pago Planilla', 'Estado Planilla',
            'Observaciones'
        ])
        
        # Formatear montos
        for col in ['Monto Gastos Admin', 'Monto Planilla']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"S/. {x:,.2f}" if pd.notna(x) and x > 0 else "-")
        
        # Mostrar estadísticas primero
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Registros", len(registros))
        
        with col2:
            st.metric("IDs de Registros", f"{', '.join(map(str, [r[0] for r in registros][:5]))}...")
        
        with col3:
            st.metric("Registros Mostrados", f"{len(df)}")
        
        st.divider()
        
        # Mostrar dataframe sin límite de altura para ver todos los registros
        st.dataframe(df, use_container_width=True)
        
        # Tabs para Editar y Eliminar
        tab_editar, tab_eliminar = st.tabs(["✏️ Editar Registro", "🗑️ Eliminar Registro"])
        
        # ========== TAB EDITAR ==========
        with tab_editar:
            st.subheader("✏️ Editar Registro")
            
            # Inicializar session state para contraseña de edición
            if 'contraseña_editar_correcta' not in st.session_state:
                st.session_state.contraseña_editar_correcta = False
            
            # Solicitar contraseña
            if not st.session_state.contraseña_editar_correcta:
                col_pass1, col_pass2 = st.columns([3, 1])
                
                with col_pass1:
                    contraseña_edit = st.text_input(
                        "🔐 Ingresa la contraseña para editar registros:",
                        type="password",
                        placeholder="Contraseña requerida",
                        key="pass_editar"
                    )
                
                with col_pass2:
                    st.markdown("")
                    st.markdown("")
                    if st.button("✅ Verificar", use_container_width=True, key="btn_verify_edit"):
                        if contraseña_edit == "calidad":
                            st.session_state.contraseña_editar_correcta = True
                            st.success("✓ Contraseña correcta")
                            st.rerun()
                        else:
                            st.error("❌ Contraseña incorrecta")
            
            # Si contraseña es correcta, mostrar opciones de edición
            if st.session_state.contraseña_editar_correcta:
                st.success("🔓 Acceso desbloqueado")
                st.info("ℹ️ Realiza los cambios necesarios en los campos:")
                
                # Seleccionar registro a editar
                id_editar = st.selectbox(
                    "Selecciona el ID del registro a editar:",
                    options=[r[0] for r in registros],
                    help="Elige el ID que deseas modificar",
                    key="select_id_edit"
                )
                
                # Obtener datos del registro seleccionado
                registro_actual = next((r for r in registros if r[0] == id_editar), None)
                
                if registro_actual:
                    st.info(f"📋 Editando registro ID: {id_editar}")
                    
                    # Crear formulario de edición
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        promesa_ga_edit = st.text_input(
                            "Promesa GA:",
                            value=registro_actual[6] or "",
                            help="Ej: A VENCER, COBRADO, etc.",
                            key="promesa_ga_edit"
                        )
                        
                        monto_gasto_edit = st.number_input(
                            "Monto Gasto Admin:",
                            value=float(registro_actual[7]) if registro_actual[7] else 0.0,
                            step=0.01,
                            key="monto_gasto_edit"
                        )
                        
                        fecha_pago_gasto_edit = st.date_input(
                            "Fecha Pago Gasto:",
                            value=datetime.strptime(registro_actual[8], '%Y-%m-%d').date() if registro_actual[8] else date.today(),
                            format="YYYY-MM-DD",
                            key="fecha_gasto_edit"
                        )
                    
                    with col2:
                        promesa_planilla_edit = st.text_input(
                            "Promesa Planilla:",
                            value=registro_actual[9] or "",
                            help="Ej: A VENCER, COBRADO, etc.",
                            key="promesa_planilla_edit"
                        )
                        
                        monto_planilla_edit = st.number_input(
                            "Monto Planilla:",
                            value=float(registro_actual[10]) if registro_actual[10] else 0.0,
                            step=0.01,
                            key="monto_planilla_edit"
                        )
                        
                        fecha_pago_planilla_edit = st.date_input(
                            "Fecha Pago Planilla:",
                            value=datetime.strptime(registro_actual[11], '%Y-%m-%d').date() if registro_actual[11] else date.today(),
                            format="YYYY-MM-DD",
                            key="fecha_planilla_edit"
                        )
                    
                    observaciones_edit = st.text_area(
                        "Observaciones:",
                        value=registro_actual[12] or "",
                        height=80,
                        key="obs_edit"
                    )
                    
                    # Botones de acción para editar
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        if st.button("✅ Guardar Cambios", use_container_width=True, type="primary", key="btn_save_edit"):
                            try:
                                # Actualizar registro
                                conn = sqlite3.connect("pagos.db")
                                cursor = conn.cursor()
                                
                                cursor.execute('''
                                UPDATE registros_pagos 
                                SET promesa_ga = ?, monto_gasto = ?, fecha_pago_gasto = ?,
                                    promesa_planilla = ?, monto_planilla = ?, fecha_pago_planilla = ?,
                                    observaciones = ?
                                WHERE id = ?
                                ''', (
                                    promesa_ga_edit if promesa_ga_edit else None,
                                    monto_gasto_edit if monto_gasto_edit > 0 else None,
                                    fecha_pago_gasto_edit.strftime('%Y-%m-%d') if promesa_ga_edit else None,
                                    promesa_planilla_edit if promesa_planilla_edit else None,
                                    monto_planilla_edit if monto_planilla_edit > 0 else None,
                                    fecha_pago_planilla_edit.strftime('%Y-%m-%d') if promesa_planilla_edit else None,
                                    observaciones_edit,
                                    id_editar
                                ))
                                
                                conn.commit()
                                conn.close()
                                
                                st.success(f"✓ Registro ID {id_editar} actualizado correctamente")
                                st.session_state.contraseña_editar_correcta = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al actualizar: {e}")
                    
                    with col_btn2:
                        if st.button("❌ Cancelar", use_container_width=True, key="btn_cancel_edit"):
                            st.session_state.contraseña_editar_correcta = False
                            st.rerun()
                    
                    with col_btn3:
                        st.markdown("")
                        st.markdown("")
                        if st.button("Cerrar", use_container_width=True, key="btn_close_edit"):
                            st.session_state.contraseña_editar_correcta = False
                            st.rerun()
        
        # ========== TAB ELIMINAR ==========
        with tab_eliminar:
            st.subheader("🗑️ Eliminar Registro")
            
            # Inicializar session state para contraseña
            if 'contraseña_correcta' not in st.session_state:
                st.session_state.contraseña_correcta = False
            
            # Solicitar contraseña
            if not st.session_state.contraseña_correcta:
                col_pass1, col_pass2 = st.columns([3, 1])
                
                with col_pass1:
                    contraseña = st.text_input(
                        "🔐 Ingresa la contraseña para eliminar registros:",
                        type="password",
                        placeholder="Contraseña requerida"
                    )
                
                with col_pass2:
                    st.markdown("")
                    st.markdown("")
                    if st.button("✅ Verificar", use_container_width=True):
                        if contraseña == "calidad":
                            st.session_state.contraseña_correcta = True
                            st.success("✓ Contraseña correcta")
                            st.rerun()
                        else:
                            st.error("❌ Contraseña incorrecta")
            
            # Si contraseña es correcta, mostrar opciones de eliminación
            if st.session_state.contraseña_correcta:
                st.success("🔓 Acceso desbloqueado")
                st.warning("⚠️ Estás en modo de eliminación. Sé cuidadoso.")
                
                col_elim1, col_elim2, col_elim3 = st.columns([2, 1, 1])
                
                with col_elim1:
                    id_registro = st.number_input(
                        "Ingresa el ID del registro a eliminar:",
                        min_value=1,
                        value=None,
                        help="Puedes ver el ID en la primera columna de la tabla"
                    )
                
                with col_elim2:
                    st.markdown("")
                    st.markdown("")
                    if st.button("🗑️ Eliminar", use_container_width=True, type="secondary"):
                        if id_registro:
                            try:
                                eliminar_registro(int(id_registro))
                                st.success(f"✓ Registro ID {id_registro} eliminado correctamente")
                                st.session_state.contraseña_correcta = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al eliminar: {e}")
                        else:
                            st.warning("⚠️ Por favor ingresa un ID válido")
                
                with col_elim3:
                    st.markdown("")
                    st.markdown("")
                    if st.button("Cerrar", use_container_width=True):
                        st.session_state.contraseña_correcta = False
                        st.rerun()
    else:
        st.info("ℹ️ No hay registros en la fecha seleccionada")

# ======================== EXPORTAR DATOS ========================
elif opcion == "📂 Exportar Datos":
    st.header("📂 Exportar Datos")
    
    st.subheader("Descargar registros en formato CSV")
    
    if st.button("⬇️ Descargar Todos los Registros", use_container_width=True):
        try:
            archivo = exportar_a_csv()
            with open(archivo, 'rb') as f:
                st.download_button(
                    label="📥 Descargar CSV",
                    data=f.read(),
                    file_name=archivo,
                    mime="text/csv"
                )
            st.success(f"✓ Archivo generado: {archivo}")
        except Exception as e:
            st.error(f"❌ Error al exportar: {e}")
    
    st.markdown("---")
    st.info("""
    Los registros se exportarán en formato CSV con todas las columnas:
    - Fecha Reporte
    - RUC, ID Documento, Campaña, Asesor
    - Promesa GA, Monto Gasto, Fecha de Pago (GA)
    - Promesa Planilla, Monto Planilla, Fecha de Pago (Planilla)
    - Observaciones
    """)
