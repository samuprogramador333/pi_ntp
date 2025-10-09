## Aplicación 2 - Análisis de Centros Educativos
import streamlit as st
import pandas as pd

def mostrar_RegistroEducativos():
    st.sidebar.info("🏫 Análisis integral de centros educativos con filtros y visualizaciones clave.")
    
    # Cargar datos
    try:
        datos = pd.read_csv('WL_T_Centros_Educativos.csv')
        datos = datos.dropna(subset=['MUNICIPIO', 'CATEGORIA'])
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return
    
    st.title("🏫 Sistema de Análisis de Centros Educativos")
    
    # === INFORMACIÓN DEL SISTEMA ===
    with st.expander("ℹ️ Información del Sistema", expanded=False):
        st.markdown("""
        ### 🎯 **Capacidades del Análisis**
        - **📊 Visualización Integral**: 6 gráficos clave para entender el sistema educativo
        - **🔍 Filtros Inteligentes**: 5 filtros esenciales para análisis específicos
        - **📈 Métricas Automáticas**: Indicadores calculados en tiempo real
        - **🧠 Insights**: Interpretación automática de patrones importantes
        """)
    
    # === MÉTRICAS PRINCIPALES ===
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏫 Total Centros", f"{len(datos):,}")
    with col2:
        st.metric("🏛️ Municipios", datos['MUNICIPIO'].nunique())
    with col3:
        st.metric("🎓 Categorías", datos['CATEGORIA'].nunique())
    with col4:
        urbanos_pct = len(datos[datos['Zona'] == 'URBANA']) / len(datos) * 100
        st.metric("🌆 % Urbanos", f"{urbanos_pct:.1f}%")
    
    st.divider()
    
    # === FILTROS PRINCIPALES (TOP 5 MÁS IMPORTANTES) ===
    st.sidebar.markdown("## 🔧 Filtros Principales")
    
    # 1. FILTRO POR MUNICIPIO (Modo inteligente)
    modo_municipio = st.sidebar.radio(
        "🏛️ Selección de municipios:",
        ["Todos", "Top municipios", "Específicos"]
    )
    
    if modo_municipio == "Top municipios":
        top_n = st.sidebar.slider("¿Cuántos top municipios?", 3, 15, 8)
        top_municipios = datos['MUNICIPIO'].value_counts().head(top_n).index.tolist()
        municipio_sel = top_municipios
        st.sidebar.info(f"Seleccionados: {len(top_municipios)} municipios principales")
    elif modo_municipio == "Específicos":
        municipios = sorted(datos['MUNICIPIO'].unique())
        municipio_sel = st.sidebar.multiselect("Selecciona municipios:", municipios, default=[])
        if not municipio_sel:
            municipio_sel = municipios
    else:
        municipio_sel = datos['MUNICIPIO'].unique().tolist()
    
    # 2. FILTRO POR ESTADO DE INFRAESTRUCTURA (Crítico)
    estado_modo = st.sidebar.selectbox(
        "🏗️ Estado de infraestructura:",
        ["Todos los estados", "Solo estados críticos", "Solo buen estado", "Personalizado"]
    )
    
    if estado_modo == "Solo estados críticos":
        estado_sel = ['Malo', 'Deficit']
        st.sidebar.warning("Mostrando solo centros críticos")
    elif estado_modo == "Solo buen estado":
        estado_sel = ['Bueno']
        st.sidebar.success("Mostrando solo centros en buen estado")
    elif estado_modo == "Personalizado":
        estados = datos['Estado_InfraestructuraE'].dropna().unique()
        estado_sel = st.sidebar.multiselect("Estados específicos:", estados, default=list(estados))
    else:
        estado_sel = datos['Estado_InfraestructuraE'].dropna().unique().tolist()
    
    # 4. FILTRO POR CATEGORÍA EDUCATIVA
    categoria_todas = sorted(datos['CATEGORIA'].dropna().unique())
    categoria_sel = st.sidebar.multiselect(
        "🎓 Categorías educativas:",
        categoria_todas,
        default=[],
        help="Vacío = todas las categorías"
    )
    if not categoria_sel:
        categoria_sel = categoria_todas
    
    # 5. BÚSQUEDA POR TEXTO EN NOMBRE
    busqueda_texto = st.sidebar.text_input(
        "🔍 Buscar en nombres:",
        placeholder="Ej: Colegio, Universidad, Técnico...",
        help="Filtra centros que contengan este texto"
    )

    # === APLICAR FILTROS ===
    datos_filtrados = datos[
        datos['MUNICIPIO'].isin(municipio_sel) &
        datos['CATEGORIA'].isin(categoria_sel) &
        datos['Estado_InfraestructuraE'].isin(estado_sel)
    ]
    
    # Aplicar filtro de búsqueda por texto
    if busqueda_texto:
        datos_filtrados = datos_filtrados[
            datos_filtrados['ESTABLECIMIENTO_EDUCATIVO'].str.contains(busqueda_texto, case=False, na=False)
        ]
    
    # === MÉTRICAS FILTRADAS ===
    st.header(f"📊 Análisis de {len(datos_filtrados):,} Centros Seleccionados")
    
    if len(datos_filtrados) == 0:
        st.warning("⚠️ No hay centros que cumplan con los filtros seleccionados")
        return
    
    # Métricas de los datos filtrados
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        porcentaje_total = len(datos_filtrados) / len(datos) * 100
        st.metric("📈 % del Total", f"{porcentaje_total:.1f}%")
    with col2:
        municipios_filtrados = datos_filtrados['MUNICIPIO'].nunique()
        st.metric("🏛️ Municipios", municipios_filtrados)
    with col3:
        categorias_filtradas = datos_filtrados['CATEGORIA'].nunique()
        st.metric("� Categorías", categorias_filtradas)
    with col4:
        provincias_filtradas = datos_filtrados['PROVINCIA'].nunique()
        st.metric("🗺️ Provincias", provincias_filtradas)
    
    st.divider()
    
    # === 6 GRÁFICOS MÁS IMPORTANTES ===
    
    # GRÁFICO 1: TOP 10 MUNICIPIOS CON MÁS CENTROS
    st.subheader("🏆 Top 10 Municipios con Más Centros Educativos")
    with st.expander("💡 ¿Qué nos dice este gráfico?"):
        st.markdown("""
        - **Identifica** los municipios con mayor concentración educativa
        - **Muestra** posibles desequilibrios territoriales  
        - **Ayuda** a planificar redistribución de recursos
        """)
    
    top_municipios_graf = datos_filtrados['MUNICIPIO'].value_counts().head(10)
    if len(top_municipios_graf) > 0:
        st.bar_chart(top_municipios_graf)
        lider = top_municipios_graf.index[0]
        cantidad_lider = top_municipios_graf.values[0]
        st.success(f"🏆 **{lider}** lidera con {cantidad_lider} centros educativos")
    
    # GRÁFICO 2: ESTADO DE INFRAESTRUCTURA
    st.subheader("🏗️ Distribución por Estado de Infraestructura")
    with st.expander("💡 ¿Qué nos dice este gráfico?"):
        st.markdown("""
        - **Evalúa** la calidad general del sistema educativo
        - **Identifica** necesidades de inversión prioritaria
        - **Mide** el porcentaje de centros que requieren atención
        """)
    
    estado_graf = datos_filtrados['Estado_InfraestructuraE'].value_counts()
    if len(estado_graf) > 0:
        st.bar_chart(estado_graf)
        
        # Análisis automático del estado
        total_filtrados = len(datos_filtrados)
        buenos = estado_graf.get('Bueno', 0)
        criticos = estado_graf.get('Malo', 0) + estado_graf.get('Deficit', 0)
        
        col1, col2 = st.columns(2)
        with col1:
            if buenos > 0:
                pct_buenos = buenos / total_filtrados * 100
                st.metric("✅ Estado Bueno", f"{buenos}", f"{pct_buenos:.1f}%")
        with col2:
            if criticos > 0:
                pct_criticos = criticos / total_filtrados * 100
                st.metric("🚨 Estado Crítico", f"{criticos}", f"{pct_criticos:.1f}%")
    
    # GRÁFICO 3: TOP CATEGORÍAS EDUCATIVAS
    st.subheader("🎓 Top 10 Categorías Educativas Más Comunes")
    with st.expander("💡 ¿Qué nos dice este gráfico?"):
        st.markdown("""
        - **Muestra** qué tipos de educación predominan en la región
        - **Identifica** posibles vacíos en la oferta educativa
        - **Ayuda** a planificar nuevos tipos de centros según demanda
        """)
    
    categoria_graf = datos_filtrados['CATEGORIA'].value_counts().head(10)
    if len(categoria_graf) > 0:
        st.bar_chart(categoria_graf)
        categoria_principal = categoria_graf.index[0]
        cantidad_principal = categoria_graf.values[0]
        st.info(f"📚 **{categoria_principal}** es la categoría más común con {cantidad_principal} centros")
    
    # GRÁFICO 5: DISTRIBUCIÓN POR PROVINCIA
    st.subheader("🗺️ Distribución de Centros por Provincia")
    with st.expander("💡 ¿Qué nos dice este gráfico?"):
        st.markdown("""
        - **Muestra** la cobertura educativa a nivel provincial
        - **Identifica** provincias con mayor/menor dotación educativa
        - **Ayuda** en la planificación territorial de políticas educativas
        """)
    
    provincia_graf = datos_filtrados['PROVINCIA'].value_counts()
    if len(provincia_graf) > 0:
        st.bar_chart(provincia_graf)
        provincia_lider = provincia_graf.index[0]
        centros_lider = provincia_graf.values[0]
        participacion = centros_lider / len(datos_filtrados) * 100
        st.info(f"🗺️ **{provincia_lider}** concentra {centros_lider} centros ({participacion:.1f}% del total)")
    
    # === INSIGHTS AUTOMÁTICOS FINALES ===
    st.divider()
    st.subheader("🧠 Insights Clave del Análisis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Insight de cobertura
        cobertura_territorial = len(datos_filtrados['MUNICIPIO'].unique()) / len(datos['MUNICIPIO'].unique()) * 100
        if cobertura_territorial == 100:
            st.success(f"✅ Cobertura completa: {cobertura_territorial:.0f}% de municipios")
        else:
            st.info(f"📊 Cobertura parcial: {cobertura_territorial:.1f}% de municipios")
    
    with col2:
        # Insight de calidad
        if len(datos_filtrados) > 0:
            centros_buenos = len(datos_filtrados[datos_filtrados['Estado_InfraestructuraE'] == 'Bueno'])
            porcentaje_calidad = centros_buenos / len(datos_filtrados) * 100
            
            if porcentaje_calidad >= 60:
                st.success(f"✅ Buena calidad: {porcentaje_calidad:.1f}% en buen estado")
            elif porcentaje_calidad >= 30:
                st.warning(f"⚠️ Calidad media: {porcentaje_calidad:.1f}% en buen estado")  
            else:
                st.error(f"🚨 Baja calidad: {porcentaje_calidad:.1f}% en buen estado")
    
    with col3:
        # Insight de diversidad
        diversidad_educativa = len(datos_filtrados['CATEGORIA'].unique())
        if diversidad_educativa >= 10:
            st.success(f"🎓 Alta diversidad: {diversidad_educativa} tipos educativos")
        elif diversidad_educativa >= 5:
            st.info(f"📚 Diversidad media: {diversidad_educativa} tipos educativos")
        else:
            st.warning(f"📖 Baja diversidad: {diversidad_educativa} tipos educativos")
    
    # === TABLA DE DATOS DETALLADOS ===
    st.divider()
    st.subheader("📋 Datos Detallados (Primeros 20 registros)")
    
    # Seleccionar columnas más importantes para mostrar
    columnas_importantes = ['MUNICIPIO', 'ESTABLECIMIENTO_EDUCATIVO', 'CATEGORIA', 'Estado_InfraestructuraE', 'Zona', 'PROVINCIA']
    datos_mostrar = datos_filtrados[columnas_importantes].head(20)
    
    st.dataframe(datos_mostrar, use_container_width=True, hide_index=True)
    
    if len(datos_filtrados) > 20:
        st.info(f"ℹ️ Mostrando 20 de {len(datos_filtrados)} registros totales. Ajusta los filtros para ver datos específicos.")