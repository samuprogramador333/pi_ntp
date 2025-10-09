import streamlit as st
import pandas as pd

from pages.app1 import mostrar_horarios
from pages.app2 import mostrar_RegistroEducativos
from pages.app4_ExploracionDatos import mostrar_exploracion_datos
from pages.app5_ExploracionDatos import mostrar_exploracion_datos_educativos

st.set_page_config(
    page_title="Panel Principal - Sistema de Gestión", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header principal
st.title("🏢 Inicio de Apps")
st.subheader("Panel de control unificado para análisis de datos y gestión empresarial")

# Sidebar con información del sistema
st.sidebar.header("📊 Navegación del Sistema")
st.sidebar.divider()

opcion = st.sidebar.selectbox(
    "🎯 Selecciona una aplicación:",
    (
        "🏠 Inicio",
        "⏰ Registro de Horarios",
        "🎓 Centros Educativos",
        "📈 Exploración de Datos",
        "🏫 Exploración Centros Educativos"
    )
)

# Información adicional en sidebar
st.sidebar.divider()
st.sidebar.subheader("📋 Información del Sistema")
st.sidebar.info("🔄 **Estado**: Operativo\n📅 **Última actualización**: Hoy\n👥 **Módulos activos**: 4")

if opcion == "🏠 Inicio":
    # Header principal con diseño mejorado
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        # 👋 Bienvenido al Sistema de Análisis Integral
        ### Panel de control unificado para análisis de datos y gestión empresarial
        """)
        
        st.markdown("""
        **Un ecosistema completo** de herramientas especializadas diseñadas para optimizar 
        los procesos organizacionales, facilitar la toma de decisiones basada en datos 
        y proporcionar insights valiosos para tu organización.
        """)
    
    with col2:
        st.info("""
        🎯 **4 Módulos Especializados**  
        📊 **Análisis Avanzado**  
        🔍 **Filtros Inteligentes**  
        📈 **Visualizaciones Dinámicas**
        """)
    
    st.divider()
    
    # Overview de las aplicaciones con métricas
    st.header("📊 Resumen de Módulos Disponibles")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⏰ Horarios", 
            value="API + Filtros",
            delta="Tiempo Real"
        )
    
    with col2:
        st.metric(
            label="🎓 Educativos", 
            value="CSV Análisis",
            delta="Multi-filtro"
        )
    
    with col3:
        st.metric(
            label="📈 Exploración", 
            value="8 Secciones",
            delta="Análisis Completo"
        )
    
    with col4:
        st.metric(
            label="🏫 Centros", 
            value="7 Análisis",
            delta="Geo-espacial"
        )
    
    st.divider()
    
    # Descripción detallada de cada aplicación con tabs
    st.header("🎯 Módulos del Sistema")
    
    tab1, tab2, tab3, tab4 = st.tabs(["⏰ Registro de Horarios", "🎓 Centros Educativos", "📈 Exploración de Datos", "🏫 Exploración Centros"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### ⏰ Aplicación 1: Registro de Horarios
            
            **Sistema completo de gestión temporal** que integra datos en tiempo real desde una API externa 
            para proporcionar un control exhaustivo de horarios laborales con capacidades de análisis avanzado.
            
            **🔗 Fuente de datos:** API MockAPI en tiempo real  
            **📊 Tipo de análisis:** Temporal, estadístico y comparativo  
            **🎯 Objetivo:** Optimización de recursos humanos y productividad
            """)
            
        with col2:
            st.success("✅ **Estado:** Conectado a API")
            st.info("🔄 **Actualización:** Tiempo real")
            st.warning("📈 **Análisis:** 6 tipos de gráficos")
        
        st.markdown("""
        **🛠️ Funcionalidades Principales:**
        
        | Característica | Descripción |
        |---------------|-------------|
        | 🔍 **Filtros Inteligentes** | Filtrado por persona, área, rol, fechas y horarios |
        | 📊 **Cálculos Automáticos** | Horas trabajadas, promedios por persona y área |
        | 📈 **Visualizaciones** | Gráficos de barras, histogramas de distribución horaria |
        | 🏆 **Rankings** | Persona con más horas trabajadas (filtro especial) |
        | 📅 **Análisis Temporal** | Top 5 días con más registros, análisis por fecha |
        | 🎨 **Interfaz Moderna** | Dashboard interactivo con métricas en tiempo real |
        """)
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🎓 Aplicación 2: Centros Educativos
            
            **Sistema de gestión educativa** especializado en el análisis de infraestructura 
            y distribución geográfica de instituciones educativas con herramientas de filtrado múltiple.
            
            **📁 Fuente de datos:** WL_T_Centros_Educativos.csv  
            **🗺️ Tipo de análisis:** Geográfico, infraestructura y categórico  
            **🎯 Objetivo:** Evaluación y planificación educativa regional
            """)
            
        with col2:
            st.success("✅ **Estado:** Datos cargados")
            st.info("📊 **Registros:** Análisis completo")
            st.warning("🎯 **Focus:** Infraestructura")
        
        st.markdown("""
        **🛠️ Funcionalidades Principales:**
        
        | Característica | Descripción |
        |---------------|-------------|
        | 🌍 **Filtros Geográficos** | Por municipio, categoría y estado de infraestructura |
        | 📊 **Visualizaciones** | Gráficos por municipio y estado de infraestructura |
        | 📈 **Métricas Clave** | Total de registros filtrados en tiempo real |
        | 🏛️ **Análisis Municipal** | Distribución de centros por municipio |
        | 🏗️ **Estado Infraestructura** | Evaluación del estado de las instalaciones |
        | 📋 **Vista de Datos** | Tabla interactiva con primeros 50 registros |
        """)
    
    with tab3:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 📈 Aplicación 3: Exploración de Datos (Horarios)
            
            **Herramienta avanzada de análisis exploratorio** especializada en registros horarios 
            que permite investigar patrones, tendencias y realizar análisis estadísticos profundos.
            
            **📁 Fuente de datos:** registros_horarios_reales.csv  
            **🔬 Tipo de análisis:** Exploratorio, estadístico y temporal  
            **🎯 Objetivo:** Descubrimiento de patrones y insights empresariales
            """)
            
        with col2:
            st.success("✅ **Módulos:** 8 secciones")
            st.info("📊 **Análisis:** Completo")
            st.warning("🔬 **Nivel:** Avanzado")
        
        st.markdown("""
        **🛠️ Módulos de Análisis (8 Secciones):**
        
        | Módulo | Descripción |
        |--------|-------------|
        | 📋 **Resumen General** | Métricas principales, vista previa e información del dataset |
        | 🔍 **Análisis Columnas** | Análisis detallado por columna con estadísticas específicas |
        | 📈 **Estadísticas Descriptivas** | Análisis completo de variables numéricas y categóricas |
        | 🎨 **Visualizaciones** | 4 tipos de gráficos especializados (área, rol, mes, horas) |
        | 🔄 **Valores Únicos** | Análisis de unicidad y frecuencias por columna |
        | 📊 **Análisis Temporal** | Tendencias, patrones por día de semana y mes |
        | 👥 **Análisis Área/Rol** | Estadísticas cruzadas entre áreas y roles |
        | 🕐 **Análisis Horarios** | Patrones de entrada/salida, rankings de horas trabajadas |
        """)
    
    with tab4:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🏫 Aplicación 4: Exploración Centros Educativos
            
            **Módulo especializado** en análisis exploratorio avanzado de centros educativos 
            con capacidades geográficas, de infraestructura y análisis de concentración.
            
            **📁 Fuente de datos:** WL_T_Centros_Educativos.csv  
            **🗺️ Tipo de análisis:** Geo-espacial, infraestructura y distribuciones  
            **🎯 Objetivo:** Planificación educativa estratégica y análisis territorial
            """)
            
        with col2:
            st.success("✅ **Módulos:** 7 secciones")
            st.info("�️ **Mapas:** Integrados")
            st.warning("📊 **HHI:** Análisis concentración")
        
        st.markdown("""
        **🛠️ Módulos de Análisis (7 Secciones):**
        
        | Módulo | Descripción |
        |--------|-------------|
        | 📋 **Resumen General** | Métricas clave, vista previa e información de columnas |
        | 🔍 **Análisis Columnas** | Análisis detallado con histogramas y estadísticas |
        | 📈 **Estadísticas Descriptivas** | Distribuciones por municipio, categoría e infraestructura |
        | 🎨 **Visualizaciones** | Gráficos zona vs categoría, provincia y establecimientos |
        | 🌍 **Análisis Geográfico** | Mapas interactivos, filtros geográficos, urbano vs rural |
        | 🏗️ **Análisis Infraestructura** | Estados (Déficit/Alerta/Cumple) por municipio y categoría |
        | 📊 **Distribuciones** | Análisis de concentración con índice Herfindahl-Hirschman |
        """)
    
    st.divider()
    
    # Guía de uso mejorada
    st.header("🚀 Guía de Uso del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 Primeros Pasos
        
        1. **Selecciona** un módulo del menú lateral
        2. **Explora** las funcionalidades disponibles  
        3. **Utiliza** los filtros para personalizar vistas
        4. **Analiza** los resultados y visualizaciones
        5. **Interpreta** las métricas y estadísticas
        """)
    
    with col2:
        st.markdown("""
        ### 💡 Tips Avanzados
        
        - 🔍 Combina múltiples filtros para análisis específicos
        - 📊 Revisa las estadísticas descriptivas primero
        - 📈 Usa las visualizaciones para identificar patrones
        - 🕐 Analiza tendencias temporales regularmente  
        - 📋 Exporta datos cuando sea necesario
        """)
    
    with col3:
        st.markdown("""
        ### ⚡ Navegación Rápida
        
        - 🏠 **Inicio:** Panel principal con resumen
        - ⏰ **Horarios:** Análisis temporal en vivo
        - 🎓 **Educativos:** Gestión de infraestructura
        - 📈 **Exploración:** Análisis estadístico profundo
        - 🏫 **Centros:** Análisis geográfico avanzado
        """)
    
    st.divider()
    
    # Footer con información adicional
    st.markdown("""
    ---
    **💻 Sistema de Análisis Integral** | Desarrollado con Streamlit | 
    **📊 Fuentes de datos:** API MockAPI + Archivos CSV | 
    **🔄 Última actualización:** Octubre 2025
    """)
    
    # Sección de desarrolladores
    st.divider()
    st.subheader("👨‍💻 Equipo de Desarrollo")
    
    # Mostrar los nombres en columnas para mejor presentación
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        ### 🧑‍💼 Samuel Bernal
        **Desarrollador Principal**
        """)
    
    with col2:
        st.markdown("""
        ### 👨‍💻 Harrison Rengifo
        **Analista de Datos**
        """)
    
    with col3:
        st.markdown("""
        ### 🎯 Cristian Sierra
        **Especialista Backend**
        """)
    
    with col4:
        st.markdown("""
        ### 📊 Sebastian Garcia
        **Desarrollador Frontend**
        """)
    
    # Footer adicional con los nombres
    st.markdown("""
    ---
    <div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
        <b>Desarrollado por:</b> Samuel Bernal • Harrison Rengifo • Cristian Sierra • Sebastian Garcia<br>
        <i>Sistema de Gestión y Análisis de Datos - 2025</i>
    </div>
    """, unsafe_allow_html=True)

elif opcion == "⏰ Registro de Horarios":
    mostrar_horarios()
elif opcion == "🎓 Centros Educativos":
    mostrar_RegistroEducativos()
elif opcion == "📈 Exploración de Datos":
    mostrar_exploracion_datos()
elif opcion == "🏫 Exploración Centros Educativos":
    mostrar_exploracion_datos_educativos()

