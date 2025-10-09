import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats


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
            df['semana'] = df['fecha'].dt.isocalendar().week
            df['hora_entrada_num'] = df['hora_entrada_dt'].dt.hour + df['hora_entrada_dt'].dt.minute/60
            df['hora_salida_num'] = df['hora_salida_dt'].dt.hour + df['hora_salida_dt'].dt.minute/60
            
            # Categorizar productividad
            df['categoria_productividad'] = pd.cut(
                df['duracion_horas'], 
                bins=[0, 7, 10, float('inf')], 
                labels=['Baja (<7h)', 'Normal (7-10h)', 'Alta (>10h)']
            )
            
            return df
        else:
            st.error(f"Error en la petición: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error al cargar datos de la API: {e}")
        return None


def mostrar_estadisticas_descriptivas(df):
    """Mostrar estadísticas descriptivas completas"""
    st.subheader("📈 Estadísticas Descriptivas")
    
    with st.expander("🔍 ¿Qué nos dicen las estadísticas descriptivas?", expanded=False):
        st.markdown("""
        Las **estadísticas descriptivas** nos ayudan a entender la distribución y comportamiento 
        de nuestros datos de horarios laborales:
        
        - **Media**: Valor promedio de horas trabajadas
        - **Mediana**: Valor central que divide los datos en dos mitades iguales
        - **Desviación estándar**: Mide la variabilidad de las horas trabajadas
        - **Percentiles**: Nos indican cómo se distribuyen los valores
        - **Coeficiente de variación**: Compara la variabilidad entre diferentes grupos
        """)
    
    if 'duracion_horas' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🕐 Análisis de Horas Trabajadas**")
            stats_horas = df['duracion_horas'].describe()
            
            # Crear un DataFrame más legible
            stats_df = pd.DataFrame({
                'Métrica': ['Conteo', 'Promedio', 'Desv. Estándar', 'Mínimo', '25%', '50% (Mediana)', '75%', 'Máximo'],
                'Valor': [
                    f"{stats_horas['count']:.0f} registros",
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
        
        with col2:
            st.write("**📊 Métricas Adicionales**")
            # Calcular métricas adicionales
            cv = (df['duracion_horas'].std() / df['duracion_horas'].mean()) * 100
            rango_iqr = df['duracion_horas'].quantile(0.75) - df['duracion_horas'].quantile(0.25)
            
            metricas_adicionales = pd.DataFrame({
                'Métrica': [
                    'Coef. Variación', 
                    'Rango IQR', 
                    'Asimetría (Skewness)',
                    'Curtosis',
                    'Empleados únicos',
                    'Días únicos'
                ],
                'Valor': [
                    f"{cv:.2f}%",
                    f"{rango_iqr:.2f} horas",
                    f"{df['duracion_horas'].skew():.2f}",
                    f"{df['duracion_horas'].kurtosis():.2f}",
                    f"{df['nombre'].nunique()} personas",
                    f"{df['fecha'].nunique()} días"
                ]
            })
            st.dataframe(metricas_adicionales, use_container_width=True, hide_index=True)


def mostrar_analisis_temporal(df_filtrado):
    """Análisis temporal detallado"""
    st.subheader("⏰ Análisis Temporal Avanzado")
    
    with st.expander("📅 Importancia del análisis temporal", expanded=False):
        st.markdown("""
        El **análisis temporal** nos permite identificar:
        - **Patrones estacionales**: ¿Hay días más productivos?
        - **Tendencias**: ¿Está aumentando o disminuyendo la productividad?
        - **Ciclos**: ¿Existen patrones repetitivos?
        - **Anomalías**: ¿Hay días o períodos inusuales?
        """)
    
    # Análisis por día de la semana
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Por Día Semana", "📈 Tendencias", "🔄 Patrones Horarios", "📉 Análisis Series"])
    
    with tab1:
        st.write("**Productividad por Día de la Semana**")
        
        # Análisis estadístico por día
        dias_stats = df_filtrado.groupby('dia_semana_es')['duracion_horas'].agg([
            'count', 'mean', 'std', 'median', 'min', 'max'
        ]).round(2)
        
        # Reordenar días de la semana
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dias_stats = dias_stats.reindex([d for d in orden_dias if d in dias_stats.index])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras con error bars
            fig_dias = go.Figure()
            
            fig_dias.add_trace(go.Bar(
                x=dias_stats.index,
                y=dias_stats['mean'],
                error_y=dict(type='data', array=dias_stats['std']),
                marker_color='skyblue',
                name='Promedio ± Desv. Std'
            ))
            
            fig_dias.update_layout(
                title="Horas Promedio por Día (con Desviación Estándar)",
                xaxis_title="Día de la Semana",
                yaxis_title="Horas Trabajadas",
                showlegend=False
            )
            
            st.plotly_chart(fig_dias, use_container_width=True)
        
        with col2:
            # Box plot para ver distribuciones
            fig_box = px.box(
                df_filtrado, 
                x='dia_semana_es', 
                y='duracion_horas',
                title="Distribución de Horas por Día",
                category_orders={'dia_semana_es': orden_dias}
            )
            fig_box.update_layout(xaxis_title="Día de la Semana", yaxis_title="Horas")
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Tabla resumen
        st.write("**Estadísticas Detalladas por Día**")
        dias_stats.columns = ['Registros', 'Promedio', 'Desv.Std', 'Mediana', 'Mínimo', 'Máximo']
        st.dataframe(dias_stats, use_container_width=True)
        
        # Insights automáticos
        mejor_dia = dias_stats['Promedio'].idxmax()
        peor_dia = dias_stats['Promedio'].idxmin()
        st.info(f"💡 **Insight**: {mejor_dia} es el día más productivo ({dias_stats.loc[mejor_dia, 'Promedio']:.2f}h promedio), mientras que {peor_dia} es el menos productivo ({dias_stats.loc[peor_dia, 'Promedio']:.2f}h promedio).")
    
    with tab2:
        st.write("**Tendencias Temporales**")
        
        # Serie temporal de productividad diaria
        serie_diaria = df_filtrado.groupby('fecha').agg({
            'duracion_horas': ['sum', 'mean', 'count'],
            'nombre': 'nunique'
        }).round(2)
        
        serie_diaria.columns = ['Total_Horas', 'Promedio_Horas', 'Num_Registros', 'Empleados_Unicos']
        serie_diaria = serie_diaria.reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tendencia de horas totales
            fig_trend = px.line(
                serie_diaria, 
                x='fecha', 
                y='Total_Horas',
                title="Evolución de Horas Totales Diarias",
                markers=True
            )
            fig_trend.update_layout(xaxis_title="Fecha", yaxis_title="Horas Totales")
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Tendencia de empleados únicos
            fig_emp = px.line(
                serie_diaria, 
                x='fecha', 
                y='Empleados_Unicos',
                title="Empleados Activos por Día",
                markers=True,
                color_discrete_sequence=['orange']
            )
            fig_emp.update_layout(xaxis_title="Fecha", yaxis_title="Número de Empleados")
            st.plotly_chart(fig_emp, use_container_width=True)
        
        # Correlación entre variables
        if len(serie_diaria) > 1:
            correlacion = serie_diaria[['Total_Horas', 'Promedio_Horas', 'Empleados_Unicos']].corr()
            
            fig_corr = px.imshow(
                correlacion,
                text_auto=True,
                aspect="auto",
                title="Matriz de Correlación - Variables Temporales"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab3:
        st.write("**Patrones de Horarios de Entrada y Salida**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histograma de horas de entrada
            fig_entrada = px.histogram(
                df_filtrado, 
                x='hora_entrada_num', 
                nbins=24,
                title="Distribución de Horas de Entrada",
                labels={'hora_entrada_num': 'Hora de Entrada', 'count': 'Frecuencia'}
            )
            fig_entrada.update_layout(bargap=0.1)
            st.plotly_chart(fig_entrada, use_container_width=True)
        
        with col2:
            # Histograma de horas de salida
            fig_salida = px.histogram(
                df_filtrado, 
                x='hora_salida_num', 
                nbins=24,
                title="Distribución de Horas de Salida",
                labels={'hora_salida_num': 'Hora de Salida', 'count': 'Frecuencia'},
                color_discrete_sequence=['orange']
            )
            fig_salida.update_layout(bargap=0.1)
            st.plotly_chart(fig_salida, use_container_width=True)
        
        # Scatter plot: relación entre hora de entrada y duración
        fig_scatter = px.scatter(
            df_filtrado, 
            x='hora_entrada_num', 
            y='duracion_horas',
            color='area',
            title="Relación: Hora de Entrada vs Duración de Jornada",
            labels={'hora_entrada_num': 'Hora de Entrada', 'duracion_horas': 'Duración (horas)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.write("**Análisis de Series Temporales**")
        
        if len(serie_diaria) > 7:  # Solo si tenemos suficientes datos
            # Descomposición de tendencia (simplificada)
            serie_diaria_sorted = serie_diaria.sort_values('fecha')
            
            # Calcular media móvil
            window = min(7, len(serie_diaria) // 3)
            if window >= 2:
                serie_diaria_sorted['Media_Movil'] = serie_diaria_sorted['Total_Horas'].rolling(window=window).mean()
                
                fig_ma = go.Figure()
                fig_ma.add_trace(go.Scatter(
                    x=serie_diaria_sorted['fecha'],
                    y=serie_diaria_sorted['Total_Horas'],
                    mode='lines+markers',
                    name='Datos Originales',
                    line=dict(color='lightblue')
                ))
                fig_ma.add_trace(go.Scatter(
                    x=serie_diaria_sorted['fecha'],
                    y=serie_diaria_sorted['Media_Movil'],
                    mode='lines',
                    name=f'Media Móvil ({window} días)',
                    line=dict(color='red', width=2)
                ))
                
                fig_ma.update_layout(
                    title=f"Tendencia con Media Móvil ({window} días)",
                    xaxis_title="Fecha",
                    yaxis_title="Horas Totales"
                )
                st.plotly_chart(fig_ma, use_container_width=True)
        else:
            st.info("📊 Se necesitan más datos para realizar análisis de series temporales avanzado.")


def mostrar_analisis_por_grupos(df_filtrado):
    """Análisis segmentado por diferentes grupos"""
    st.subheader("👥 Análisis Segmentado")
    
    with st.expander("🔬 Análisis por grupos - ¿Por qué es importante?", expanded=False):
        st.markdown("""
        El **análisis por grupos** nos permite:
        - **Comparar performance**: Entre diferentes áreas, roles, empleados
        - **Identificar outliers**: Empleados o áreas con comportamientos únicos
        - **Optimizar recursos**: Entender dónde se concentra la productividad
        - **Detectar inequidades**: Diferencias significativas entre grupos
        """)
    
    tab1, tab2, tab3 = st.tabs(["🏢 Por Área", "🎭 Por Rol", "👤 Por Empleado"])
    
    with tab1:
        st.write("**Análisis Detallado por Área de Trabajo**")
        
        # Estadísticas por área
        area_stats = df_filtrado.groupby('area').agg({
            'duracion_horas': ['count', 'mean', 'std', 'median', 'sum'],
            'nombre': 'nunique',
            'fecha': 'nunique'
        }).round(2)
        
        area_stats.columns = ['Registros', 'Prom_Horas', 'Desv_Std', 'Mediana', 'Total_Horas', 'Empleados', 'Días_Activos']
        area_stats = area_stats.sort_values('Total_Horas', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras comparativo
            fig_area = px.bar(
                area_stats.reset_index(),
                x='area',
                y='Prom_Horas',
                color='Total_Horas',
                title="Productividad Promedio por Área",
                color_continuous_scale='Viridis'
            )
            fig_area.update_layout(xaxis_title="Área", yaxis_title="Horas Promedio")
            st.plotly_chart(fig_area, use_container_width=True)
        
        with col2:
            # Box plot por área
            fig_box_area = px.box(
                df_filtrado,
                x='area',
                y='duracion_horas',
                title="Distribución de Horas por Área"
            )
            fig_box_area.update_layout(xaxis_title="Área", yaxis_title="Horas Trabajadas")
            st.plotly_chart(fig_box_area, use_container_width=True)
        
        # Tabla detallada
        st.write("**Estadísticas Completas por Área**")
        st.dataframe(area_stats, use_container_width=True)
        
        # ANOVA si hay múltiples áreas
        if len(area_stats) > 1:
            grupos_area = [df_filtrado[df_filtrado['area'] == area]['duracion_horas'].values 
                          for area in df_filtrado['area'].unique()]
            
            try:
                f_stat, p_value = stats.f_oneway(*grupos_area)
                if p_value < 0.05:
                    st.success(f"🔬 **Análisis ANOVA**: Existen diferencias estadísticamente significativas entre áreas (p-value: {p_value:.4f})")
                else:
                    st.info(f"📊 **Análisis ANOVA**: No hay diferencias estadísticamente significativas entre áreas (p-value: {p_value:.4f})")
            except:
                st.info("No se pudo realizar el análisis ANOVA")
    
    with tab2:
        st.write("**Análisis por Rol/Posición**")
        
        # Estadísticas por rol
        rol_stats = df_filtrado.groupby('rol').agg({
            'duracion_horas': ['count', 'mean', 'std', 'median'],
            'nombre': 'nunique'
        }).round(2)
        
        rol_stats.columns = ['Registros', 'Prom_Horas', 'Desv_Std', 'Mediana', 'Empleados']
        rol_stats = rol_stats.sort_values('Prom_Horas', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico radial para roles
            fig_radar = go.Figure()
            
            for i, (rol, stats) in enumerate(rol_stats.iterrows()):
                fig_radar.add_trace(go.Scatterpolar(
                    r=[stats['Prom_Horas'], stats['Registros']/10, stats['Empleados']*2, stats['Mediana']],
                    theta=['Promedio Horas', 'Registros (÷10)', 'Empleados (×2)', 'Mediana Horas'],
                    fill='toself',
                    name=rol
                ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max(rol_stats['Prom_Horas'].max(), 20)])),
                showlegend=True,
                title="Perfil Multidimensional por Rol"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Gráfico de barras horizontales
            fig_rol = px.bar(
                rol_stats.reset_index().sort_values('Prom_Horas'),
                x='Prom_Horas',
                y='rol',
                orientation='h',
                title="Horas Promedio por Rol",
                color='Prom_Horas',
                color_continuous_scale='Blues'
            )
            fig_rol.update_layout(yaxis_title="Rol", xaxis_title="Horas Promedio")
            st.plotly_chart(fig_rol, use_container_width=True)
        
        st.dataframe(rol_stats, use_container_width=True)
    
    with tab3:
        st.write("**Análisis Individual por Empleado**")
        
        # Top performers
        empleado_stats = df_filtrado.groupby('nombre').agg({
            'duracion_horas': ['count', 'mean', 'std', 'sum'],
            'fecha': 'nunique',
            'area': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A',
            'rol': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A'
        }).round(2)
        
        empleado_stats.columns = ['Registros', 'Prom_Horas', 'Desv_Std', 'Total_Horas', 'Días_Trabajados', 'Área_Principal', 'Rol_Principal']
        empleado_stats = empleado_stats.sort_values('Total_Horas', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 empleados por horas totales
            top_10 = empleado_stats.head(10)
            fig_top = px.bar(
                top_10.reset_index(),
                x='Total_Horas',
                y='nombre',
                orientation='h',
                title="Top 10: Empleados por Horas Totales",
                color='Prom_Horas',
                color_continuous_scale='Greens'
            )
            fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col2:
            # Distribución de consistencia (coeficiente de variación)
            empleado_stats['CV'] = (empleado_stats['Desv_Std'] / empleado_stats['Prom_Horas']) * 100
            
            fig_cv = px.histogram(
                empleado_stats,
                x='CV',
                nbins=15,
                title="Distribución de Consistencia (Coef. Variación)",
                labels={'CV': 'Coeficiente de Variación (%)', 'count': 'Número de Empleados'}
            )
            st.plotly_chart(fig_cv, use_container_width=True)
        
        # Ranking completo (primeros 20)
        st.write("**Ranking de Empleados (Top 20)**")
        ranking = empleado_stats.head(20).copy()
        ranking.index.name = 'Empleado'
        st.dataframe(ranking, use_container_width=True)
        
        # Empleados más consistentes (menor CV)
        if len(empleado_stats) > 1:
            consistentes = empleado_stats[empleado_stats['Registros'] >= 3].nsmallest(5, 'CV')
            if len(consistentes) > 0:
                st.success(f"🎯 **Empleados más consistentes**: {', '.join(consistentes.index.tolist())}")


def mostrar_analisis_correlacion(df_filtrado):
    """Análisis de correlaciones y relaciones entre variables"""
    st.subheader("🔗 Análisis de Correlaciones")
    
    with st.expander("📊 Interpretación de correlaciones", expanded=False):
        st.markdown("""
        Las **correlaciones** miden la relación lineal entre variables:
        
        - **+1.0**: Correlación positiva perfecta
        - **+0.7 a +0.9**: Correlación fuerte positiva  
        - **+0.3 a +0.7**: Correlación moderada positiva
        - **-0.3 a +0.3**: Correlación débil o nula
        - **-0.3 a -0.7**: Correlación moderada negativa
        - **-0.7 a -0.9**: Correlación fuerte negativa
        - **-1.0**: Correlación negativa perfecta
        """)
    
    # Preparar variables numéricas para correlación
    variables_numericas = ['duracion_horas', 'hora_entrada_num', 'hora_salida_num']
    
    # Agregar variables derivadas por empleado
    empleado_metricas = df_filtrado.groupby('nombre').agg({
        'duracion_horas': ['mean', 'std', 'count'],
        'hora_entrada_num': 'mean',
        'hora_salida_num': 'mean',
        'fecha': 'nunique'
    }).round(3)
    
    empleado_metricas.columns = ['Prom_Duración', 'Std_Duración', 'Num_Registros', 'Prom_Entrada', 'Prom_Salida', 'Días_Únicos']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Matriz de correlación de variables básicas
        if len(df_filtrado) > 1:
            corr_basic = df_filtrado[variables_numericas].corr()
            
            fig_corr1 = px.imshow(
                corr_basic,
                text_auto='.3f',
                aspect="auto",
                title="Correlación: Variables de Horarios",
                color_continuous_scale='RdBu_r'
            )
            st.plotly_chart(fig_corr1, use_container_width=True)
    
    with col2:
        # Matriz de correlación de métricas por empleado
        if len(empleado_metricas) > 1:
            corr_emp = empleado_metricas.corr()
            
            fig_corr2 = px.imshow(
                corr_emp,
                text_auto='.3f',
                aspect="auto", 
                title="Correlación: Métricas por Empleado",
                color_continuous_scale='RdBu_r'
            )
            st.plotly_chart(fig_corr2, use_container_width=True)
    
    # Análisis de correlaciones específicas
    st.write("**Análisis de Relaciones Específicas**")
    
    tab1, tab2 = st.tabs(["📈 Scatter Plots", "🔍 Análisis Estadístico"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Relación: Hora entrada vs Duración
            fig_scatter1 = px.scatter(
                df_filtrado,
                x='hora_entrada_num',
                y='duracion_horas',
                color='area',
                size='duracion_horas',
                title="Hora de Entrada vs Duración",
                trendline="ols"
            )
            st.plotly_chart(fig_scatter1, use_container_width=True)
        
        with col2:
            # Relación: Registros vs Promedio (por empleado)
            fig_scatter2 = px.scatter(
                empleado_metricas.reset_index(),
                x='Num_Registros',
                y='Prom_Duración',
                color='Std_Duración',
                title="Registros vs Duración Promedio (por empleado)",
                hover_name='nombre'
            )
            st.plotly_chart(fig_scatter2, use_container_width=True)
    
    with tab2:
        # Análisis estadístico de correlaciones importantes
        if len(df_filtrado) > 2:
            # Correlación entrada-duración
            corr_entrada_duracion = df_filtrado['hora_entrada_num'].corr(df_filtrado['duracion_horas'])
            
            # Test de significancia
            from scipy.stats import pearsonr
            try:
                corr_coef, p_value = pearsonr(df_filtrado['hora_entrada_num'], df_filtrado['duracion_horas'])
                
                st.write("**🔬 Análisis Estadístico de Correlaciones**")
                
                resultados = pd.DataFrame({
                    'Relación': [
                        'Hora Entrada ↔ Duración',
                        'Hora Entrada ↔ Hora Salida', 
                        'Significancia Estadística'
                    ],
                    'Coeficiente': [
                        f"{corr_entrada_duracion:.3f}",
                        f"{df_filtrado['hora_entrada_num'].corr(df_filtrado['hora_salida_num']):.3f}",
                        f"p-value: {p_value:.4f}"
                    ],
                    'Interpretación': [
                        'Moderada negativa' if corr_entrada_duracion < -0.3 else 'Débil' if abs(corr_entrada_duracion) < 0.3 else 'Moderada positiva',
                        'Fuerte positiva' if df_filtrado['hora_entrada_num'].corr(df_filtrado['hora_salida_num']) > 0.7 else 'Moderada',
                        'Significativa' if p_value < 0.05 else 'No significativa'
                    ]
                })
                
                st.dataframe(resultados, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.info("No se pudo realizar el análisis de significancia estadística")


def mostrar_exploracion_datos():
    """Función principal que muestra toda la exploración de datos"""
    st.sidebar.info("🔬 Realiza un análisis exhaustivo de los datos de horarios laborales con herramientas estadísticas avanzadas.")
    
    try:
        # Cargar datos
        datos = cargar_datos_api()
        
        if datos is None or datos.empty:
            st.error("❌ No se pudieron cargar los datos de la API o no hay datos disponibles.")
            return
        
        # Título principal
        st.title("🔬 Exploración Avanzada de Datos")
        st.markdown("### 📊 Análisis Estadístico Completo de Horarios Laborales")
        
        # Descripción del módulo
        with st.expander("🎯 ¿Qué hace este módulo de exploración?", expanded=True):
            st.markdown("""
            Este módulo realiza un **análisis estadístico completo** de los datos de horarios laborales:
            
            #### 🔍 **Análisis Incluidos:**
            - **📈 Estadísticas Descriptivas**: Medidas de tendencia central, dispersión y distribución
            - **⏰ Análisis Temporal**: Patrones por días, tendencias, estacionalidad
            - **👥 Segmentación**: Comparación entre áreas, roles y empleados individuales
            - **🔗 Correlaciones**: Relaciones entre variables y su significancia estadística
            - **📊 Visualizaciones Avanzadas**: Gráficos interactivos y dashboards
            
            #### 🎯 **Objetivos:**
            - Identificar patrones ocultos en los datos
            - Detectar anomalías y outliers
            - Optimizar la gestión de recursos humanos
            - Proporcionar insights basados en evidencia estadística
            """)
        
        # Información general de los datos
        st.success(f"✅ **Datos cargados correctamente**: {len(datos):,} registros desde la API")
        
        # Métricas principales
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("👥 Empleados", f"{datos['nombre'].nunique()}")
        with col2:
            st.metric("🏢 Áreas", f"{datos['area'].nunique()}")  
        with col3:
            st.metric("🎭 Roles", f"{datos['rol'].nunique()}")
        with col4:
            st.metric("📅 Días", f"{datos['fecha'].nunique()}")
        with col5:
            if 'duracion_horas' in datos.columns:
                st.metric("⏱️ Prom. Horas", f"{datos['duracion_horas'].mean():.1f}h")
        
        st.divider()
        
        # === PANEL DE FILTROS AVANZADOS ===
        st.sidebar.markdown("## 🎛️ **Panel de Control Avanzado**")
        st.sidebar.markdown("*Personaliza tu análisis con filtros inteligentes*")
        
        # Filtros básicos
        st.sidebar.markdown("### 🔍 **Filtros Básicos**")
        
        nombres = datos['nombre'].unique()
        nombre_sel = st.sidebar.selectbox(
            "👤 Empleado", 
            options=['Todos'] + list(nombres),
            help="Analizar empleado específico"
        )
        
        areas = datos['area'].unique()
        areas_sel = st.sidebar.multiselect(
            "🏢 Área(s)", 
            options=areas, 
            default=list(areas),
            help="Seleccionar áreas a comparar"
        )
        
        roles = datos['rol'].unique()
        roles_sel = st.sidebar.multiselect(
            "🎭 Rol(es)", 
            options=roles, 
            default=list(roles),
            help="Filtrar por tipos de trabajo"
        )
        
        # Filtros temporales avanzados
        st.sidebar.markdown("### 📅 **Filtros Temporales**")
        
        fecha_min = datos['fecha'].min().date()
        fecha_max = datos['fecha'].max().date()
        fecha_inicio, fecha_fin = st.sidebar.date_input(
            "📅 Período de análisis",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )
        
        # Filtro por productividad
        nivel_productividad = st.sidebar.selectbox(
            "⚡ Nivel de productividad",
            options=['Todos', 'Alta (>10h)', 'Normal (7-10h)', 'Baja (<7h)'],
            help="Segmentar por niveles de rendimiento"
        )
        
        # Filtros estadísticos avanzados
        st.sidebar.markdown("### 📊 **Filtros Estadísticos**")
        
        # Filtro por percentiles
        percentil_filtro = st.sidebar.slider(
            "📈 Filtrar por percentil de horas",
            min_value=0, max_value=100,
            value=(0, 100),
            help="Excluir outliers por percentiles"
        )
        
        # Filtro de consistencia (coeficiente de variación)
        incluir_consistencia = st.sidebar.checkbox(
            "🎯 Solo empleados consistentes (CV < 30%)",
            value=False,
            help="Filtrar empleados con horarios regulares"
        )
        
        # === APLICAR FILTROS ===
        datos_filtrados = datos.copy()
        
        # Filtros básicos
        if nombre_sel != 'Todos':
            datos_filtrados = datos_filtrados[datos_filtrados['nombre'] == nombre_sel]
        if areas_sel:
            datos_filtrados = datos_filtrados[datos_filtrados['area'].isin(areas_sel)]
        if roles_sel:
            datos_filtrados = datos_filtrados[datos_filtrados['rol'].isin(roles_sel)]
        
        # Filtros temporales
        datos_filtrados = datos_filtrados[
            (datos_filtrados['fecha'].dt.date >= fecha_inicio) &
            (datos_filtrados['fecha'].dt.date <= fecha_fin)
        ]
        
        # Filtro por productividad
        if nivel_productividad != 'Todos' and 'duracion_horas' in datos_filtrados.columns:
            if nivel_productividad == 'Alta (>10h)':
                datos_filtrados = datos_filtrados[datos_filtrados['duracion_horas'] > 10]
            elif nivel_productividad == 'Normal (7-10h)':
                datos_filtrados = datos_filtrados[
                    (datos_filtrados['duracion_horas'] >= 7) & 
                    (datos_filtrados['duracion_horas'] <= 10)
                ]
            elif nivel_productividad == 'Baja (<7h)':
                datos_filtrados = datos_filtrados[datos_filtrados['duracion_horas'] < 7]
        
        # Filtro por percentiles
        if 'duracion_horas' in datos_filtrados.columns:
            p_min = np.percentile(datos_filtrados['duracion_horas'], percentil_filtro[0])
            p_max = np.percentile(datos_filtrados['duracion_horas'], percentil_filtro[1])
            datos_filtrados = datos_filtrados[
                (datos_filtrados['duracion_horas'] >= p_min) & 
                (datos_filtrados['duracion_horas'] <= p_max)
            ]
        
        # Filtro de consistencia
        if incluir_consistencia:
            empleados_cv = datos_filtrados.groupby('nombre')['duracion_horas'].agg(['mean', 'std']).reset_index()
            empleados_cv['cv'] = (empleados_cv['std'] / empleados_cv['mean']) * 100
            empleados_consistentes = empleados_cv[empleados_cv['cv'] < 30]['nombre'].tolist()
            datos_filtrados = datos_filtrados[datos_filtrados['nombre'].isin(empleados_consistentes)]
        
        # Mostrar resumen de filtros aplicados
        if len(datos_filtrados) != len(datos):
            st.info(f"🔍 **Filtros aplicados**: Mostrando {len(datos_filtrados):,} de {len(datos):,} registros ({(len(datos_filtrados)/len(datos)*100):.1f}%)")
        
        # Validar que hay datos suficientes
        if len(datos_filtrados) < 2:
            st.warning("⚠️ Los filtros seleccionados resultan en muy pocos datos para realizar análisis estadísticos significativos.")
            return
        
        # === ANÁLISIS COMPLETO ===
        
        # 1. Estadísticas Descriptivas
        mostrar_estadisticas_descriptivas(datos_filtrados)
        
        st.divider()
        
        # 2. Análisis Temporal
        mostrar_analisis_temporal(datos_filtrados)
        
        st.divider()
        
        # 3. Análisis por Grupos
        mostrar_analisis_por_grupos(datos_filtrados)
        
        st.divider()
        
        # 4. Análisis de Correlaciones
        mostrar_analisis_correlacion(datos_filtrados)
        
        st.divider()
        
        # === RESUMEN EJECUTIVO ===
        st.subheader("📋 Resumen Ejecutivo del Análisis")
        
        with st.expander("📊 Principales hallazgos y recomendaciones", expanded=True):
            if 'duracion_horas' in datos_filtrados.columns:
                # Calcular métricas clave
                prom_horas = datos_filtrados['duracion_horas'].mean()
                std_horas = datos_filtrados['duracion_horas'].std()
                cv_general = (std_horas / prom_horas) * 100
                
                # Identificar patrones
                mejor_area = datos_filtrados.groupby('area')['duracion_horas'].mean().idxmax()
                peor_area = datos_filtrados.groupby('area')['duracion_horas'].mean().idxmin()
                
                empleados_total = datos_filtrados['nombre'].nunique()
                registros_por_empleado = len(datos_filtrados) / empleados_total if empleados_total > 0 else 0
                
                st.markdown(f"""
                ### 🎯 **Hallazgos Principales:**
                
                **📊 Productividad General:**
                - Promedio de horas trabajadas: **{prom_horas:.2f} horas** por jornada
                - Variabilidad: **{cv_general:.1f}%** (Coeficiente de Variación)
                - Total de empleados analizados: **{empleados_total}**
                - Registros promedio por empleado: **{registros_por_empleado:.1f}**
                
                **🏢 Performance por Área:**
                - Área más productiva: **{mejor_area}**
                - Área con menor productividad: **{peor_area}**
                
                **⚡ Recomendaciones:**
                - {"Excelente consistencia en horarios" if cv_general < 15 else "Considerar estandarizar horarios" if cv_general > 25 else "Variabilidad aceptable"}
                - {"Productividad alta, mantener estrategias actuales" if prom_horas > 8.5 else "Evaluar causas de baja productividad" if prom_horas < 7 else "Productividad en rango normal"}
                - Implementar mejores prácticas de **{mejor_area}** en otras áreas
                """)
        
        # Exportar datos filtrados (opcional)
        if st.button("📥 Descargar datos filtrados (CSV)", help="Descargar los datos actuales para análisis externos"):
            csv = datos_filtrados.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv,
                file_name=f"datos_horarios_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"❌ Error durante el análisis: {e}")
        st.info("💡 Intenta ajustar los filtros o contacta al administrador del sistema.")


# Función principal para ser llamada desde la aplicación principal
def main():
    mostrar_exploracion_datos()


if __name__ == "__main__":
    main()
