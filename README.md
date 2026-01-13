# 💰 Sistema de Registro de Pagos Diarios

Sistema web para registrar y gestionar pagos diarios, con seguimiento de promesas y dashboard analítico.

## 📋 Características

- ✅ **Registro de Pagos** - Ingresa pagos con RUC, asesor, monto y fecha de promesa
- 📊 **Dashboard** - Visualiza resumen de gastos administrativos y planillas por día
- 🎯 **Promesas de Pago** - Seguimiento de pagos prometidos para el día actual
- 👥 **Gestión de Asesores** - Asigna y modifica asesores en registros
- 📈 **Historial** - Consulta todos los registros con filtros por fecha
- 📂 **Exportar** - Descarga datos en CSV
- 📱 **Interfaz Web** - Acceso desde navegador usando Streamlit

## 🛠️ Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repo-url>
cd "REGISTRO DE PAGOS"
```

### 2. Crear entorno virtual (Opcional pero recomendado)
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Iniciar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8503`

### Primeros pasos
1. Ve a la página **"📝 Registrar Pago"**
2. Ingresa un RUC (ej: 10040852943)
3. Selecciona campaña, asesor y montos
4. Establece las fechas de promesa
5. Haz clic en "Registrar Pago"

## 📊 Páginas Disponibles

| Página | Descripción |
|--------|-------------|
| **📊 Dashboard** | Resumen diario con filtro de fechas |
| **🎯 Promesas** | Pagos prometidos para hoy (solo A VENCER) |
| **📝 Registrar** | Formulario para registrar nuevos pagos |
| **📋 Ver Registros** | Historial completo de registros |
| **📂 Exportar** | Descarga datos en CSV |

## 🗄️ Base de Datos

- **Tipo**: SQLite (archivo local `pagos.db`)
- **Tablas**:
  - `rucs` - Base de datos de RUCs (7,060 registros)
  - `registros_pagos` - Registro de pagos diarios

**Nota**: El archivo `pagos.db` está ignorado en Git (`.gitignore`) para preservar tus datos localmente.

## 📁 Estructura del Proyecto

```
REGISTRO DE PAGOS/
├── app.py                 # Aplicación Streamlit principal
├── database.py            # Funciones de base de datos
├── requirements.txt       # Dependencias
├── .gitignore            # Archivos ignorados en Git
├── README.md             # Este archivo
├── clean_db.py           # Script para inicializar BD
├── import_excel.py       # Script para importar RUCs desde Excel
└── pagos.db              # Base de datos (NO se sube a Git)
```

## 🔐 Seguridad

- Los datos se guardan localmente en `pagos.db`
- No se pierden datos al cerrar la aplicación
- Cada máquina tiene su propia copia de datos
- Cambios en el código no afectan los datos existentes

## 🐛 Troubleshooting

### El puerto 8503 está en uso
```bash
streamlit run app.py --server.port 8504
```

### Errores de SQL
Reinicia desde cero:
```bash
python clean_db.py
python import_excel.py
```

### Datos desaparecidos
Los datos nunca se eliminan automáticamente. Si ejecutaste `clean_db.py` por error, restaura desde un backup de `pagos.db`.

## 📞 Soporte

Para reportar problemas o sugerencias, crea un issue en el repositorio.

---

**Versión**: 1.0  
**Última actualización**: 13 de enero de 2026
  - **PROMESA**: Pago prometido para una fecha futura
- Fecha de vencimiento para promesas
- Campo de observaciones opcional

### 4. **Ver Registros (📋)**
- Filtrar por tipo de pago (Planillas o Gastos)
- Filtrar por RUC
- Vista completa de todos los registros
- Fechas y montos formateados

### 5. **Gestionar Pagos (🔍)**
- Cambiar estado de pagos existentes
- Filtrar por estado (COBRADO, PROMESA, PROMESA CAIDA)
- Marcar promesas como pagadas
- Marcar promesas como caídas
- **Validación automática**: Las promesas vencidas se convierten en "PROMESA CAIDA"

### 6. **Exportar Datos (💾)**
- Generar archivo CSV con resumen consolidado
- Ubicación: `C:\Users\USUARIO\Desktop\REGISTRO DE PAGOS\DATA ENERO 2026.csv`
- Información por RUC:
  - Planillas cobradas vs prometidas vs caídas
  - Gastos cobrados vs prometidos vs caídos
  - Total a pagar vs total pagado
  - Diferencias por RUC

---

## 📁 Archivos del Proyecto

```
REGISTRO DE PAGOS/
├── app.py                      # Aplicación principal Streamlit
├── database.py                 # Funciones de base de datos
├── utils.py                    # Funciones auxiliares
├── export_data.py              # Script para exportar datos
├── import_csv.py               # Script para importar CSV
├── pagos.db                    # Base de datos SQLite (se crea automáticamente)
├── DATA ENERO 2026.csv         # Archivo de exportación
├── requirements.txt            # Dependencias
└── README.md                   # Esta documentación
```

