import streamlit as st
import pandas as pd
from datetime import datetime


def cargar_datos_centros_educativos():
    """Cargar datos de centros educativos desde CSV y procesarlos"""
    try:
        # Cargar datos desde el archivo CSV
        df = pd.read_csv('WL_T_Centros_Educativos.csv')
        
        # Limpiar datos básicos
        df = df.dropna(subset=['MUNICIPIO', 'CATEGORIA'])
        
        # Limpiar espacios en blanco en columnas de texto
        for col in ['MUNICIPIO', 'CATEGORIA', 'Estado_InfraestructuraE', 'ESTABLECIMIENTO_EDUCATIVO']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Crear columnas derivadas para análisis
        if 'Estado_InfraestructuraE' in df.columns:
            df['Estado_Clasificado'] = df['Estado_InfraestructuraE'].map({
                'Bueno': 'Excelente',
                'Regular': 'Necesita Mejoras',
                'Malo': 'Crítico'
            }).fillna(df['Estado_InfraestructuraE'])
        
        return df
        
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'WL_T_Centros_Educativos.csv'")
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {e}")
        return None


def mostrar_resumen_general_educativo(df):
    """Mostrar resumen general de los centros educativos"""
    st.subheader("📊 Resumen General - Sistema Educativo")
    
    with st.expander("🏫 ¿Qué nos dicen los datos del sistema educativo?", expanded=False):
        st.markdown("""
        ### 🎯 **Análisis del Sistema Educativo Regional**
        
        Este análisis te permite entender la **distribución y estado** de la infraestructura 
        educativa en la región:
        
        - **📚 Total de Centros**: Cantidad de establecimientos educativos registrados
        - **🏛️ Municipios Cubiertos**: Alcance geográfico del sistema educativo
        - **🎭 Tipos de Categorías**: Diversidad de instituciones (preescolar, primaria, secundaria, etc.)
        - **🏗️ Estados de Infraestructura**: Condición física de los establecimientos
        
        ### 🎯 **¿Por qué es importante?**
        - **Planificación educativa**: Identificar necesidades por región
        - **Asignación de recursos**: Priorizar inversiones en infraestructura
        - **Cobertura geográfica**: Evaluar acceso a educación por municipio
        - **Calidad educativa**: Correlación entre infraestructura y resultados
        """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏫 Total Centros Educativos", len(df))
    
    with col2:
        st.metric("🏛️ Municipios Cubiertos", df['MUNICIPIO'].nunique())
    
    with col3:
        st.metric("🎭 Tipos de Categorías", df['CATEGORIA'].nunique())
    
    with col4:
        if 'Estado_InfraestructuraE' in df.columns:
            st.metric("🏗️ Estados de Infraestructura", df['Estado_InfraestructuraE'].nunique())
        else:
            st.metric("📊 Datos Únicos", df.shape[1])


def mostrar_estadisticas_educativas(df):
    """Mostrar estadísticas descriptivas de los centros educativos"""
    st.subheader("📈 Estadísticas del Sistema Educativo")
    
    with st.expander("📊 ¿Cómo interpretar las estadísticas educativas?", expanded=False):
        st.markdown("""
        ### 📚 **Métricas Educativas Explicadas**
        
        **🏫 Distribución por Municipio:**
        - **Concentración urbana vs. rural**: ¿Dónde hay más centros?
        - **Equidad territorial**: Distribución equilibrada de instituciones
        - **Necesidades de expansión**: Municipios con poca cobertura
        
        **🎓 Análisis por Categoría:**
        - **Niveles educativos**: Preescolar, primaria, secundaria, superior
        - **Especialización regional**: Tipos de educación por zona
        - **Cadena educativa**: Continuidad entre niveles
        
        **🏗️ Estado de Infraestructura:**
        - **Calidad del sistema**: % de centros en buen estado
        - **Necesidades de inversión**: Centros que requieren mejoras
        - **Priorización**: Identificar casos críticos
        
        ### 💡 **Insights que puedes obtener:**
        - **Brechas educativas** entre municipios
        - **Inversión prioritaria** según estado de infraestructura
        - **Planificación territorial** de nuevos centros
        - **Políticas públicas** basadas en datos reales
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏛️ Distribución por Municipio**")
        municipios_stats = df['MUNICIPIO'].value_counts().head(10)
        
        municipios_df = pd.DataFrame({
            'Municipio': municipios_stats.index,
            'Número_de_Centros': municipios_stats.values,
            'Porcentaje': (municipios_stats.values / len(df) * 100).round(1)
        })
        
        st.dataframe(municipios_df, use_container_width=True, hide_index=True)
        
        # Insight automático
        municipio_lider = municipios_stats.index[0]
        cantidad_lider = municipios_stats.values[0]
        st.info(f"🏆 **{municipio_lider}** lidera con {cantidad_lider} centros educativos")
    
    with col2:
        st.write("**🎓 Distribución por Categoría Educativa**")
        categorias_stats = df['CATEGORIA'].value_counts()
        
        categorias_df = pd.DataFrame({
            'Categoría': categorias_stats.index,
            'Cantidad': categorias_stats.values,
            'Porcentaje': (categorias_stats.values / len(df) * 100).round(1)
        })
        
        st.dataframe(categorias_df, use_container_width=True, hide_index=True)
        
        # Insight automático
        categoria_principal = categorias_stats.index[0]
        st.success(f"📚 **{categoria_principal}** es la categoría más común")


def mostrar_analisis_por_municipio(df):
    """Análisis detallado por municipio"""
    st.subheader("🏛️ Análisis por Municipio")
    
    with st.expander("🗺️ ¿Cómo interpretar el análisis municipal?", expanded=False):
        st.markdown("""
        ### 🏛️ **Análisis Territorial Educativo**
        
        **📊 Métricas por Municipio:**
        - **🏫 Total de Centros**: Cantidad absoluta de establecimientos
        - **🎓 Diversidad de Categorías**: Variedad de niveles educativos
        - **🏗️ Estado Promedio**: Condición general de la infraestructura
        - **📊 Participación %**: Representación en el sistema regional
        
        ### 🎯 **¿Qué puedes identificar?**
        - **Municipios bien dotados**: Alta cantidad y diversidad
        - **Zonas con deficiencias**: Poca cobertura o diversidad limitada  
        - **Calidad territorial**: Municipios con mejor/peor infraestructura
        - **Oportunidades de inversión**: Dónde se necesitan más recursos
        
        ### 💼 **Decisiones que puedes tomar:**
        - **Redistribuir recursos** hacia municipios con menos cobertura
        - **Priorizar mantenimiento** en zonas con infraestructura deficiente
        - **Planificar nuevos centros** en municipios con poca diversidad
        - **Establecer políticas** específicas por región
        """)
    
    # Análisis completo por municipio
    municipios_analisis = df.groupby('MUNICIPIO').agg({
        'ESTABLECIMIENTO_EDUCATIVO': 'count',
        'CATEGORIA': 'nunique'
    }).round(2)
    
    # Añadir análisis de estado si existe la columna
    if 'Estado_InfraestructuraE' in df.columns:
        # Calcular el estado promedio (asignando valores numéricos)
        estado_valores = {'Bueno': 3, 'Regular': 2, 'Malo': 1}
        df_temp = df.copy()
        df_temp['Estado_Numerico'] = df_temp['Estado_InfraestructuraE'].map(estado_valores)
        
        estado_promedio = df_temp.groupby('MUNICIPIO')['Estado_Numerico'].mean()
        municipios_analisis['Estado_Promedio_Num'] = estado_promedio
        
        # Convertir de vuelta a texto
        municipios_analisis['Estado_General'] = municipios_analisis['Estado_Promedio_Num'].apply(
            lambda x: 'Bueno' if x >= 2.5 else 'Regular' if x >= 1.5 else 'Malo'
        )
        municipios_analisis = municipios_analisis.drop('Estado_Promedio_Num', axis=1)
    
    # Calcular porcentaje de participación
    municipios_analisis['Participacion_%'] = (
        municipios_analisis['ESTABLECIMIENTO_EDUCATIVO'] / len(df) * 100
    ).round(1)
    
    # Renombrar columnas para mejor presentación
    municipios_analisis.columns = [
        'Total_Centros', 'Diversidad_Categorías', 'Estado_General', 'Participación_%'
    ] if 'Estado_InfraestructuraE' in df.columns else [
        'Total_Centros', 'Diversidad_Categorías', 'Participación_%'
    ]
    
    municipios_analisis = municipios_analisis.reset_index()
    
    st.write("**🏛️ Análisis Completo por Municipio**")
    st.dataframe(municipios_analisis, use_container_width=True, hide_index=True)
    
    # Top municipios
    st.write("**🏆 Top 5 Municipios por Cantidad de Centros Educativos**")
    top_municipios = municipios_analisis.nlargest(5, 'Total_Centros')[
        ['MUNICIPIO', 'Total_Centros', 'Diversidad_Categorías', 'Participación_%']
    ]
    st.dataframe(top_municipios, use_container_width=True, hide_index=True)
    
    # Insights automáticos
    if len(municipios_analisis) > 0:
        mejor_municipio = municipios_analisis.loc[
            municipios_analisis['Total_Centros'].idxmax()
        ]
        
        st.write("**💡 Insights Municipales:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🏆 **Municipio líder**: {mejor_municipio['MUNICIPIO']}")
            st.write(f"• {mejor_municipio['Total_Centros']} centros educativos")
            st.write(f"• {mejor_municipio['Diversidad_Categorías']} tipos de categorías")
        
        with col2:
            promedio_centros = municipios_analisis['Total_Centros'].mean()
            municipios_sobre_promedio = len(
                municipios_analisis[municipios_analisis['Total_Centros'] > promedio_centros]
            )
            st.info(f"📊 **Promedio regional**: {promedio_centros:.1f} centros por municipio")
            st.write(f"• {municipios_sobre_promedio} municipios sobre el promedio")


def mostrar_analisis_infraestructura(df):
    """Análisis del estado de infraestructura"""
    if 'Estado_InfraestructuraE' in df.columns and df['Estado_InfraestructuraE'].notna().any():
        st.subheader("🏗️ Análisis de Infraestructura Educativa")
        
        with st.expander("🔧 ¿Cómo evaluar la infraestructura educativa?", expanded=False):
            st.markdown("""
            ### 🏗️ **Estado de la Infraestructura Explicado**
            
            **🎯 Categorías de Estado:**
            - **🟢 Bueno**: Infraestructura en condiciones óptimas para el aprendizaje
            - **🟡 Regular**: Requiere mantenimiento preventivo o mejoras menores
            - **🔴 Malo**: Necesita intervención urgente o reconstrucción
            
            ### 📊 **Métricas de Infraestructura:**
            - **% de Centros por Estado**: Distribución general del sistema
            - **Análisis por Municipio**: Identificar zonas críticas
            - **Priorización de Inversión**: Centros que requieren atención inmediata
            - **Impacto Educativo**: Relación entre infraestructura y calidad
            
            ### 🎯 **¿Qué acciones tomar?**
            - **Centros en estado malo**: Intervención prioritaria inmediata
            - **Centros regulares**: Programar mantenimiento preventivo
            - **Centros buenos**: Mantener y usar como referencia
            - **Planificación presupuestal**: Asignar recursos según prioridades
            """)
        
        # Análisis general de infraestructura
        infraestructura_stats = df['Estado_InfraestructuraE'].value_counts()
        
        infraestructura_df = pd.DataFrame({
            'Estado': infraestructura_stats.index,
            'Cantidad': infraestructura_stats.values,
            'Porcentaje': (infraestructura_stats.values / len(df) * 100).round(1)
        })
        
        st.write("**🏗️ Estado General de Infraestructura**")
        st.dataframe(infraestructura_df, use_container_width=True, hide_index=True)
        
        # Análisis crítico
        col1, col2, col3 = st.columns(3)
        
        with col1:
            buenos = infraestructura_df[infraestructura_df['Estado'] == 'Bueno']['Porcentaje'].sum()
            st.metric("🟢 Estado Bueno", f"{buenos:.1f}%")
        
        with col2:
            regulares = infraestructura_df[infraestructura_df['Estado'] == 'Regular']['Porcentaje'].sum()
            st.metric("🟡 Estado Regular", f"{regulares:.1f}%")
        
        with col3:
            malos = infraestructura_df[infraestructura_df['Estado'] == 'Malo']['Porcentaje'].sum()
            st.metric("🔴 Estado Malo", f"{malos:.1f}%")
        
        # Análisis por municipio y estado
        st.write("**🏛️ Estado de Infraestructura por Municipio**")
        
        infraestructura_municipio = pd.crosstab(
            df['MUNICIPIO'], 
            df['Estado_InfraestructuraE'], 
            margins=True
        )
        
        # Convertir a porcentajes por municipio (excluyendo la fila 'All')
        municipios_sin_total = infraestructura_municipio.drop('All', axis=0)
        infraestructura_pct = municipios_sin_total.div(
            municipios_sin_total.sum(axis=1), axis=0
        ) * 100
        infraestructura_pct = infraestructura_pct.round(1)
        
        st.dataframe(infraestructura_pct, use_container_width=True)
        
        # Identificar municipios críticos
        if 'Malo' in infraestructura_pct.columns:
            municipios_criticos = infraestructura_pct[
                infraestructura_pct['Malo'] > 30
            ].sort_values('Malo', ascending=False)
            
            if len(municipios_criticos) > 0:
                st.warning("⚠️ **Municipios con Infraestructura Crítica (>30% en mal estado)**")
                criticos_df = municipios_criticos[['Malo']].reset_index()
                criticos_df.columns = ['Municipio', '% Estado Malo']
                st.dataframe(criticos_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ **Excelente**: Ningún municipio tiene más del 30% de centros en mal estado")


def mostrar_analisis_categorias(df):
    """Análisis por categoría educativa"""
    st.subheader("🎓 Análisis por Categoría Educativa")
    
    with st.expander("📚 ¿Cómo interpretar las categorías educativas?", expanded=False):
        st.markdown("""
        ### 🎓 **Niveles del Sistema Educativo**
        
        **📊 Análisis por Categoría Educativa:**
        - **🧒 Educación Inicial**: Preescolar y jardines infantiles
        - **📚 Educación Básica**: Primaria y secundaria básica
        - **🎯 Educación Media**: Bachillerato y educación técnica
        - **🏛️ Educación Superior**: Universidades e institutos técnicos
        
        ### 🔍 **¿Qué puedes identificar?**
        - **Cobertura por nivel**: ¿Hay suficientes centros en cada categoría?
        - **Cadena educativa**: Continuidad entre niveles educativos
        - **Especialización regional**: Fortalezas educativas por zona
        - **Brechas del sistema**: Niveles con poca representación
        
        ### 📈 **Métricas Importantes:**
        - **Distribución territorial**: Dónde se concentra cada nivel
        - **Estado por categoría**: Calidad de infraestructura por nivel
        - **Densidad educativa**: Relación entre categorías y población
        """)
    
    # Análisis general por categoría
    categoria_analisis = df.groupby('CATEGORIA').agg({
        'ESTABLECIMIENTO_EDUCATIVO': 'count',
        'MUNICIPIO': 'nunique'
    })
    
    # Añadir análisis de infraestructura si existe
    if 'Estado_InfraestructuraE' in df.columns:
        # Estado promedio por categoría
        estado_valores = {'Bueno': 3, 'Regular': 2, 'Malo': 1}
        df_temp = df.copy()
        df_temp['Estado_Numerico'] = df_temp['Estado_InfraestructuraE'].map(estado_valores)
        
        estado_promedio_cat = df_temp.groupby('CATEGORIA')['Estado_Numerico'].mean()
        categoria_analisis['Estado_Promedio'] = estado_promedio_cat.apply(
            lambda x: 'Bueno' if x >= 2.5 else 'Regular' if x >= 1.5 else 'Malo'
        )
    
    # Calcular porcentajes
    categoria_analisis['Porcentaje_Sistema'] = (
        categoria_analisis['ESTABLECIMIENTO_EDUCATIVO'] / len(df) * 100
    ).round(1)
    
    # Renombrar columnas
    columnas = ['Total_Centros', 'Municipios_Presentes', 'Estado_Promedio', 'Participación_%'] if 'Estado_InfraestructuraE' in df.columns else ['Total_Centros', 'Municipios_Presentes', 'Participación_%']
    categoria_analisis.columns = columnas
    categoria_analisis = categoria_analisis.reset_index()
    
    st.write("**🎓 Análisis Completo por Categoría Educativa**")
    st.dataframe(categoria_analisis, use_container_width=True, hide_index=True)
    
    # Análisis de cobertura territorial por categoría
    st.write("**🗺️ Cobertura Territorial por Categoría**")
    
    cobertura_territorial = pd.crosstab(df['CATEGORIA'], df['MUNICIPIO'])
    cobertura_pct = (cobertura_territorial > 0).sum(axis=1) / df['MUNICIPIO'].nunique() * 100
    
    cobertura_df = pd.DataFrame({
        'Categoría': cobertura_pct.index,
        'Municipios_con_Presencia': (cobertura_territorial > 0).sum(axis=1).values,
        'Cobertura_Territorial_%': cobertura_pct.round(1).values
    })
    
    st.dataframe(cobertura_df, use_container_width=True, hide_index=True)
    
    # Insights automáticos
    if len(categoria_analisis) > 0:
        categoria_principal = categoria_analisis.loc[
            categoria_analisis['Total_Centros'].idxmax()
        ]
        
        mejor_cobertura = cobertura_df.loc[
            cobertura_df['Cobertura_Territorial_%'].idxmax()
        ]
        
        st.write("**💡 Insights del Sistema Educativo:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"📚 **Categoría dominante**: {categoria_principal['CATEGORIA']}")
            st.write(f"• {categoria_principal['Total_Centros']} centros ({categoria_principal['Participación_%']}%)")
            
        with col2:
            st.info(f"🗺️ **Mejor cobertura territorial**: {mejor_cobertura['Categoría']}")
            st.write(f"• Presente en {mejor_cobertura['Cobertura_Territorial_%']}% de municipios")


def mostrar_datos_detallados_educativos(df):
    """Mostrar tabla de datos detallados con filtros"""
    st.subheader("🔍 Datos Detallados - Centros Educativos")
    
    with st.expander("🎛️ ¿Cómo usar los filtros del sistema educativo?", expanded=False):
        st.markdown("""
        ### 🔧 **Sistema de Filtros Educativos**
        
        **🏛️ Filtro por Municipio:**
        - Selecciona **municipios específicos** para análisis regional
        - Útil para **comparaciones territoriales** y planificación local
        - Permite **análisis multi-municipio** para estudios comparativos
        
        **🎓 Filtro por Categoría:**
        - Filtra por **nivel educativo** (preescolar, primaria, etc.)
        - Perfecto para **planificación sectorial** por tipo de educación
        - Identifica **necesidades específicas** por nivel
        
        **🏗️ Filtro por Estado de Infraestructura:**
        - Enfócate en centros por **condición física**
        - Ideal para **priorización de inversiones** y mantenimiento
        - Útil para **auditorías** y planes de mejora
        
        ### 💡 **Casos de uso prácticos:**
        - **Planificación municipal**: Filtrar por municipio específico
        - **Política sectorial**: Filtrar por categoría educativa
        - **Mantenimiento**: Filtrar centros en mal estado
        - **Estudios comparativos**: Combinar múltiples filtros
        """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por municipio
        municipios = ['Todos'] + sorted(df['MUNICIPIO'].unique().tolist())
        municipios_seleccionados = st.multiselect(
            "🏛️ Filtrar por Municipio(s):", 
            municipios,
            default=['Todos'],
            help="Selecciona uno o varios municipios para análisis territorial"
        )
    
    with col2:
        # Filtro por categoría
        categorias = ['Todas'] + sorted(df['CATEGORIA'].unique().tolist())
        categorias_seleccionadas = st.multiselect(
            "🎓 Filtrar por Categoría(s):",
            categorias,
            default=['Todas'],
            help="Filtra por nivel o tipo de educación"
        )
    
    with col3:
        # Filtro por estado de infraestructura
        if 'Estado_InfraestructuraE' in df.columns:
            estados = ['Todos'] + sorted(df['Estado_InfraestructuraE'].dropna().unique().tolist())
            estados_seleccionados = st.multiselect(
                "🏗️ Filtrar por Estado:",
                estados,
                default=['Todos'],
                help="Filtra por condición de la infraestructura"
            )
        else:
            estados_seleccionados = ['Todos']
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if 'Todos' not in municipios_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['MUNICIPIO'].isin(municipios_seleccionados)]
    
    if 'Todas' not in categorias_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado['CATEGORIA'].isin(categorias_seleccionadas)]
    
    if 'Estado_InfraestructuraE' in df.columns and 'Todos' not in estados_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['Estado_InfraestructuraE'].isin(estados_seleccionados)]
    
    # Mostrar información de filtros aplicados
    filtros_activos = []
    if 'Todos' not in municipios_seleccionados:
        filtros_activos.append(f"🏛️ {len(municipios_seleccionados)} municipio(s)")
    if 'Todas' not in categorias_seleccionadas:
        filtros_activos.append(f"🎓 {len(categorias_seleccionadas)} categoría(s)")
    if 'Estado_InfraestructuraE' in df.columns and 'Todos' not in estados_seleccionados:
        filtros_activos.append(f"🏗️ {len(estados_seleccionados)} estado(s)")
    
    if len(df_filtrado) != len(df):
        filtros_texto = " • ".join(filtros_activos) if filtros_activos else "Filtros aplicados"
        st.info(f"🔍 **{filtros_texto}**: Mostrando {len(df_filtrado)} de {len(df)} centros educativos")
    
    # Seleccionar columnas a mostrar
    columnas_mostrar = ['ESTABLECIMIENTO_EDUCATIVO', 'MUNICIPIO', 'CATEGORIA']
    if 'Estado_InfraestructuraE' in df.columns:
        columnas_mostrar.append('Estado_InfraestructuraE')
    
    # Agregar más columnas si existen
    columnas_adicionales = ['DIRECCION', 'SEDE', 'BARRIO', 'COMUNA'] 
    for col in columnas_adicionales:
        if col in df.columns:
            columnas_mostrar.append(col)
    
    df_mostrar = df_filtrado[columnas_mostrar].head(100)  # Limitar a 100 registros para rendimiento
    
    st.write(f"**📊 Tabla de Centros Educativos (máximo 100 registros)**")
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # Estadísticas rápidas de los datos filtrados
    if len(df_filtrado) > 0:
        st.write("**📈 Estadísticas Rápidas de la Selección:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏫 Centros Seleccionados", len(df_filtrado))
        
        with col2:
            st.metric("🏛️ Municipios Únicos", df_filtrado['MUNICIPIO'].nunique())
        
        with col3:
            st.metric("🎓 Categorías Únicas", df_filtrado['CATEGORIA'].nunique())


def mostrar_resumen_ejecutivo_educativo(df):
    """Mostrar resumen ejecutivo del sistema educativo"""
    st.subheader("📋 Resumen Ejecutivo - Sistema Educativo")
    
    with st.expander("💼 ¿Qué es el Resumen Ejecutivo Educativo?", expanded=False):
        st.markdown("""
        ### 🎯 **Síntesis del Sistema Educativo Regional**
        
        El **resumen ejecutivo educativo** condensa los hallazgos más importantes 
        sobre la infraestructura y distribución educativa para **decisiones estratégicas**.
        
        ### 📊 **Incluye:**
        - **Métricas clave** del sistema educativo regional
        - **Identificación de brechas** y oportunidades
        - **Recomendaciones** para políticas públicas
        - **Prioridades de inversión** basadas en datos
        - **Alertas** sobre situaciones críticas
        """)
    
    # Métricas principales
    total_centros = len(df)
    total_municipios = df['MUNICIPIO'].nunique()
    total_categorias = df['CATEGORIA'].nunique()
    
    # Métricas de infraestructura
    if 'Estado_InfraestructuraE' in df.columns:
        centros_buenos = len(df[df['Estado_InfraestructuraE'] == 'Bueno'])
        centros_malos = len(df[df['Estado_InfraestructuraE'] == 'Malo'])
        porcentaje_buenos = (centros_buenos / total_centros * 100)
        porcentaje_malos = (centros_malos / total_centros * 100)
    
    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏫 Total de Centros", 
            total_centros,
            help="Número total de establecimientos educativos registrados"
        )
    
    with col2:
        st.metric(
            "🏛️ Cobertura Territorial", 
            f"{total_municipios} municipios",
            help="Alcance geográfico del sistema educativo"
        )
    
    with col3:
        st.metric(
            "🎓 Diversidad Educativa", 
            f"{total_categorias} categorías",
            help="Variedad de niveles y tipos educativos"
        )
    
    with col4:
        if 'Estado_InfraestructuraE' in df.columns:
            st.metric(
                "🏗️ Infraestructura Buena", 
                f"{porcentaje_buenos:.1f}%",
                help="Porcentaje de centros en buen estado"
            )
    
    # Análisis de distribución territorial
    st.write("### 🗺️ **Análisis Territorial**")
    
    # Distribución por municipio
    municipios_stats = df['MUNICIPIO'].value_counts()
    concentracion = (municipios_stats.head(3).sum() / total_centros * 100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏛️ Distribución Municipal**")
        
        if concentracion > 50:
            st.warning(f"⚠️ Alta concentración: {concentracion:.1f}% de centros en top 3 municipios")
        elif concentracion > 30:
            st.info(f"📊 Concentración moderada: {concentracion:.1f}% en top 3 municipios")
        else:
            st.success(f"✅ Distribución equilibrada: {concentracion:.1f}% en top 3 municipios")
        
        municipio_lider = municipios_stats.index[0]
        cantidad_lider = municipios_stats.values[0]
        st.write(f"🏆 **Municipio líder**: {municipio_lider} ({cantidad_lider} centros)")
        
    with col2:
        st.write("**🎓 Cobertura Educativa**")
        
        # Análisis de categorías
        categorias_stats = df['CATEGORIA'].value_counts()
        categoria_principal = categorias_stats.index[0]
        porcentaje_principal = (categorias_stats.values[0] / total_centros * 100)
        
        if porcentaje_principal > 60:
            st.warning(f"⚠️ Sobre-representación: {categoria_principal} ({porcentaje_principal:.1f}%)")
        else:
            st.success(f"✅ Distribución balanceada de categorías educativas")
        
        st.write(f"📚 **Categoría principal**: {categoria_principal}")
    
    # Análisis de infraestructura
    if 'Estado_InfraestructuraE' in df.columns:
        st.write("### 🏗️ **Estado de Infraestructura**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if porcentaje_buenos >= 70:
                st.success(f"✅ Excelente: {porcentaje_buenos:.1f}% en buen estado")
            elif porcentaje_buenos >= 50:
                st.info(f"📊 Aceptable: {porcentaje_buenos:.1f}% en buen estado")
            else:
                st.warning(f"⚠️ Crítico: Solo {porcentaje_buenos:.1f}% en buen estado")
        
        with col2:
            if porcentaje_malos <= 10:
                st.success(f"✅ Pocos centros críticos ({porcentaje_malos:.1f}%)")
            elif porcentaje_malos <= 25:
                st.warning(f"⚠️ Atención requerida ({porcentaje_malos:.1f}% en mal estado)")
            else:
                st.error(f"🚨 Situación crítica ({porcentaje_malos:.1f}% en mal estado)")
        
        with col3:
            inversion_estimada = centros_malos * 50000  # Estimación de $50k por centro
            st.metric("💰 Inversión Estimada", f"${inversion_estimada:,.0f}")
    
    # Recomendaciones automáticas
    st.write("### 💡 **Recomendaciones Estratégicas**")
    
    recomendaciones = []
    
    if concentracion > 50:
        recomendaciones.append("🗺️ **Descentralizar**: Promover centros educativos en municipios con menor cobertura")
    
    if 'Estado_InfraestructuraE' in df.columns:
        if porcentaje_malos > 20:
            recomendaciones.append("🏗️ **Inversión urgente**: Priorizar mejoramiento de infraestructura crítica")
        elif porcentaje_buenos < 60:
            recomendaciones.append("🔧 **Plan de mantenimiento**: Implementar programa preventivo de infraestructura")
    
    # Análisis de brechas por categoría
    cobertura_categorias = pd.crosstab(df['CATEGORIA'], df['MUNICIPIO'])
    cobertura_pct = (cobertura_categorias > 0).sum(axis=1) / total_municipios * 100
    
    if (cobertura_pct < 50).any():
        categorias_limitadas = cobertura_pct[cobertura_pct < 50].index.tolist()
        recomendaciones.append(f"📚 **Expandir cobertura**: Aumentar presencia de {', '.join(categorias_limitadas[:2])} en más municipios")
    
    if not recomendaciones:
        st.success("🎉 **¡Excelente!** El sistema educativo muestra una distribución balanceada")
    else:
        for i, rec in enumerate(recomendaciones, 1):
            st.write(f"{i}. {rec}")
    
    # Próximos pasos
    st.write("### 🎯 **Próximos Pasos Sugeridos**")
    
    pasos = [
        "📊 **Análisis demográfico**: Correlacionar centros educativos con densidad poblacional",
        "🚌 **Estudio de accesibilidad**: Evaluar transporte y distancias a centros educativos",
        "👥 **Análisis de capacidad**: Determinar si la oferta satisface la demanda",
        "💰 **Plan de inversión**: Priorizar recursos según análisis de necesidades",
        "📈 **Monitoreo continuo**: Establecer indicadores para seguimiento regular"
    ]
    
    for paso in pasos:
        st.write(f"• {paso}")


def mostrar_exploracion_datos_educativos():
    """Función principal para mostrar la exploración de datos educativos"""
    st.title("📚 Exploración de Datos - Sistema Educativo Regional")
    
    # Información sobre la aplicación de exploración educativa
    with st.expander("ℹ️ ¿Qué es el Análisis del Sistema Educativo?", expanded=False):
        st.markdown("""
        ### 🎯 **Propósito del Análisis Educativo**
        
        El **análisis del sistema educativo** permite evaluar y optimizar la distribución,
        calidad e infraestructura de los centros educativos en una región.
        
        ### 🔍 **¿Qué encontrarás en esta sección?**
        - 📊 **Estadísticas generales**: Distribución de centros por región y tipo
        - 🏛️ **Análisis territorial**: Cobertura educativa por municipio
        - 🏗️ **Estado de infraestructura**: Condición física de los establecimientos
        - 🎓 **Análisis por categoría**: Niveles educativos y especialización
        - 🔍 **Datos detallados**: Exploración completa con filtros avanzados
        - 📋 **Resumen ejecutivo**: Insights para toma de decisiones
        
        ### 💡 **¿Para qué sirve?**
        - **Planificación educativa** basada en datos reales
        - **Asignación eficiente** de recursos y presupuesto
        - **Identificación de brechas** en cobertura territorial
        - **Priorización de inversiones** en infraestructura
        - **Políticas públicas** informadas por evidencia
        - **Monitoreo del sistema** educativo regional
        """)
    
    st.write("**Análisis integral del sistema educativo usando datos de centros educativos regionales**")
    
    # Cargar datos con información detallada
    with st.spinner("📚 Cargando datos del sistema educativo..."):
        df = cargar_datos_centros_educativos()
    
    if df is not None and not df.empty:
        st.success(f"✅ **Datos educativos cargados**: {len(df)} centros educativos procesados")
        
        # Información rápida sobre los datos cargados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"🏫 **{len(df)}** Centros Educativos")
        with col2:
            st.info(f"🏛️ **{df['MUNICIPIO'].nunique()}** Municipios")
        with col3:
            st.info(f"🎓 **{df['CATEGORIA'].nunique()}** Categorías Educativas")
        with col4:
            if 'Estado_InfraestructuraE' in df.columns:
                st.info(f"🏗️ **{df['Estado_InfraestructuraE'].nunique()}** Estados de Infraestructura")
            else:
                st.info("🏗️ **Estado**: No disponible")
        
        st.divider()
        
        # Mostrar diferentes secciones de análisis
        mostrar_resumen_general_educativo(df)
        
        st.divider()
        mostrar_estadisticas_educativas(df)
        
        st.divider()
        mostrar_analisis_por_municipio(df)
        
        st.divider()
        mostrar_analisis_infraestructura(df)
        
        st.divider()
        mostrar_analisis_categorias(df)
        
        st.divider()
        mostrar_datos_detallados_educativos(df)
        
        st.divider()
        mostrar_resumen_ejecutivo_educativo(df)
        
    else:
        st.error("❌ No se pudieron cargar los datos educativos. Verifica que el archivo 'WL_T_Centros_Educativos.csv' exista en el directorio.")


if __name__ == "__main__":
    mostrar_exploracion_datos_educativos()
