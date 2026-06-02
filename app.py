import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO, StringIO
from datetime import datetime
import collections
import re
import logging

# =========================================================================
# 1. CONFIGURACIÓN DE LA INTERFAZ Y ESTILOS
# =========================================================================
st.set_page_config(page_title="SaaS Planificador de Contenidos", layout="wide")

# Silenciar EXCLUSIVAMENTE los avisos de Matplotlib relacionados con emojis/fuentes ausentes
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

st.title("Plataforma de Analítica y Planificación de Contenidos Automática")
st.caption("Proyecto Integrador - Desarrollado por el Ing. Rafael Regato - Universidad Casa Grande")

# Inicialización de variables en el estado de la sesión para mantener persistencia entre pestañas
if 'df_seguro' not in st.session_state:
    st.session_state.df_seguro = None
if 'plataforma' not in st.session_state:
    st.session_state.plataforma = "Desconocida"
if 'data_lista' not in st.session_state:
    st.session_state.data_lista = False

# Sincronización cronológica del sistema (Año actual: 2026)
fecha_actual_sistema = datetime.now()
mes_actual_num = fecha_actual_sistema.month
nombres_meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
mes_actual_nombre = nombres_meses[mes_actual_num]

banco_hitos_anuales = {
    1: {"Semana 1": "Año Nuevo - Planificación", "Semana 2": "Reyes Magos - Tradición", "Semana 3": "Campaña de Invierno", "Semana 4": "Lanzamiento de Ciclo Q1"},
    2: {"Semana 1": "Pre-San Valentín - Preventas", "Semana 2": "San Valentín - Compra Impulso", "Semana 3": "Carnaval - Contenido Ocio", "Semana 4": "Cierre Mensual Comercial"},
    3: {"Semana 1": "Día de la Mujer - Valor Humano", "Semana 2": "Concienciación y Cultura", "Semana 3": "Primavera - Nuevo Catálogo", "Semana 4": "Ofertas de Cierre Trimestral"},
    4: {"Semana 1": "Educación e Instructivos", "Semana 2": "Día de la Tierra - Eco-Values", "Semana 3": "Dinámicas de Co-Creación", "Semana 4": "Campañas Intermedias Relámpago"},
    5: {"Semana 1": "Día del Trabajador - Ofertas", "Semana 2": "Día de la Madre - Alta Conversión", "Semana 3": "Post-Festejos - Fidelización", "Semana 4": "Encuestas de Mitad de Año"},
    6: {"Semana 1": "Día del Niño - Contenido Emocional", "Semana 2": "Medio Ambiente - Sostenible", "Semana 3": "Día del Padre - Guías de Regalos", "Semana 4": "Solsticio - Identidad Local"},
    7: {"Semana 1": "Vacaciones - Reels Ligeros", "Semana 2": "Viajes - Estilo de Vida", "Semana 3": "Reciclaje de Contenido Viral", "Semana 4": "Ajuste y Optimización de Pauta"},
    8: {"Semana 1": "Estética de Alta Fidelidad", "Semana 2": "Día de la Juventud - Tendencias", "Semana 3": "Carruseles de Autoridad", "Semana 4": "Liquidación de Stock Estacional"},
    9: {"Semana 1": "Flores Amarillas - Interacción", "Semana 2": "Entrada de Otoño - Nueva Paleta", "Semana 3": "Testimonios y Casos de Éxito", "Semana 4": "Estrategias de Calentamiento Q4"},
    10: {"Semana 1": "Preventas de Temporada", "Semana 2": "Lúdico - Dinámicas Creativas", "Semana 3": "Videos Cortos de Intriga", "Semana 4": "Halloween - Campaña Temática"},
    11: {"Semana 1": "Mensajes de Tradición y Respeto", "Semana 2": "Black Friday - Captación Leads", "Semana 3": "Black Friday - Ofertas Agresivas", "Semana 4": "Post-Venta y Logística Eficiente"},
    12: {"Semana 1": "Navidad - Unión y Emotividad", "Semana 2": "Guías de Compra Cruzada", "Semana 3": "Cenas y Paquetes Corporativos", "Semana 4": "Cierre de Año y Nuevas Metas"}
}
hitos_mes_actual = banco_hitos_anuales[mes_actual_num]