---

## 🔧 Instalación

### Requisitos
- Python 3.8 o superior
- Windows/Linux/Mac

### Pasos

1. **Navega a la carpeta del proyecto**
```bash
cd "C:\Users\USUARIO\Desktop\REGISTRO DE PAGOS"
```

2. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecuta la aplicación**
```bash
python -m streamlit run app.py
```

4. **Abre en tu navegador**
```
http://localhost:8501
```

---

## 📊 Funciones por Archivo

### **database.py**
Gestiona toda la interacción con la base de datos SQLite:

- `init_db()` - Inicializa las tablas
- `agregar_ruc(ruc, nombre)` - Registra nuevo RUC
- `obtener_rucs()` - Obtiene lista de RUCs
- `registrar_pago_planilla()` - Registra pago de planilla
- `registrar_gasto_administrativo()` - Registra gasto administrativo
- `obtener_pagos_planilla()` - Obtiene pagos de planillas
- `obtener_gastos_administrativos()` - Obtiene gastos
- `actualizar_estado_pago()` - Cambia estado de pago
- `obtener_estadisticas_hoy()` - Estadísticas del día actual
- `obtener_resumen_por_ruc()` - Resumen consolidado por RUC
- `exportar_a_csv()` - Exporta a archivo CSV

### **utils.py**
Funciones de formato y utilidades:

- `formatear_fecha()` - Formatea fechas ISO a formato legible
- `formatear_moneda()` - Formatea montos como moneda
- `crear_dataframe_pagos()` - Crea DataFrames para mostrar
- `verificar_promesas_vencidas()` - Valida promesas vencidas

### **app.py**
Interfaz de Streamlit con 6 secciones principales

---

## 💾 Estructura de Datos

### Tabla: **rucs**
```
id (int) - ID único
ruc (text) - Número de RUC
nombre (text) - Nombre de la empresa
fecha_creacion (text) - Fecha de creación
```

### Tabla: **pagos_planilla**
```
id (int) - ID único
ruc_id (int) - Referencia al RUC
ruc (text) - Número de RUC
monto (real) - Monto del pago
fecha_registro (text) - Fecha de registro
fecha_pago (text) - Fecha cuando se pagó (NULL si PROMESA)
estado (text) - COBRADO, PROMESA, PROMESA CAIDA
fecha_promesa (text) - Fecha prometida de pago
observaciones (text) - Notas adicionales
```

### Tabla: **gastos_administrativos**
Misma estructura que `pagos_planilla`

---

## 📝 Guía de Uso

### Flujo Típico:

1. **Registrar RUC**
   - Ir a "➕ Registrar RUC"
   - Ingresar RUC y nombre de empresa
   - Click en "Registrar RUC"

2. **Registrar Pagos**
   - Ir a "📝 Registrar Pagos"
   - Seleccionar RUC
   - Seleccionar tipo (Planilla o Gasto)
   - Ingresar monto
   - Seleccionar estado (COBRADO o PROMESA)
   - Si es PROMESA, seleccionar fecha de vencimiento
   - Click en "Registrar Pago"

3. **Ver Estado**
   - Ir a "📊 Dashboard" para ver resumen del día
   - Ir a "📋 Ver Registros" para ver todos los pagos

4. **Actualizar Estados**
   - Ir a "🔍 Gestionar Pagos"
   - Filtrar por estado según sea necesario
   - Cambiar estado y hacer click en "Actualizar"

5. **Exportar Datos**
   - Ir a "💾 Exportar Datos"
   - Click en "📥 Descargar CSV"
   - El archivo se genera en `DATA ENERO 2026.csv`

---

## 🔄 Importar CSV Existente

Si tienes un CSV con datos de RUCs (como el original `DATA ENERO 2026.csv`), puedes importarlos:

```bash
python import_csv.py
```

Esto lee el archivo CSV y agrega los RUCs a la base de datos.

---

## 📊 Exportar Datos

Para exportar datos desde terminal:

```bash
python export_data.py
```

Esto genera un CSV con resumen consolidado de:
- RUC y nombre de empresa
- Desglose de planillas y gastos
- Montos pagados vs adeudados
- Promesas pendientes y caídas

---

## 🐛 Solución de Problemas

### "Streamlit no reconocido"
Usar: `python -m streamlit run app.py`

### "No hay datos para exportar"
Primero registra RUCs y pagos en la aplicación

### "Error de base de datos"
Elimina `pagos.db` y reinicia la aplicación para crear una nueva base de datos

---

## 📞 Contacto

Sistema desarrollado para gestión integral de pagos de planillas y gastos administrativos.

---

## 📅 Fecha de Creación
13 de enero de 2026

---

**¡El sistema está listo para usar!** 🎉
