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
    obtener_resumen_total_por_promesa
)

# Configuración
st.set_page_config(
    page_title="📊 Registro de Pagos Diarios",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar BD
init_db()

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

# Título principal
st.title("💰 Sistema de Registro de Pagos Diarios")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Menú")
    
    # Mostrar estado de la BD
    registros_total = len(obtener_todos_registros())
    st.metric("📊 Registros Guardados", registros_total, delta="Guardados en BD")
    st.info(f"✓ Los datos se guardan permanentemente en `pagos.db`")
    
    st.divider()
    
    opcion = st.radio(
        "Selecciona una opción:",
        [
            "📊 Dashboard",
            "🎯 Promesas de Hoy",
            "📝 Registrar Pago",
            "📋 Ver Registros",
            "📂 Exportar Datos"
        ]
    )

# ======================== DASHBOARD ========================
if opcion == "📊 Dashboard":
    st.header("📊 Dashboard de Pagos")
    
    # Filtro de fecha en la barra lateral
    with st.sidebar:
        st.markdown("### 📅 Filtros")
        fecha_filtro = st.date_input(
            "Selecciona fecha:",
            value=date.today(),
            key="fecha_dashboard"
        )
    
    # Obtener datos con la fecha seleccionada
    resumen_gasto = obtener_resumen_total_por_promesa(tipo_pago='gasto', fecha=fecha_filtro)
    resumen_planilla = obtener_resumen_total_por_promesa(tipo_pago='planilla', fecha=fecha_filtro)
    resumen_asesor_gasto = obtener_resumen_por_asesor_promesa(tipo_pago='gasto', fecha=fecha_filtro)
    resumen_asesor_planilla = obtener_resumen_por_asesor_promesa(tipo_pago='planilla', fecha=fecha_filtro)
    
    # Calcular totales
    total_gasto = sum(r[2] for r in resumen_gasto) if resumen_gasto else 0
    total_rucs_gasto = sum(r[1] for r in resumen_gasto) if resumen_gasto else 0
    total_planilla = sum(r[2] for r in resumen_planilla) if resumen_planilla else 0
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
            cobrado_gasto = [r for r in resumen_gasto if r[0] == 'COBR...']
            
            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                if a_vencer_gasto:
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
                    tabla_gasto.append({
                        'Asesor': asesor.split()[0] if asesor else 'N/A',  # Nombre corto
                        'Estado': '⏳' if promesa == 'A VEN...' else '✅',
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
            cobrado_plan = [r for r in resumen_planilla if r[0] == 'COBR...']
            
            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                if a_vencer_plan:
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
                    tabla_planilla.append({
                        'Asesor': asesor.split()[0] if asesor else 'N/A',  # Nombre corto
                        'Estado': '⏳' if promesa == 'A VEN...' else '✅',
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
        st.metric("👥 Total RUCs", total_rucs_gasto + total_rucs_planilla)
    
    with resumen_col4:
        registros_fecha = obtener_registros_por_fecha(fecha_filtro)
        st.metric("📝 Registros", len(registros_fecha))

# ======================== PROMESAS DE HOY ========================
elif opcion == "🎯 Promesas de Hoy":
    st.header("🎯 Pagos Prometidos para HOY")
    
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
        
        # Opciones de Asesor
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
        # Crear DataFrame
        df = pd.DataFrame(registros, columns=[
            'ID', 'Fecha Reporte', 'RUC', 'ID Doc', 'Campaña', 'Asesor',
            'Promesa GA', 'Monto Gasto', 'Fecha Pago Gasto',
            'Promesa Planilla', 'Monto Planilla', 'Fecha Pago Planilla',
            'Observaciones'
        ])
        
        # Formatear montos
        for col in ['Monto Gasto', 'Monto Planilla']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"S/. {x:,.2f}" if pd.notna(x) and x > 0 else "-")
        
        st.dataframe(df, use_container_width=True, height=400)
        
        # Botones de acción
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Registros", len(registros))
        
        with col2:
            st.metric("IDs de Registros", f"{', '.join(map(str, [r[0] for r in registros]))}")
        
        st.divider()
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