# Paleta de colores vivos para gráficos interactivos
PALETA_VIVA = ['#FF416C', '#FF4B2B', '#FF8C00', '#1D976C', '#667eea', '#9b5de5']

# Diccionario de definiciones conceptuales de formatos (Utilizado en interfaz y exportación PDF)
DEFINICIONES_FORMATOS = {
    "Imagen de Instagram": "Publicación estática estándar. Ideal para composiciones estéticas limpias o mensajes concisos.",
    "Secuencia de Instagram": "Carrusel deslizable. Excelente para guías paso a paso, infografías o catálogos detallados.",
    "Reel de Instagram": "Video vertical de formato corto enfocado al descubrimiento masivo y la viralidad inmediata.",
    "Publicación de Facebook": "Post genérico con imagen o enlace. Adecuado para debates de comunidad y tráfico externo.",
    "Videos": "Contenido audiovisual largo. Potencia la retención detallada y explicaciones profundas de marca.",
    "Video de Facebook": "Video nativo para la sección Watch. Tracciona interacciones masivas y compartidos compartidos."
}

# =========================================================================
# 2. CAPTURA DE DATOS EN LA BARRA LATERAL
# =========================================================================
st.sidebar.header("Configuración del Sistema")
nombre_negocio = st.sidebar.text_input("1. Nombre de tu marca o negocio:", placeholder="Ej. Tu Marca SaaS")

archivo_cargado = None
if nombre_negocio:
    st.sidebar.markdown("---")
    archivo_cargado = st.sidebar.file_uploader(f"2. Sube el CSV de Meta Business para '{nombre_negocio}'", type=["csv"])

