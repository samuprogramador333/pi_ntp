import streamlit as st
import pandas as pd
import requests
from datetime import datetime


def cargar_datos_api():
    """Cargar datos desde la API y procesarlos correctamente"""
    try:
        # Realizar petición GET a la API
        response = requests.get('https://68de838bd7b591b4b78fce39.mockapi.io/Horarios')

        if response.status_code == 200:
            # Convertir la respuesta JSON a DataFrame
            data = response.json()
            df = pd.DataFrame(data)
            
            # Limpiar datos nulos o vacíos
            df = df.dropna(subset=['nombre', 'fecha', 'hora_entrada', 'hora_salida'])
            
            # Convertir la columna fecha correctamente
            df['fecha'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
            
            # Eliminar filas con fechas inválidas
            df = df.dropna(subset=['fecha'])
            
            # Agregar columna de duración calculada
            try:
                # Convertir horas a datetime para calcular duración
                df['hora_entrada_dt'] = pd.to_datetime(df['hora_entrada'], format='%H:%M', errors='coerce')
                df['hora_salida_dt'] = pd.to_datetime(df['hora_salida'], format='%H:%M', errors='coerce')
                
                # Eliminar filas con horas inválidas
                df = df.dropna(subset=['hora_entrada_dt', 'hora_salida_dt'])
                
                # Calcular duración en horas
                df['duracion_horas'] = (df['hora_salida_dt'] - df['hora_entrada_dt']).dt.total_seconds() / 3600
                
                # Manejar casos donde la salida es al día siguiente (duración negativa)
                df.loc[df['duracion_horas'] < 0, 'duracion_horas'] += 24
                
            except Exception as e:
                st.warning(f"Error calculando duración: {e}")
                df['duracion_horas'] = 8.0  # Valor por defecto

            # Limpiar columnas de texto
            for col in ['nombre', 'area', 'rol']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
            
            # Crear variables derivadas para análisis
            df['dia_semana'] = df['fecha'].dt.day_name()
            df['dia_semana_es'] = df['fecha'].dt.dayofweek.map({
                0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 
                4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
            })
            df['mes'] = df['fecha'].dt.month_name()
            df['mes_numero'] = df['fecha'].dt.month
            
            return df
        else:
            st.error(f"Error en la petición: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error al cargar datos de la API: {e}")
        return None


def mostrar_resumen_general(df):
    """Mostrar resumen general de los datos"""
    st.subheader("📊 Resumen General de los Datos")
    
    with st.expander("🔍 ¿Qué nos dice el resumen general?", expanded=False):
        st.markdown("""
        ### 📋 **Métricas Fundamentales**
        Estas métricas te dan una **vista panorámica** de todo el conjunto de datos:
        
        - **📝 Total de Registros**: Cantidad total de entradas de horarios en la base de datos
        - **👥 Empleados Únicos**: Número de personas diferentes que han registrado horarios
        - **📅 Días Registrados**: Cantidad de días únicos con actividad laboral
        - **🏢 Áreas/Promedio**: Número de departamentos o promedio de horas por día
        
        ### 🎯 **¿Por qué es importante?**
        - Te permite **evaluar el volumen** de información disponible
        - Identifica la **cobertura temporal** de los datos
        - Muestra la **diversidad organizacional** (empleados y áreas)
        - Establece el **contexto base** para análisis más profundos
        """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", len(df))
    
    with col2:
        st.metric("Empleados Únicos", df['nombre'].nunique())
    
    with col3:
        st.metric("Días Registrados", df['fecha'].nunique())
    
    with col4:
        if 'area' in df.columns:
            st.metric("Áreas", df['area'].nunique())
        else:
            st.metric("Promedio Horas/Día", f"{df['duracion_horas'].mean():.1f}")


def mostrar_estadisticas_basicas(df):
    """Mostrar estadísticas descriptivas básicas"""
    st.subheader("📈 Estadísticas Básicas")
    
    with st.expander("📊 ¿Cómo interpretar las estadísticas descriptivas?", expanded=False):
        st.markdown("""
        ### 🧮 **Métricas Estadísticas Explicadas**
        
        - **📊 Conteo**: Número total de registros válidos
        - **📈 Promedio**: Valor medio de horas trabajadas (tendencia central)
        - **📏 Desviación Estándar**: Mide qué tan dispersos están los datos del promedio
        - **⬇️ Mínimo**: La jornada más corta registrada
        - **📊 Percentil 25%**: El 25% de las jornadas duran menos que este valor
        - **🎯 Mediana (50%)**: Valor que divide los datos por la mitad
        - **📊 Percentil 75%**: El 75% de las jornadas duran menos que este valor
        - **⬆️ Máximo**: La jornada más larga registrada
        
        ### 💡 **¿Qué puedes descubrir?**
        - Si hay **consistencia** en los horarios (desviación baja = más uniforme)
        - Si existen **valores atípicos** (diferencia grande entre min/max y percentiles)
        - El **rango normal** de trabajo (entre percentil 25% y 75%)
        - Si la distribución es **simétrica** (promedio ≈ mediana) o **sesgada**
        """)
    
    # Estadísticas de horas trabajadas
    if 'duracion_horas' in df.columns:
        st.write("**⏱️ Horas Trabajadas - Estadísticas Descriptivas**")
        
        stats_horas = df['duracion_horas'].describe()
        
        # Crear tabla de estadísticas
        stats_df = pd.DataFrame({
            'Métrica': ['Conteo', 'Promedio', 'Desviación Estándar', 'Mínimo', 'Percentil 25%', 'Mediana', 'Percentil 75%', 'Máximo'],
            'Valor': [
                f"{stats_horas['count']:.0f}",
                f"{stats_horas['mean']:.2f} horas",
                f"{stats_horas['std']:.2f} horas",
                f"{stats_horas['min']:.2f} horas",
                f"{stats_horas['25%']:.2f} horas",
                f"{stats_horas['50%']:.2f} horas",
                f"{stats_horas['75%']:.2f} horas",
                f"{stats_horas['max']:.2f} horas"
            ]
        })
        
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        # Agregar insights automáticos
        promedio = df['duracion_horas'].mean()
        mediana = df['duracion_horas'].median()
        desv_std = df['duracion_horas'].std()
        
        st.write("**📋 Interpretación Automática:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if desv_std < 1:
                st.success("✅ **Horarios muy consistentes** (baja variabilidad)")
            elif desv_std < 2:
                st.info("📊 **Horarios moderadamente consistentes**")
            else:
                st.warning("⚠️ **Horarios muy variables** (alta dispersión)")
        
        with col2:
            if abs(promedio - mediana) < 0.5:
                st.success("✅ **Distribución balanceada** (promedio ≈ mediana)")
            else:
                st.info("📈 **Distribución con sesgo** (promedio ≠ mediana)")


def mostrar_analisis_empleados(df):
    """Análisis por empleado"""
    st.subheader("👥 Análisis por Empleado")
    
    with st.expander("🔍 ¿Cómo entender el análisis por empleado?", expanded=False):
        st.markdown("""
        ### 👤 **Métricas Individuales Explicadas**
        
        - **📅 Días Trabajados**: Cuántos días ha registrado horarios cada empleado
        - **⭐ Promedio Horas**: Horas promedio por jornada de cada persona
        - **⬇️ Min Horas**: La jornada más corta de cada empleado
        - **⬆️ Max Horas**: La jornada más larga de cada empleado
        - **🏆 Total Horas**: Suma total de todas las horas trabajadas
        - **📅 Primera/Última Fecha**: Rango temporal de actividad
        
        ### 🎯 **Insights que puedes obtener:**
        - **Consistencia individual**: Diferencia entre min y max horas
        - **Productividad relativa**: Comparar total de horas entre empleados
        - **Patrones de asistencia**: Frecuencia de registro por persona
        - **Identificación de top performers**: Empleados más productivos
        - **Detección de irregularidades**: Jornadas excesivamente largas o cortas
        
        ### 📊 **Tabla Top 10**
        Muestra los **empleados más productivos** basándose en el total de horas trabajadas,
        incluyendo métricas clave para comparar su rendimiento.
        """)
    
    # Resumen por empleado
    empleados_stats = df.groupby('nombre').agg({
        'duracion_horas': ['count', 'mean', 'min', 'max', 'sum'],
        'fecha': ['min', 'max']
    }).round(2)
    
    # Aplanar las columnas multi-nivel
    empleados_stats.columns = ['Días_Trabajados', 'Promedio_Horas', 'Min_Horas', 'Max_Horas', 'Total_Horas', 'Primera_Fecha', 'Última_Fecha']
    empleados_stats = empleados_stats.reset_index()
    
    st.write("**Resumen de Trabajo por Empleado**")
    st.dataframe(empleados_stats, use_container_width=True)
    
    # Top empleados por horas trabajadas
    st.write("**Top 10 Empleados por Total de Horas Trabajadas**")
    top_empleados = empleados_stats.nlargest(10, 'Total_Horas')[['nombre', 'Total_Horas', 'Días_Trabajados', 'Promedio_Horas']]
    st.dataframe(top_empleados, use_container_width=True, hide_index=True)
    
    # Insights automáticos para empleados
    if len(top_empleados) > 0:
        mejor_empleado = top_empleados.iloc[0]
        total_empleados = len(empleados_stats)
        
        st.write("**💡 Insights Destacados:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"🏆 **Top Performer**: {mejor_empleado['nombre']}")
            st.write(f"• Total: {mejor_empleado['Total_Horas']:.1f} horas")
            st.write(f"• Promedio: {mejor_empleado['Promedio_Horas']:.1f} h/día")
        
        with col2:
            promedio_general = empleados_stats['Total_Horas'].mean()
            if mejor_empleado['Total_Horas'] > promedio_general * 1.5:
                st.success("⭐ **Productividad excepcional** vs. promedio general")
            else:
                st.info("📊 **Rendimiento dentro del rango normal**")


def mostrar_analisis_temporal(df):
    """Análisis temporal básico"""
    st.subheader("📅 Análisis Temporal")
    
    with st.expander("⏰ ¿Qué revelan los patrones temporales?", expanded=False):
        st.markdown("""
        ### 📊 **Análisis por Día de la Semana**
        
        **¿Qué mide cada métrica?**
        - **📝 Número de Registros**: Cuántos empleados trabajaron cada día
        - **⏱️ Promedio Horas**: Duración promedio de las jornadas por día
        - **🏆 Total Horas**: Suma de todas las horas trabajadas ese día
        
        **🔍 Patrones que puedes identificar:**
        - **Días más productivos**: ¿Lunes o viernes son diferentes?
        - **Consistencia semanal**: ¿Hay días con menor actividad?
        - **Carga de trabajo**: ¿Se concentra en días específicos?
        
        ### 📆 **Análisis por Mes**
        (Solo aparece si hay datos de múltiples meses)
        
        **💡 Insights estacionales:**
        - **Variaciones mensuales** en productividad
        - **Tendencias temporales** de largo plazo  
        - **Picos y valles** de actividad laboral
        - **Planificación de recursos** según estacionalidad
        
        ### 🎯 **¿Para qué usar esta información?**
        - **Optimizar horarios** según días más productivos
        - **Planificar recursos** humanos por día/mes
        - **Identificar necesidades** de personal por períodos
        - **Detectar patrones** de ausentismo o sobretiempo
        """)
    
    # Análisis por día de la semana
    st.write("**Trabajo por Día de la Semana**")
    dias_stats = df.groupby('dia_semana_es').agg({
        'duracion_horas': ['count', 'mean', 'sum']
    }).round(2)
    
    dias_stats.columns = ['Número_Registros', 'Promedio_Horas', 'Total_Horas']
    dias_stats = dias_stats.reset_index()
    
    # Ordenar por días de la semana
    orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dias_stats['dia_semana_es'] = pd.Categorical(dias_stats['dia_semana_es'], categories=orden_dias, ordered=True)
    dias_stats = dias_stats.sort_values('dia_semana_es')
    
    st.dataframe(dias_stats, use_container_width=True, hide_index=True)
    
    # Análisis automático de patrones semanales
    dia_mas_activo = dias_stats.loc[dias_stats['Total_Horas'].idxmax(), 'dia_semana_es']
    dia_menos_activo = dias_stats.loc[dias_stats['Total_Horas'].idxmin(), 'dia_semana_es']
    
    st.write("**📊 Análisis Semanal Automático:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"🏆 **Día más productivo**: {dia_mas_activo}")
        horas_max = dias_stats['Total_Horas'].max()
        st.write(f"• {horas_max:.1f} horas totales")
    
    with col2:
        st.info(f"📉 **Día menos activo**: {dia_menos_activo}")
        horas_min = dias_stats['Total_Horas'].min()
        st.write(f"• {horas_min:.1f} horas totales")
    
    # Análisis por mes
    if df['mes'].nunique() > 1:
        st.write("**Trabajo por Mes**")
        meses_stats = df.groupby(['mes', 'mes_numero']).agg({
            'duracion_horas': ['count', 'mean', 'sum']
        }).round(2)
        
        meses_stats.columns = ['Número_Registros', 'Promedio_Horas', 'Total_Horas']
        meses_stats = meses_stats.reset_index()
        meses_stats = meses_stats.sort_values('mes_numero')
        meses_stats = meses_stats.drop('mes_numero', axis=1)
        
        st.dataframe(meses_stats, use_container_width=True, hide_index=True)


def mostrar_analisis_areas(df):
    """Análisis por áreas si existe la columna"""
    if 'area' in df.columns and df['area'].notna().any():
        st.subheader("🏢 Análisis por Área")
        
        with st.expander("🏗️ ¿Cómo comparar el rendimiento por áreas?", expanded=False):
            st.markdown("""
            ### 🏢 **Métricas Departamentales**
            
            - **📊 Número de Registros**: Actividad total registrada por área
            - **⏱️ Promedio Horas**: Duración promedio de jornadas en cada área
            - **🏆 Total Horas**: Suma completa de horas trabajadas por departamento
            - **👥 Empleados Únicos**: Cantidad de personas diferentes por área
            
            ### 🎯 **Comparaciones Útiles**
            - **Productividad relativa**: ¿Qué áreas trabajan más horas?
            - **Eficiencia por empleado**: Ratio horas/persona por área
            - **Carga de trabajo**: Distribución del esfuerzo organizacional
            - **Tamaño vs. producción**: Áreas grandes vs. productivas
            
            ### 💡 **Decisiones que puedes tomar:**
            - **Reasignar recursos** entre áreas según necesidades
            - **Balancear cargas** de trabajo interdepartamentales
            - **Identificar áreas** que necesitan más personal
            - **Reconocer departamentos** de alto rendimiento
            """)
            
        st.write("**Comparación de productividad y actividad entre diferentes áreas de trabajo**")
        
        areas_stats = df.groupby('area').agg({
            'duracion_horas': ['count', 'mean', 'sum'],
            'nombre': 'nunique'
        }).round(2)
        
        areas_stats.columns = ['Número_Registros', 'Promedio_Horas', 'Total_Horas', 'Empleados_Únicos']
        areas_stats = areas_stats.reset_index()
        
        st.dataframe(areas_stats, use_container_width=True, hide_index=True)


def mostrar_analisis_roles(df):
    """Análisis por roles si existe la columna"""
    if 'rol' in df.columns and df['rol'].notna().any():
        st.subheader("👔 Análisis por Rol")
        
        with st.expander("👨‍💼 ¿Qué diferencias hay entre roles?", expanded=False):
            st.markdown("""
            ### 🎭 **Análisis por Posición Laboral**
            
            **📊 Métricas por Rol:**
            - **📈 Número de Registros**: Frecuencia de trabajo por tipo de rol
            - **⏰ Promedio Horas**: Jornada típica según la posición
            - **🏆 Total Horas**: Contribución total por tipo de rol
            - **👥 Empleados Únicos**: Cuántas personas tienen cada rol
            
            ### 🔍 **Patrones por Rol**
            - **Roles operativos vs. administrativos**: Diferencias en horarios
            - **Carga de responsabilidad**: ¿Los supervisores trabajan más?
            - **Especialización**: Roles con jornadas específicas
            - **Distribución organizacional**: Balance entre tipos de roles
            
            ### 💼 **Insights Organizacionales:**
            - **Estructura jerárquica**: Cómo se distribuye el trabajo
            - **Necesidades de contratación**: Roles con poca representación
            - **Equidad laboral**: Distribución justa de cargas de trabajo
            - **Planificación de carrera**: Progresión entre roles
            """)
            
        st.write("**Análisis comparativo del rendimiento y patrones de trabajo según el rol o posición**")
        
        roles_stats = df.groupby('rol').agg({
            'duracion_horas': ['count', 'mean', 'sum'],
            'nombre': 'nunique'
        }).round(2)
        
        roles_stats.columns = ['Número_Registros', 'Promedio_Horas', 'Total_Horas', 'Empleados_Únicos']
        roles_stats = roles_stats.reset_index()
        
        st.dataframe(roles_stats, use_container_width=True, hide_index=True)


def mostrar_datos_detallados(df):
    """Mostrar tabla de datos detallados con filtros"""
    st.subheader("🔍 Datos Detallados")
    
    with st.expander("🔧 ¿Cómo usar los filtros de datos?", expanded=False):
        st.markdown("""
        ### 🎛️ **Sistema de Filtros Interactivos**
        
        **👤 Filtro por Empleado:**
        - Selecciona **"Todos"** para ver todos los empleados
        - Escoge un **empleado específico** para análisis individual
        - Útil para **evaluaciones de desempeño** o seguimiento personal
        
        **📅 Filtro por Rango de Fechas:**
        - Define el **período específico** que quieres analizar
        - Arrastra los controles para **ajustar fechas** de inicio y fin
        - Perfect para análisis de **períodos específicos** o comparaciones temporales
        
        ### 🎯 **¿Cómo aprovechar esta tabla?**
        - **Verificar datos individuales**: Revisar registros específicos
        - **Detectar inconsistencias**: Identificar horarios inusuales
        - **Análisis de casos**: Estudiar empleados o períodos específicos
        - **Validación de información**: Confirmar datos antes de tomar decisiones
        
        ### 💡 **Tips de uso:**
        - Combina **múltiples filtros** para análisis más precisos
        - La tabla se **actualiza automáticamente** al cambiar filtros
        - Usa el **contador de registros** para evaluar el tamaño de la muestra
        """)
    
    st.write("**Tabla completa de registros con filtros interactivos para análisis detallado**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro por empleado
        empleados = ['Todos'] + sorted(df['nombre'].unique().tolist())
        empleado_seleccionado = st.selectbox("Filtrar por Empleado:", empleados)
    
    with col2:
        # Filtro por rango de fechas
        fecha_min = df['fecha'].min().date()
        fecha_max = df['fecha'].max().date()
        fecha_inicio, fecha_fin = st.date_input(
            "Rango de Fechas:",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if empleado_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['nombre'] == empleado_seleccionado]
    
    df_filtrado = df_filtrado[
        (df_filtrado['fecha'].dt.date >= fecha_inicio) & 
        (df_filtrado['fecha'].dt.date <= fecha_fin)
    ]
    
    # Mostrar datos filtrados
    st.write(f"**Mostrando {len(df_filtrado)} registros de {len(df)} totales**")
    
    # Seleccionar columnas a mostrar
    columnas_mostrar = ['nombre', 'fecha', 'hora_entrada', 'hora_salida', 'duracion_horas', 'dia_semana_es']
    if 'area' in df.columns:
        columnas_mostrar.append('area')
    if 'rol' in df.columns:
        columnas_mostrar.append('rol')
    
    df_mostrar = df_filtrado[columnas_mostrar].copy()
    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%Y-%m-%d')
    df_mostrar['duracion_horas'] = df_mostrar['duracion_horas'].round(2)
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)


def mostrar_resumen_ejecutivo(df):
    """Mostrar resumen ejecutivo con insights clave"""
    st.subheader("📋 Resumen Ejecutivo")
    
    with st.expander("💼 ¿Qué es el Resumen Ejecutivo?", expanded=False):
        st.markdown("""
        ### 🎯 **Síntesis de Hallazgos Clave**
        
        El **resumen ejecutivo** condensa los insights más importantes del análisis
        en información **accionable** para la toma de decisiones gerenciales.
        
        ### 📊 **Incluye:**
        - **Métricas principales** del período analizado
        - **Identificación de patrones** críticos
        - **Recomendaciones** basadas en datos
        - **Alertas** sobre situaciones que requieren atención
        - **Oportunidades** de mejora organizacional
        """)
    
    # Calcular métricas clave
    total_empleados = df['nombre'].nunique()
    total_registros = len(df)
    promedio_horas = df['duracion_horas'].mean()
    total_horas_periodo = df['duracion_horas'].sum()
    
    # Métricas en cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Empleados Activos", 
            total_empleados,
            help="Número total de empleados con registros"
        )
    
    with col2:
        st.metric(
            "📝 Total Registros", 
            total_registros,
            help="Total de entradas de horarios procesadas"
        )
    
    with col3:
        st.metric(
            "⏱️ Promedio Horas/Día", 
            f"{promedio_horas:.1f}",
            help="Duración promedio de jornada laboral"
        )
    
    with col4:
        st.metric(
            "🏆 Total Horas Período", 
            f"{total_horas_periodo:.0f}",
            help="Suma total de horas trabajadas"
        )
    
    # Insights automáticos
    st.write("### 🔍 **Insights Clave del Análisis**")
    
    # Análisis de productividad
    horas_optimas = (promedio_horas >= 7.5) and (promedio_horas <= 9)
    variabilidad = df['duracion_horas'].std()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**⚡ Productividad General**")
        if horas_optimas:
            st.success("✅ Promedio de horas en rango óptimo (7.5-9h)")
        elif promedio_horas < 7.5:
            st.warning("⚠️ Promedio de horas por debajo del estándar")
        else:
            st.info("📈 Promedio de horas por encima del estándar")
            
        if variabilidad < 1.5:
            st.success("✅ Horarios muy consistentes entre empleados")
        elif variabilidad < 2.5:
            st.info("📊 Variabilidad moderada en horarios")
        else:
            st.warning("⚠️ Alta variabilidad - revisar inconsistencias")
    
    with col2:
        st.write("**📊 Cobertura de Datos**")
        
        # Análisis de cobertura temporal
        rango_fechas = (df['fecha'].max() - df['fecha'].min()).days + 1
        dias_unicos = df['fecha'].nunique()
        cobertura = (dias_unicos / rango_fechas) * 100
        
        if cobertura > 80:
            st.success(f"✅ Excelente cobertura de datos ({cobertura:.1f}%)")
        elif cobertura > 60:
            st.info(f"📊 Buena cobertura de datos ({cobertura:.1f}%)")
        else:
            st.warning(f"⚠️ Cobertura limitada ({cobertura:.1f}%) - faltan datos")
        
        # Análisis de empleados
        registros_por_empleado = total_registros / total_empleados
        if registros_por_empleado > 10:
            st.success(f"✅ Buen historial por empleado ({registros_por_empleado:.1f} reg/persona)")
        else:
            st.info(f"📊 Datos limitados por empleado ({registros_por_empleado:.1f} reg/persona)")
    
    # Recomendaciones automáticas
    st.write("### 💡 **Recomendaciones Basadas en Datos**")
    
    recomendaciones = []
    
    if promedio_horas > 9:
        recomendaciones.append("🔄 **Revisar carga de trabajo** - El promedio de horas es alto, considerar redistribución")
    
    if variabilidad > 2:
        recomendaciones.append("📏 **Estandarizar horarios** - Alta variabilidad sugiere falta de políticas claras")
    
    if cobertura < 70:
        recomendaciones.append("📊 **Mejorar registro de datos** - Cobertura insuficiente para análisis precisos")
    
    # Análisis por día de la semana si hay datos suficientes
    if df['dia_semana_es'].nunique() >= 5:
        dias_stats = df.groupby('dia_semana_es')['duracion_horas'].sum()
        if dias_stats.std() > dias_stats.mean() * 0.3:
            recomendaciones.append("📅 **Balancear carga semanal** - Distribución desigual entre días")
    
    if not recomendaciones:
        st.success("🎉 **¡Excelente!** No se detectaron áreas críticas de mejora en los datos actuales")
    else:
        for i, rec in enumerate(recomendaciones, 1):
            st.write(f"{i}. {rec}")
    
    # Próximos pasos sugeridos
    st.write("### 🎯 **Próximos Pasos Sugeridos**")
    
    pasos = [
        "🔍 **Análisis profundo** de empleados con patrones atípicos",
        "📈 **Seguimiento temporal** para identificar tendencias",
        "🏢 **Comparación entre áreas** para optimización de recursos",
        "📋 **Implementar KPIs** basados en estos hallazgos",
        "🔄 **Revisión periódica** de estos indicadores"
    ]
    
    for paso in pasos:
        st.write(f"• {paso}")


def mostrar_exploracion_datos():
    """Función principal para mostrar la exploración de datos"""
    st.title("📊 Exploración de Datos - Horarios Laborales")
    
    # Información sobre la aplicación de exploración de datos
    with st.expander("ℹ️ ¿Qué es la Exploración de Datos?", expanded=False):
        st.markdown("""
        ### 🎯 **Propósito del Análisis Exploratorio**
        La **exploración de datos** es el proceso de examinar y analizar conjuntos de datos para 
        descubrir patrones, identificar anomalías, verificar suposiciones y obtener insights útiles.
        
        ### 🔍 **¿Qué encontrarás en esta sección?**
        - 📈 **Estadísticas descriptivas**: Medidas centrales y de dispersión
        - 👥 **Análisis por empleado**: Rendimiento individual detallado
        - 📅 **Patrones temporales**: Tendencias por días y meses
        - 🏢 **Comparación por áreas**: Productividad departamental
        - 👔 **Análisis por roles**: Comportamientos según posición
        - 🔍 **Datos detallados**: Tabla completa con filtros avanzados
        
        ### 💡 **¿Para qué sirve?**
        - **Identificar patrones** de comportamiento laboral
        - **Detectar anomalías** en horarios de trabajo
        - **Optimizar recursos** humanos por área
        - **Tomar decisiones** basadas en datos reales
        - **Mejorar la productividad** organizacional
        """)
    
    st.write("**Análisis completo de los datos de horarios usando tablas interactivas y métricas clave**")
    
    # Cargar datos con información detallada
    with st.spinner("🔄 Cargando datos desde la API..."):
        df = cargar_datos_api()
    
    if df is not None and not df.empty:
        st.success(f"✅ **Datos cargados exitosamente**: {len(df)} registros procesados desde la API")
        
        # Información rápida sobre los datos cargados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"👥 **{df['nombre'].nunique()}** Empleados")
        with col2:
            if 'area' in df.columns:
                st.info(f"🏢 **{df['area'].nunique()}** Áreas")
            else:
                st.info("🏢 **Áreas**: N/A")
        with col3:
            if 'rol' in df.columns:
                st.info(f"🎭 **{df['rol'].nunique()}** Roles")
            else:
                st.info("🎭 **Roles**: N/A")
        with col4:
            fecha_range = f"{df['fecha'].min().strftime('%d/%m/%Y')} - {df['fecha'].max().strftime('%d/%m/%Y')}"
            st.info(f"📅 **Período**: {fecha_range}")
        
        st.divider()
    
    if df is not None and not df.empty:
        # Mostrar diferentes secciones de análisis
        mostrar_resumen_general(df)
        
        st.divider()
        mostrar_estadisticas_basicas(df)
        
        st.divider()
        mostrar_analisis_empleados(df)
        
        st.divider()
        mostrar_analisis_temporal(df)
        
        st.divider()
        mostrar_analisis_areas(df)
        
        st.divider()
        mostrar_analisis_roles(df)
        
        st.divider()
        mostrar_datos_detallados(df)
        
        # Sección de resumen ejecutivo
        st.divider()
        mostrar_resumen_ejecutivo(df)
        
    else:
        st.error("No se pudieron cargar los datos o no hay datos disponibles.")


if __name__ == "__main__":
    mostrar_exploracion_datos()