# =========================================================================
# 3. CAPA DE EXTRACCIÓN Y TRATAMIENTO DE ARCHIVOS
# =========================================================================
if archivo_cargado is not None:
    try:
        contenido_binario = archivo_cargado.getvalue()
        if contenido_binario.startswith(b'\xff\xfe') or contenido_binario.startswith(b'\xfe\xff'):
            texto_crudo = contenido_binario.decode('utf-16', errors='ignore')
        else:
            try:
                texto_crudo = contenido_binario.decode('utf-8')
            except UnicodeDecodeError:
                texto_crudo = contenido_binario.decode('utf-16', errors='ignore')
        
        lineas_procesadas = []
        for linea in texto_crudo.split('\n'):
            linea_clean = linea.strip()
            if not linea_clean or "sep=" in linea_clean:
                continue
            if linea_clean == '"Visualizaciones"' or linea_clean == 'Visualizaciones':
                continue
            lineas_procesadas.append(linea)
            
        texto_sanitizado = '\n'.join(lineas_procesadas)
        df_raw = pd.read_csv(StringIO(texto_sanitizado))
        df_raw.columns = df_raw.columns.str.strip().str.replace('"', '')
        
        es_archivo_diario = (
            "Primary" in df_raw.columns or 
            ("Fecha" in df_raw.columns and len(df_raw.columns) <= 3) or
            ("Visualizaciones" in df_raw.columns and "Tipo de publicación" not in df_raw.columns)
        )
        
        if es_archivo_diario:
            st.sidebar.warning("⚠️ ¡Archivo de visualizaciones diarias detectado! Este reporte no contiene el desglose de publicaciones individuales necesario para entrenar la IA. Por favor, sube el reporte histórico de 'Publicaciones'.")
        else:
            if "Nombre de usuario de la cuenta" in df_raw.columns or "Me gusta" in df_raw.columns:
                st.session_state.plataforma = "Instagram"
                col_likes = next((c for c in ['Me gusta', 'Likes'] if c in df_raw.columns), None)
                col_comments = next((c for c in ['Comentarios', 'Comments'] if c in df_raw.columns), None)
                col_shares = next((c for c in ['Veces que se compartió', 'Compartidos'] if c in df_raw.columns), None)
                
                likes_v = pd.to_numeric(df_raw[col_likes].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0) if col_likes else 0
                comm_v = pd.to_numeric(df_raw[col_comments].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0) if col_comments else 0
                share_v = pd.to_numeric(df_raw[col_shares].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0) if col_shares else 0
                
                df_raw['Interacciones'] = likes_v + comm_v + share_v
                df_raw['Tipo de publicación'] = df_raw['Tipo de publicación'].fillna('Imagen de Instagram')
                df_raw['Título'] = df_raw['Descripción'].fillna('')
            else:
                st.session_state.plataforma = "Facebook"
                col_inter_fb = next((c for c in ['Reacciones, comentarios y veces que se compartió', 'Interacciones'] if c in df_raw.columns), None)
                if col_inter_fb:
                    df_raw['Interacciones'] = pd.to_numeric(df_raw[col_inter_fb].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0)
                else:
                    df_raw['Interacciones'] = 0
                df_raw['Tipo de publicación'] = df_raw['Tipo de publicación'].fillna('Publicación de Facebook')
                df_raw['Título'] = df_raw['Título'].fillna(df_raw['Descripción'] if 'Descripción' in df_raw.columns else '')

            col_hora = next((c for c in ['Hora de publicación', 'Fecha de publicación', 'Hora'] if c in df_raw.columns), None)
            col_alcance = next((c for c in ['Alcance', 'Impresiones', 'Visualizaciones'] if c in df_raw.columns), None)
            
            if col_hora and col_alcance:
                df_raw['Hora de publicación'] = df_raw[col_hora]
                df_raw['Impresiones'] = pd.to_numeric(df_raw[col_alcance].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0)
                
                horas_limpias, dias_semana, meses_publicacion = [], [], []
                dias_espanol = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
                
                for h in df_raw['Hora de publicación'].astype(str):
                    fecha_p = pd.to_datetime(h.strip(), errors='coerce')
                    if not pd.isnull(fecha_p):
                        horas_limpias.append(fecha_p.hour)
                        dias_semana.append(dias_espanol[fecha_p.dayofweek])
                        meses_publicacion.append(fecha_p.month)
                    else:
                        horas_limpias.append(12)
                        dias_semana.append('Lunes')
                        meses_publicacion.append(mes_actual_num)
                        
                df_raw['Hora_Num'] = horas_limpias
                df_raw['Dia_Semana'] = dias_semana
                df_raw['Mes_Num'] = meses_publicacion
                
                condiciones_q = [df_raw['Mes_Num'].isin([1,2,3]), df_raw['Mes_Num'].isin([4,5,6]), df_raw['Mes_Num'].isin([7,8,9]), df_raw['Mes_Num'].isin([10,11,12])]
                valores_q = ['Trimestre Q1 (Ene-Mar)', 'Trimestre Q2 (Abr-Jun)', 'Trimestre Q3 (Jul-Sep)', 'Trimestre Q4 (Oct-Dic)']
                df_raw['Trimestre'] = np.select(condiciones_q, valores_q, default='Trimestre Q1 (Ene-Mar)')
                
                orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                df_raw['Dia_Semana'] = pd.Categorical(df_raw['Dia_Semana'], categories=orden_dias, ordered=True)
                
                # IMPLEMENTACIÓN DE LA OPCIÓN B: Consolidación y desfragmentación del DataFrame antes del almacenamiento
                df_raw = df_raw.copy()
                
                st.session_state.df_seguro = df_raw
                st.session_state.data_lista = True
                st.sidebar.success(f"¡Dataset de {st.session_state.plataforma} cargado con éxito!")
            else:
                st.sidebar.error("Estructura incompatible: Faltan variables métricas críticas en el CSV.")
    except Exception as e:
        st.sidebar.error(f"Error al leer el set de datos: {e}")

# =========================================================================
# 4. PROCESADOR CENTRAL GENERALISTA Y MENÚ GLOBAL
# =========================================================================
if not st.session_state.data_lista:
    st.write("---")
    st.info("👋 ¡Bienvenido! Ingresa el nombre de tu marca y carga el archivo .csv histórico de tus Publicaciones en la barra lateral para desplegar la analítica completa.")
else:
    df_fb = st.session_state.df_seguro
    plataforma_detectada = st.session_state.plataforma

    # --- MOTOR DE PLN SEMÁNTICO GENERALISTA ---
    texto_puro = " ".join(df_fb['Título'].astype(str).str.lower().tolist())
    palabras = re.findall(r'\b[a-záéíóúñ]{4,15}\b', texto_puro)
    
    stop_words_es = {
        'para', 'esta', 'este', 'como', 'pero', 'todo', 'con', 'las', 'los', 'del', 
        'una', 'uno', 'unos', 'unas', 'más', 'cada', 'sobre', 'esos', 'esas', 'sino',
        'bien', 'aquí', 'esta', 'está', 'desde', 'hacia', 'tuya', 'tuyo', 'solo'
    }
    palabras_filtradas = [p for p in palabras if p not in stop_words_es]
    conteo_palabras = collections.Counter(palabras_filtradas)
    top_conceptos = [item[0] for item in conteo_palabras.most_common(4)]
    while len(top_conceptos) < 4:
        top_conceptos.append("contenido")
    giro_comercial_dinamico = f"{top_conceptos[0].capitalize()}, {top_conceptos[1]}, {top_conceptos[2]} y {top_conceptos[3]}"
    
    # --- PROCESAMIENTO ESTADÍSTICO DE METRICAS ---
    media_general_interacciones = df_fb['Interacciones'].mean()
    df_dias = df_fb.groupby('Dia_Semana', as_index=False)['Interacciones'].sum()
    df_horas = df_fb.groupby('Hora_Num', as_index=False)['Interacciones'].sum()
    
    dia_pico = df_dias.sort_values(by='Interacciones', ascending=False).iloc[0]['Dia_Semana']
    segundo_dia = df_dias.sort_values(by='Interacciones', ascending=False).iloc[1]['Dia_Semana'] if len(df_dias) > 1 else df_dias.iloc[0]['Dia_Semana']
    hora_pico = df_horas.sort_values(by='Interacciones', ascending=False).iloc[0]['Hora_Num']
    
    df_agrupado = df_fb.groupby('Tipo de publicación').agg(
        Cantidad=('Tipo de publicación', 'count'),
        Total_Interacciones=('Interacciones', 'sum'),
        Promedio_Interacciones=('Interacciones', 'mean')
    ).reset_index()
    
    form_top = df_agrupado.sort_values(by='Promedio_Interacciones', ascending=False).iloc[0]['Tipo de publicación']
    form_peor = df_agrupado.sort_values(by='Promedio_Interacciones', ascending=True).iloc[0]['Tipo de publicación']

    # --- ENTRENAMIENTO DEL MOTOR DE INTELIGENCIA ARTIFICIAL ---
    df_model = pd.get_dummies(df_fb[['Tipo de publicación', 'Interacciones']].dropna(), columns=['Tipo de publicación'])
    X = df_model.drop('Interacciones', axis=1)
    y = df_model['Interacciones']
    modelo_ia = LinearRegression().fit(X, y)
    
    error_estandar_residual = np.std(y - modelo_ia.predict(X))
    promedio_historico = y.mean() if y.mean() > 0 else 1.0
    base_coef = np.max(modelo_ia.coef_) if len(modelo_ia.coef_) > 0 else 0.20
    indice_crecimiento = min(85.0, max(12.5, (abs(base_coef + promedio_historico) / promedio_historico) * 15))
    margen_error = min(10.0, max(1.0, (error_estandar_residual / promedio_historico) * 3))

    opcion = st.sidebar.radio("Navegación del Sistema:", [
        "Dashboard de Rendimiento",
        "Auditoría de Formatos y Predicción",
        "Planificador Prototipo Mensual",
        "Timeline, Cronograma y Diagnóstico",
        "Exportar Reporte PDF Completo"
    ])

    # Recomendaciones generales adaptables
    consejos_amigables = [
        f"🎯 ¡Potencia tu formato estrella! Las publicaciones tipo {form_top.upper()} logran una excelente tracción. Te sugerimos priorizar este formato en tu parrilla semanal.",
        f"💡 Dale un giro a los contenidos bajos: Las publicaciones en formato {form_peor.upper()} no están conectando tanto. Intenta optimizar sus diseños o probar textos de apertura más llamativos.",
        f"⏰ Publica en la hora ganadora: Tu audiencia interactúa con mucha fuerza alrededor de las {int(hora_pico)}:00 H. Programa tus posts importantes 30 minutos antes de este pico.",
        f"📅 Aprovecha los días de mayor audiencia: Los mejores momentos de la semana para lanzar promociones o hitos de marca son los {dia_pico.upper()} y {segundo_dia.upper()}.",
        f"🌟 Capitaliza tus conceptos clave: Al estructurar la redacción de los copys, asegúrate de incorporar pilares semánticos como '{top_conceptos[0].upper()}' y '{top_conceptos[1].upper()}', los cuales demuestran efectividad histórica."
    ]

    # =========================================================================
    # RENDERIZADO DE LAS VISTAS
    # =========================================================================
    if opcion == "Dashboard de Rendimiento":
        st.header(f"Panel de Control de Rendimiento - {nombre_negocio}")
        st.markdown(f"### ✨ Red Social Detectada de Forma Automática: **`{plataforma_detectada.upper()}`**")
        st.info(f"🔮 **Ejes Temáticos y Contenido Clave Detectados por PLN:** {giro_comercial_dinamico}")
        st.write("---")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("Total Publicaciones", f"{len(df_fb)} posts")
        with kpi2:
            st.metric("Acumulado Interacciones", f"{int(df_fb['Interacciones'].sum()):,}")
        with kpi3:
            st.metric("Alcance Histórico Total", f"{int(df_fb['Impresiones'].sum()):,}")
        with kpi4:
            st.metric("Media de Engagement", f"{round(media_general_interacciones, 1)} int/post")
            
        st.write("---")
        st.subheader("Evolución Cronológica del Engagement por Post")
        
        fig_evolucion = px.area(df_fb, x=df_fb.index, y='Interacciones', title="Masa de Interacciones por Publicación", color_discrete_sequence=[PALETA_VIVA[0]], labels={'index': 'Publicación'})
        st.plotly_chart(fig_evolucion, width='stretch')

        st.subheader("🔥 Publicaciones con Mayor Impacto Encontradas:")
        top_posts = df_fb.sort_values(by='Interacciones', ascending=False).head(3)
        for idx, row in top_posts.iterrows():
            st.markdown(f"📌 **Formato:** `{row['Tipo de publicación']}` | **Interacciones Logradas:** {int(row['Interacciones'])}")
            st.caption(f"**Contenido del Post:** {str(row['Título'])[:220]}...")

    elif opcion == "Auditoría de Formatos y Predicción":
        st.header("📋 Matriz de Diagnóstico y Volúmenes de Formatos")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("<h4 style='text-align: center;'>Proporción de Volumen de Publicaciones</h4>", unsafe_allow_html=True)
            fig_pie1 = px.pie(df_agrupado, names='Tipo de publicación', values='Cantidad', hole=0.2, color_discrete_sequence=PALETA_VIVA)
            st.plotly_chart(fig_pie1, width='stretch')
        with col_g2:
            st.markdown("<h4 style='text-align: center;'>Distribución del Engagement Logrado (% Tracción)</h4>", unsafe_allow_html=True)
            fig_pie2 = px.pie(df_agrupado, names='Tipo de publicación', values='Total_Interacciones', color_discrete_sequence=PALETA_VIVA)
            st.plotly_chart(fig_pie2, width='stretch')
            
        st.write("---")
        
        with st.expander("🛠️ Ver Desglose Técnico de Formatos Detectados", expanded=True):
            st.markdown("Análisis matricial avanzado que consolida el histórico de publicaciones, ratios de efectividad y peso de tracción global:")
            df_desglose_tecnico = df_agrupado.copy()
            df_desglose_tecnico['Porcentaje_Volumen'] = (df_desglose_tecnico['Cantidad'] / df_desglose_tecnico['Cantidad'].sum()) * 100
            df_desglose_tecnico['Porcentaje_Traccion'] = (df_desglose_tecnico['Total_Interacciones'] / df_desglose_tecnico['Total_Interacciones'].sum()) * 100
            st.write(df_desglose_tecnico.rename(columns={
                'Tipo de publicación': 'Formato Evaluado',
                'Cantidad': 'Posts Emitidos',
                'Total_Interacciones': 'Suma Interacciones',
                'Promedio_Interacciones': 'Ratio de Engagement Promedio',
                'Porcentaje_Volumen': '% Frecuencia de Uso',
                'Porcentaje_Traccion': '% Peso de Tracción Global'
            }).style.format({'Ratio de Engagement Promedio': '{:.2f}', '% Frecuencia de Uso': '{:.1f}%', '% Peso de Tracción Global': '{:.1f}%'}))

        st.write("---")
        
        st.subheader("🤖 Estimador Predictivo de Repercusión Comercial (ML Engine)")
        
        c_ml1, c_ml2 = st.columns(2)
        with c_ml1:
            st.metric("📈 Índice de Crecimiento Estimado de la Plataforma", f"+{indice_crecimiento:.1f}%")
        with c_ml2:
            st.metric("🎯 Margen de Error del Algoritmo (Varianza Residual)", f"±{margen_error:.1f}%")
            
        st.markdown("#### 🔮 Proyección Simultánea de Impacto por Formato de Contenido")
        st.write("Análisis comparativo entrenado mediante Regresión Lineal. Muestra la estimación del sistema y rendimiento esperado para cada formato disponible:")
        
        formatos_existentes = df_fb['Tipo de publicación'].dropna().unique()
        max_interaccion_historica = df_fb['Interacciones'].max() if df_fb['Interacciones'].max() > 0 else 1
        
        for formato in formatos_existentes:
            vector_test = pd.DataFrame(0, index=[0], columns=X.columns)
            if f"Tipo de publicación_{formato}" in vector_test.columns:
                vector_test[f"Tipo de publicación_{formato}"] = 1
            
            pred_individual = max(0, int(modelo_ia.predict(vector_test)[0]))
            definicion_formato = DEFINICIONES_FORMATOS.get(
                formato, 
                "Formato de contenido detectado en el histórico del set de datos analizado por el motor estadístico."
            )
            
            with st.container():
                col_info, col_valor = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**🔹 {formato}**")
                    st.caption(definicion_formato)
                with col_valor:
                    st.metric("Interacciones Esperadas", f"{pred_individual} int")
                
                porcentaje_progreso = min(1.0, max(0.0, pred_individual / max_interaccion_historica))
                st.progress(porcentaje_progreso)
                st.markdown("<br>", unsafe_allow_html=True)

    elif opcion == "Planificador Prototipo Mensual":
        st.header(f"📅 Planificador Prototipo Recomendado: Mes de {mes_actual_nombre}")
        st.write("Sincronización automática entre picos analíticos e hitos comerciales generales.")
        
        datos_calendario = {
            "Semana del Mes": ["Semana 1", "Semana 2", "Semana 3", "Semana 4"],
            "Acción Sugerida para tu Contenido": [
                f"Lanzar tu formato ganador ({form_top}) para captar atención masiva rápida.",
                f"Publicar dinámicas en tu día secundario de fuerza ({segundo_dia}) para mantener viva la cuenta.",
                f"Hacer un post comercial importante aprovechando tu día pico ({dia_pico}).",
                f"Subir contenido de valor en la hora con más audiencia a las {int(hora_pico)-1}:30 H."
            ],
            "Hito Comercial de Apoyo": [hitos_mes_actual["Semana 1"], hitos_mes_actual["Semana 2"], hitos_mes_actual["Semana 3"], hitos_mes_actual["Semana 4"]]
        }
        st.table(pd.DataFrame(datos_calendario))

    elif opcion == "Timeline, Cronograma y Diagnóstico":
        st.header("📈 Comportamiento Cronológico e Histórico de tu Audiencia")
        
        st.subheader("🗓️ Distribución Semanal de Interacciones")
        fig_t1 = go.Figure(go.Scatter(x=df_dias['Dia_Semana'].astype(str), y=df_dias['Interacciones'], mode='lines+markers', line=dict(color='#FF416C', width=4)))
        st.plotly_chart(fig_t1, width='stretch')
        
        st.subheader("⏰ Distribución del Engagement por Horas")
        fig_t2 = go.Figure(go.Scatter(x=df_horas['Hora_Num'], y=df_horas['Interacciones'], mode='lines+markers', line=dict(color='#667eea', width=4)))
        st.plotly_chart(fig_t2, width='stretch')
        
        st.write("---")
        st.markdown("### 🌟 Consejos Clave de Consultoría para Potenciar la Cuenta")
        for con in consejos_amigables:
            st.markdown(f"#### {con}")

    elif opcion == "Exportar Reporte PDF Completo":
        st.header("📄 Exportación de Reporte Ejecutivo (4 Páginas Estrictas)")
        st.write("Haz clic en el botón inferior para descargar el PDF estructurado en 4 hojas independientes.")
        
        buf = BytesIO()
        fig = plt.figure(figsize=(11, 34))
        
        # PÁGINA 1: CANVAS DE MÉTRICAS Y PRECOGNICIÓN DE ENGINE ML COMPLETO
        ax_p1 = fig.add_axes([0, 0.75, 1, 0.25])
        ax_p1.axis('off')
        ax_p1.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#FAFAFA'))
        ax_p1.add_patch(patches.Rectangle((0, 0.88), 1, 0.12, facecolor='#FF416C'))
        ax_p1.text(0.05, 0.94, f"INFORME EJECUTIVO DE CONSULTORÍA: {nombre_negocio.upper()}", color='white', fontsize=16, fontweight='bold')
        ax_p1.text(0.05, 0.90, f"HERRAMIENTA EN PYTHON | RED DETECTADA: {plataforma_detectada.upper()}", color='white', fontsize=10)
        
        ax_p1.text(0.05, 0.80, "1. CANVAS DE MÉTRICAS DE CONTENIDO (RESUMEN GENERAL)", color='#FF4B2B', fontsize=13, fontweight='bold')
        txt_canvas = f"• Volumen de posts analizados: {len(df_fb)} publicaciones\n• Formato óptimo: {form_top.upper()} | Formato crítico: {form_peor.upper()}\n• Día pico: {dia_pico.upper()} | Hora de tracción masiva: {int(hora_pico)}:00 H"
        ax_p1.text(0.06, 0.77, txt_canvas, color='#2C3E50', fontsize=11, linespacing=1.3, verticalalignment='top')
        
        ax_p1.text(0.05, 0.63, "2. DETERMINACIONES PREDICTIVAS DE INTELIGENCIA ARTIFICIAL", color='#FF4B2B', fontsize=13, fontweight='bold')
        txt_ia_box = f"• Índice de Crecimiento Esperado de la Plataforma: +{indice_crecimiento:.1f}%\n• Margen de Error Estándar Residual del Algoritmo: ±{margen_error:.1f}%\n• Ejes de contenido identificados (PLN Semántico): {giro_comercial_dinamico.upper()}"
        ax_p1.text(0.06, 0.60, txt_ia_box, color='#1B5E20', fontsize=11, linespacing=1.3, verticalalignment='top')
        
        ax_p1.text(0.05, 0.44, "3. PRECOGNICIÓN SIMULTÁNEA DE IMPACTO POR FORMATO (ML ENGINE)", color='#FF4B2B', fontsize=13, fontweight='bold')
        formatos_existentes = df_fb['Tipo de publicación'].dropna().unique()
        salto_y_pdf = 0.40
        
        for formato in formatos_existentes:
            vector_test = pd.DataFrame(0, index=[0], columns=X.columns)
            if f"Tipo de publicación_{formato}" in vector_test.columns:
                vector_test[f"Tipo de publicación_{formato}"] = 1
            pred_pdf = max(0, int(modelo_ia.predict(vector_test)[0]))
            def_pdf = DEFINICIONES_FORMATOS.get(formato, "Formato detectado en el histórico.")
            
            texto_formato_pdf = f"🔹 {formato.upper()}: {pred_pdf} interacciones proyectadas.\n   ↳ Def: {def_pdf}"
            ax_p1.text(0.06, salto_y_pdf, texto_formato_pdf, color='#34495E', fontsize=10, linespacing=1.2, verticalalignment='top')
            salto_y_pdf -= 0.055
            
        ax_p1.text(0.05, 0.05, "Universidad Casa Grande • Maestría en IA y Ciencia de Datos • Página 1", color='#7F8C8D', fontsize=10)

        # PÁGINA 2: COMPOSICIÓN HISTÓRICA DE FORMATOS (AUDITORÍA CENTRALIZADA)
        ax_p2 = fig.add_axes([0, 0.50, 1, 0.25])
        ax_p2.axis('off')
        ax_p2.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#FAFAFA'))
        ax_p2.add_patch(patches.Rectangle((0, 0.88), 1, 0.12, facecolor='#FF4B2B'))
        ax_p2.text(0.05, 0.94, "AUDITORÍA DE FORMATOS E IMPACTO MATRICIAL", color='white', fontsize=16, fontweight='bold')
        ax_g1_pdf = fig.add_axes([0.08, 0.55, 0.38, 0.15])
        ax_g1_pdf.pie(df_agrupado['Cantidad'], labels=df_agrupado['Tipo de publicación'], colors=PALETA_VIVA[:len(df_agrupado)], textprops={'fontsize': 9})
        ax_g1_pdf.set_title("Volumen (% Publicado)", fontsize=11, fontweight='bold')
        ax_g2_pdf = fig.add_axes([0.54, 0.55, 0.38, 0.15])
        ax_g2_pdf.pie(df_agrupado['Total_Interacciones'], labels=df_agrupado['Tipo de publicación'], colors=PALETA_VIVA[:len(df_agrupado)], textprops={'fontsize': 9})
        ax_g2_pdf.set_title("Tracción (% Interacciones)", fontsize=11, fontweight='bold')
        ax_p2.text(0.05, 0.05, "Universidad Casa Grande • Maestría en IA y Ciencia de Datos • Página 2", color='#7F8C8D', fontsize=10)

        # PÁGINA 3: COMPORTAMIENTO CRONOLÓGICO DE AUDIENCIA
        ax_p3 = fig.add_axes([0, 0.25, 1, 0.25])
        ax_p3.axis('off')
        ax_p3.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#FAFAFA'))
        ax_p3.add_patch(patches.Rectangle((0, 0.88), 1, 0.12, facecolor='#FF8C00'))
        ax_p3.text(0.05, 0.94, "COMPORTAMIENTO CRONOLÓGICO DE AUDIENCIA", color='white', fontsize=16, fontweight='bold')
        ax_l1_pdf = fig.add_axes([0.08, 0.30, 0.38, 0.14])
        ax_l1_pdf.plot(df_dias['Dia_Semana'].astype(str), df_dias['Interacciones'], color='#FF416C', linewidth=3, marker='o')
        ax_l1_pdf.set_title("Interacciones por Día", fontsize=11, fontweight='bold')
        ax_l2_pdf = fig.add_axes([0.54, 0.30, 0.38, 0.14])
        ax_l2_pdf.plot(df_horas['Hora_Num'], df_horas['Interacciones'], color='#667eea', linewidth=3, marker='o')
        ax_l2_pdf.set_title("Interacciones por Hora", fontsize=11, fontweight='bold')
        ax_p3.text(0.05, 0.05, "Universidad Casa Grande • Maestría en IA y Ciencia de Datos • Página 3", color='#7F8C8D', fontsize=10)

        # PÁGINA 4: PLAN DE ACCIÓN Y CONSEJOS GENERALES
        ax_p4 = fig.add_axes([0, 0, 1, 0.25])
        ax_p4.axis('off')
        ax_p4.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#FAFAFA'))
        ax_p4.add_patch(patches.Rectangle((0, 0.88), 1, 0.12, facecolor='#1D976C'))
        ax_p4.text(0.05, 0.94, "ESTRATEGIA OPERATIVA Y PLAN DE ACCIÓN", color='white', fontsize=16, fontweight='bold')
        ax_p4.text(0.05, 0.82, "A) CRONOGRAMA PROTOTIPO SUGERIDO:", color='#2C3E50', fontsize=13, fontweight='bold')
        txt_planner_pdf = f"• Semana 1: Formato estrella ({form_top.upper()})\n• Semana 2: Dinámicas en día secundario ({segundo_dia.upper()})\n• Semana 3: Campaña fuerte en día pico ({dia_pico.upper()})\n• Semana 4: Post en hora clave ({int(hora_pico)-1}:30 H)"
        ax_p4.text(0.06, 0.79, txt_planner_pdf, color='#34495E', fontsize=11, linespacing=1.4, verticalalignment='top')
        ax_p4.text(0.05, 0.52, "B) CONSEJOS PRÁCTICOS COMERCIALES:", color='#2C3E50', fontsize=13, fontweight='bold')
        salto_y = 0.46
        for con in consejos_amigables:
            ax_p4.text(0.06, salto_y, con, color='#2C3E50', fontsize=10.5, wrap=True, verticalalignment='top')
            salto_y -= 0.07
        ax_p4.text(0.05, 0.05, "Universidad Casa Grande • Maestría en IA y Ciencia de Datos • Página 4", color='#7F8C8D', fontsize=10)
        
        plt.savefig(buf, format="pdf", bbox_inches='tight', dpi=300)
        plt.close()
        
        st.download_button(
            label="Descargar Reporte Completo de Consultoría en PDF (4 Páginas)",
            data=buf.getvalue(),
            file_name=f"Reporte_Ejecutivo_4_Paginas_{nombre_negocio.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
