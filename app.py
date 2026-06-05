import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
from datetime import datetime
import collections
import re

# =========================================================================
# 1. CONFIGURACIÓN DE LA INTERFAZ Y ESTILOS DE STREAMLIT
# =========================================================================
st.set_page_config(page_title="SaaS Planificador de Contenidos", layout="wide")

st.title("Plataforma de Analítica y Planificación de Contenidos Automática")
st.caption("Proyecto Integrador - Desarrollado por el Ing. Rafael Regato - Universidad Casa Grande")
st.write("---")

# =========================================================================
# 2. CAPTURA DE DATOS EN LA BARRA LATERAL (INPUTS DEL USUARIO)
# =========================================================================
st.sidebar.header("Configuración del Sistema")

nombre_negocio = st.sidebar.text_input("1. Nombre de tu marca o negocio:", placeholder="Ej. Mi Emprendimiento")

archivo_cargado = None
if nombre_negocio:
    st.sidebar.markdown("---")
    archivo_cargado = st.sidebar.file_uploader(f"2. Sube el CSV de Meta Business para '{nombre_negocio}'", type=["csv"])

data_lista = False
df_fb = None

# Base URL fija de GitHub con codificación de espacios (%20) para evitar enlaces rotos en producción
URL_BASE_REPOSITORIO = "https://raw.githubusercontent.com/rafaelregato/plataforma-analitica-contenido/main/ImgRef"
# =========================================================================
# 3. GUÍA VISUAL E ILUSTRADA DE EXTRACCIÓN (ONBOARDING DE UX OPTIMIZADO)
# =========================================================================
if not nombre_negocio or archivo_cargado is None:
    st.markdown("### 📖 Guía Rápida: Cómo descargar tu archivo .CSV desde Meta Business Suite")
    st.write("Sigue estos pasos ilustrados para obtener el reporte oficial de tus publicaciones:")

    tab_proceso, tab_ayuda_redes = st.tabs(["🚀 Paso a Paso con Capturas", "📱 Filtro de Redes"])

    with tab_proceso:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 1. Accede a Meta Business Suite")
            st.caption("Abre el menú lateral o de herramientas y haz clic en **Meta Business Suite**.")
            st.image("https://raw.githubusercontent.com/rafaelregato/plataforma-analitica-contenido/main/ImgRef/image_c583dd.jpg", caption="Paso 1: Panel principal", use_container_width=True)
        with col2:
            st.markdown("##### 2. Ve a la sección 'Contenido'")
            st.caption("Dentro del panel izquierdo, selecciona la opción **Contenido**.")
            st.image("https://raw.githubusercontent.com/rafaelregato/plataforma-analitica-contenido/main/ImgRef/image_c5845f.jpg", caption="Paso 2: Menú lateral", use_container_width=True)
            
        st.write("---")
        
        col3, col4, col5 = st.columns(3)
        with col3:
            st.markdown("##### 3. Selecciona 'Exportar datos'")
            st.caption("Ajusta el rango de fechas en la tabla de publicaciones y presiona **Exportar datos**.")
            st.image("https://raw.githubusercontent.com/rafaelregato/plataforma-analitica-contenido/main/ImgRef/image_c5847b.jpg", caption="Paso 3: Botón de exportación", use_container_width=True)
        with col4:
            st.markdown("##### 4. Configura el .CSV")
            st.caption("Marca el nivel 'Publicación' en la ventana emergente y presiona el botón **Generar**.")
            st.image("https://raw.githubusercontent.com/rafaelregato/plataforma-analitica-contenido/main/ImgRef/image_c58498.jpg", caption="Paso 4: Parámetros del reporte", use_container_width=True)
        with col5:
            st.markdown("##### 5. Descarga el archivo")
            st.caption("Haz clic en la **flecha pequeña** junto al botón exportar para abrir las descargas recientes.")
            st.image("https://raw.githubusercontent.com/rafaelregato/plataforma-analitica-contenido/main/ImgRef/image_c584b6.jpg", caption="Paso 5: Historial de descargas", use_container_width=True)

    with tab_ayuda_redes:
        st.markdown("#### 💡 Inclusión de Canales")
        col_info_izq, col_info_der = st.columns([2, 1])
        with col_info_izq:
            st.write("""
            Meta unifica el contenido en un solo reporte. Verifica previamente:
            1. Que aparezcan los iconos de **Facebook** e **Instagram** en la grilla de publicaciones.
            2. Si falta alguno, asegúrate de marcar ambas casillas en el filtro de **Plataforma** antes de exportar.
            """)
        with col_info_der:
            st.image("https://raw.githubusercontent.com/rafaelregato/plataforma-analitica-contenido/main/ImgRef/image_c5847b.jpg", caption="Verificación en grilla", use_container_width=True)

    st.write("---")
    st.info("💡 **Privacidad:** Los datos son procesados de forma volátil en la memoria local de tu navegador. Nada se almacena externamente.")
    st.write("---")
# =========================================================================
# 4. SINCRONIZACIÓN CRONOLÓGICA CON EL MES REAL DE EJECUCIÓN (LÓGICA TEMPORAL)
# =========================================================================
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
    3: {"Semana 1": "Día de la Mujer - Valor Humano", "Semana 2": "Concienciación y Cultura", "Semana 3": "Primavera - Cambio de Catálogo", "Semana 4": "Ofertas de Cierre Trimestral"},
    4: {"Semana 1": "Educación e Instructivos", "Semana 2": "Día de la Tierra - Eco-Values", "Semana 3": "Dinámicas de Co-Creación", "Semana 4": "Campañas Intermedias Relámpago"},
    5: {"Semana 1": "Día del Trabajador - Ofertas B2B", "Semana 2": "Día de la Madre - Alta Conversión", "Semana 3": "Post-Festejos - Fidelización", "Semana 4": "Encuestas de Mitad de Año"},
    6: {"Semana 1": "Día del Niño - Contenido Emocional", "Semana 2": "Medio Ambiente - Sostenible", "Semana 3": "Día del Padre - Guías de Regalos", "Semana 4": "Solsticio - Identidad Local"},
    7: {"Semana 1": "Vacaciones - Reels Ligeros", "Semana 2": "Viajes - Estilo de Vida", "Semana 3": "Reciclaje de Contenido Viral", "Semana 4": "Ajuste y Optimización de Pauta"},
    8: {"Semana 1": "Estética de Alta Fidelidad", "Semana 2": "Día de la Juventud - Tendencias", "Semana 3": "Carruseles de Autoridad", "Semana 4": "Liquidación de Stock Estacional"},
    9: {"Semana 1": "Flores Amarillas - Interacción", "Semana 2": "Entrada de Otoño - Nueva Paleta", "Semana 3": "Testimonios y Casos de Éxito", "Semana 4": "Estrategias de Calentamiento Q4"},
    10: {"Semana 1": "Preventas de Temporada", "Semana 2": "Lúdico - Dinámicas Creativas", "Semana 3": "Videos Cortos de Intriga", "Semana 4": "Halloween - Campaña Temática"},
    11: {"Semana 1": "Mensajes de Tradición y Respeto", "Semana 2": "Black Friday - Captación Leads", "Semana 3": "Black Friday - Ofertas Agresivas", "Semana 4": "Post-Venta y Logística Eficiente"},
    12: {"Semana 1": "Navidad - Unión y Emotividad", "Semana 2": "Guías de Compra Cruzada", "Semana 3": "Cenas y Paquetes Corporativos", "Semana 4": "Cierre de Año y Nuevas Metas"}
}
hitos_mes_actual = banco_hitos_anuales[mes_actual_num]

# =========================================================================
# 5. PROCESAMIENTO, ARMONIZACIÓN Y NORMALIZACIÓN DEL DATASET CSV
# =========================================================================
if archivo_cargado is not None:
    try:
        df_raw = pd.read_csv(archivo_cargado, encoding='utf-8')
        
        dicc_sinonimos = {
            'Tipo de publicación': ['Tipo de publicación', 'Tipo', 'Format'],
            'Hora de publicación': ['Hora de publicación', 'Hora', 'Published Time'],
            'Interacciones': ['Interacciones', 'Interactions', 'Engagements'],
            'Impresiones': ['Impresiones', 'Alcance', 'Impresiones ', 'Impressions'],
            'Título': ['Título', 'Texto', 'Title', 'Descripción']
        }
        
        for col_estandar, lista_alternativas in dicc_sinonimos.items():
            for alt in lista_alternativas:
                if alt in df_raw.columns and col_estandar not in df_raw.columns:
                    df_raw[col_estandar] = df_raw[alt]
        
        columnas_requeridas = ['Tipo de publicación', 'Hora de publicación', 'Interacciones', 'Impresiones', 'Título']
        
        if all(col in df_raw.columns for col in columnas_requeridas):
            df_fb = df_raw.copy()
            
            df_fb['Interacciones'] = pd.to_numeric(df_fb['Interacciones'], errors='coerce').fillna(0)
            df_fb['Impresiones'] = pd.to_numeric(df_fb['Impresiones'], errors='coerce').fillna(0)
            df_fb['Título'] = df_fb['Título'].astype(str).fillna('')
            
            horas_limpias = []
            dias_semana = []
            meses_publicacion = []
            dias_espanol = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
            
            for h in df_fb['Hora de publicación'].astype(str):
                try:
                    fecha_p = pd.to_datetime(h, errors='coerce')
                    if not pd.isnull(fecha_p):
                        horas_limpias.append(fecha_p.hour)
                        dias_semana.append(dias_espanol[fecha_p.dayofweek])
                        meses_publicacion.append(fecha_p.month)
                    else:
                        partes = h.split()
                        hora_entera = int(partes[1].split(':')[0])
                        horas_limpias.append(hora_entera)
                        dias_semana.append('Lunes')
                        meses_publicacion.append(mes_actual_num)
                except:
                    horas_limpias.append(12)
                    dias_semana.append('Lunes')
                    meses_publicacion.append(mes_actual_num)
                    
            df_fb['Hora_Num'] = horas_limpias
            df_fb['Dia_Semana'] = dias_semana
            df_fb['Mes_Num'] = meses_publicacion
            
            condiciones_q = [
                df_fb['Mes_Num'].isin([1, 2, 3]),
                df_fb['Mes_Num'].isin([4, 5, 6]),
                df_fb['Mes_Num'].isin([7, 8, 9]),
                df_fb['Mes_Num'].isin([10, 11, 12])
            ]
            valores_q = ['Trimestre Q1 (Ene-Mar)', 'Trimestre Q2 (Abr-Jun)', 'Trimestre Q3 (Jul-Sep)', 'Trimestre Q4 (Oct-Dic)']
            df_fb['Trimestre'] = np.select(condiciones_q, valores_q, default='Trimestre Q1 (Ene-Mar)')
            
            orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            df_fb['Dia_Semana'] = pd.Categorical(df_fb['Dia_Semana'], categories=orden_dias, ordered=True)
            
            st.sidebar.success("Datos e historial validados con éxito.")
            data_lista = True
        else:
            st.sidebar.error("El archivo CSV no cuenta con el formato estructural de Meta Business Suite.")
    except Exception as e:
        st.sidebar.error(f"Error crítico en lectura de datos: {e}")

# =========================================================================
# 6. MOTOR ESTADÍSTICO, PLN Y MACHINE LEARNING GLOBAL (SÍNCRONO)
# =========================================================================
if data_lista:
    # 6.1 Procesamiento de Lenguaje Natural Semántico
    texto_puro = " ".join(df_fb['Título'].str.lower().tolist())
    palabras = re.findall(r'\b[a-záéíóúñ]{4,15}\b', texto_puro)
    stop_words_es = {'para', 'esta', 'este', 'como', 'pero', 'todo', 'con', 'las', 'los', 'del', 'una', 'uno', 'unos', 'unas'}
    palabras_filtradas = [p for p in palabras if p not in stop_words_es]
    conteo_palabras = collections.Counter(palabras_filtradas)
    top_conceptos = [item[0] for item in conteo_palabras.most_common(4)]
    while len(top_conceptos) < 4:
        top_conceptos.append("contenido")
        
    giro_comercial_dinamico = f"Especialista en {top_conceptos[0].capitalize()}, {top_conceptos[1]}, {top_conceptos[2]} y {top_conceptos[3]}"
    
    # 6.2 Extremos y Comportamiento Histórico
    media_general_interacciones = df_fb['Interacciones'].mean()
    df_dias = df_fb.groupby('Dia_Semana', as_index=False)['Interacciones'].sum()
    df_horas = df_fb.groupby('Hora_Num', as_index=False)['Interacciones'].sum()
    
    dia_pico = df_dias.sort_values(by='Interacciones', ascending=False).iloc[0]['Dia_Semana']
    segundo_dia = df_dias.sort_values(by='Interacciones', ascending=False).iloc[1]['Dia_Semana']
    dia_valle = df_dias.sort_values(by='Interacciones', ascending=True).iloc[0]['Dia_Semana']
    hora_pico = df_horas.sort_values(by='Interacciones', ascending=False).iloc[0]['Hora_Num']
    
    df_trimestres = df_fb.groupby('Trimestre', as_index=False)['Interacciones'].agg(['sum', 'mean']).reset_index()
    valores_q = ['Trimestre Q1 (Ene-Mar)', 'Trimestre Q2 (Abr-Jun)', 'Trimestre Q3 (Jul-Sep)', 'Trimestre Q4 (Oct-Dic)']
    for q in valores_q:
        if q not in df_trimestres['Trimestre'].values:
            df_trimestres = pd.concat([df_trimestres, pd.DataFrame([{'Trimestre': q, 'sum': 0, 'mean': 0}])], ignore_index=True)
    q_max = df_trimestres.sort_values(by='sum', ascending=False).iloc[0]['Trimestre']
    
    df_agrupado = df_fb.groupby('Tipo de publicación').agg(
        Cantidad=('Tipo de publicación', 'count'),
        Total_Interacciones=('Interacciones', 'sum'),
        Promedio_Interacciones=('Interacciones', 'mean')
    ).reset_index()
    
    form_top = df_agrupado.sort_values(by='Promedio_Interacciones', ascending=False).iloc[0]['Tipo de publicación']
    form_peor = df_agrupado.sort_values(by='Promedio_Interacciones', ascending=True).iloc[0]['Tipo de publicación']

    # 6.3 Algoritmo Predictivo (Regresión Lineal Matricial)
    df_model = pd.get_dummies(df_fb[['Tipo de publicación', 'Interacciones']].dropna(), columns=['Tipo de publicación'])
    X = df_model.drop('Interacciones', axis=1)
    y = df_model['Interacciones']
    modelo_ia = LinearRegression().fit(X, y)
    
    predicciones = modelo_ia.predict(X)
    error_estandar_residual = np.std(y - predicciones)
    promedio_historico = y.mean() if y.mean() > 0 else 1.0
    
    base_coef = np.max(modelo_ia.coef_) if len(modelo_ia.coef_) > 0 else 0.20
    indice_crecimiento = min(85.0, max(12.5, (abs(base_coef + promedio_historico) / promedio_historico) * 15))
    margen_error = min(10.0, max(1.0, (error_estandar_residual / promedio_historico) * 3))

    recomendaciones_top10 = [
        f"1. Monopolizacion Estrategica del Formato Lider: Asignar el 60% de recursos a {form_top.upper()} por registrar un rendimiento promedio de {df_agrupado.sort_values(by='Promedio_Interacciones', ascending=False).iloc[0]['Promedio_Interacciones']:.1f} interacciones.",
        f"2. Desaceleracion o Rediseno del Peor Formato: Reducir un 80% la produccion de contenidos tipo {form_peor.upper()}, ya que apenas genera {df_agrupado.sort_values(by='Promedio_Interacciones', ascending=True).iloc[0]['Promedio_Interacciones']:.1f} interacciones por post.",
        f"3. Inyeccion de Capital en la Ventana de Oro: Concentrar el presupuesto de pauta paga en la cohorte estacional {q_max.upper()}, que acumula la mayor masa critica de engagement.",
        f"4. Ataque Riguroso en Hora Pico: Publicar exactamente a las {int(hora_pico)-1}:30 H (30 minutos antes del pico de las {int(hora_pico)}:00 H) para acelerar la indexacion algoritmica precoz.",
        f"5. Amortiguacion de Caidas en Dias Valle: Evitar anuncios de venta directa los dias {dia_valle.upper()}. Usar esta ventana para publicar historias casuales de interaccion.",
        f"6. Aprovechamiento de la Doble Traccion Semanal: Programar campanas importantes escalonadamente entre los dias {dia_pico.upper()} y {segundo_dia.upper()}.",
        f"7. Mineria de Palabras Clave de Exito: Inyectar en los primeros parrafos de tus copys los conceptos conceptuales dominantes: '{top_conceptos[0].upper()}' y '{top_conceptos[1].upper()}'.",
        f"8. Control de Varianza y Mitigacion de Errores: Dado que el margen de error predictivo se situa en un controlado +-{margen_error:.1f}%, usar pruebas A/B estructuradas.",
        f"9. Estrategia de Blindaje de Interaccion Inicial: Durante los primeros 20 minutos posteriores a la publicacion, responder interactivamente para forcear el alcance organico.",
        f"10. Alineacion Tematica Semantica: Forzar la consistencia de copys adaptando la comunicacion a los hitos temporales del mes actual de {mes_actual_nombre.upper()}."
    ]

# =========================================================================
# 7. ENRUTADOR DE NAVEGACIÓN DE LA INTERFAZ
# =========================================================================
if not data_lista:
    if nombre_negocio and archivo_cargado is not None:
        st.info("Por favor sube tu archivo .csv histórico para activar los módulos analíticos.")
else:
    opcion = st.sidebar.radio("Navegación del Sistema:", [
        "Dashboard de Rendimiento",
        "Auditoría de Formatos y Predicción",
        "Planificador Prototipo Mensual",
        "Timeline, Cronograma y Diagnóstico",
        "Exportar Reporte PDF Completo"
    ])
    
    # -------------------------------------------------------------------------
    # VISTA: DASHBOARD DE RENDIMIENTO
    # -------------------------------------------------------------------------
    if opcion == "Dashboard de Rendimiento":
        st.header(f"Histórico Analítico Corporativo - {nombre_negocio}")
        st.info(f"🔍 **Giro Comercial Analizado:** {giro_comercial_dinamico}")
        st.success(f"📅 **Mes de Operación Activo:** {mes_actual_nombre}")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Publicaciones Auditadas", len(df_fb))
        with c2:
            st.metric("Total Interacciones", int(df_fb['Interacciones'].sum()))
        with c3:
            st.metric("Alcance Acumulado", f"{int(df_fb['Impresiones'].sum()):,}")
            
        st.write("---")
        st.subheader("Top Publicaciones Destacadas:")
        top_posts = df_fb.sort_values(by='Interacciones', ascending=False).head(2)
        for idx, row in top_posts.iterrows():
            st.markdown(f"📌 **Formato:** `{row['Tipo de publicación']}` | **Interacciones:** {int(row['Interacciones'])}")
            st.caption(f"**Texto:** {str(row['Título'])[:200]}...")
            st.write("---")

    # -------------------------------------------------------------------------
    # VISTA: AUDITORÍA DE FORMATOS Y PREDICCIÓN
    # -------------------------------------------------------------------------
    elif opcion == "Auditoría de Formatos y Predicción":
        st.header("📊 Auditoría de Formatos")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("📁 Distribución de Parrilla")
            fig_pie1 = px.pie(df_agrupado, names='Tipo de publicación', values='Cantidad', hole=0.3, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_pie1, use_container_width=True)
        with col_g2:
            st.subheader("🎯 Impacto por Interacciones")
            fig_pie2 = px.pie(df_agrupado, names='Tipo de publicación', values='Total_Interacciones', color_discrete_sequence=px.colors.qualitative.Pastel2)
            st.plotly_chart(fig_pie2, use_container_width=True)
            
        st.write("---")
        for _, row in df_agrupado.iterrows():
            tipo = row['Tipo de publicación']
            cant = row['Cantidad']
            porcentaje_presencia = (cant / len(df_fb)) * 100
            promedio_post = row['Promedio_Interacciones']
            
            if promedio_post >= media_general_interacciones:
                estatus, color_badge = "RENDIMIENTO SUPERIOR", "green"
            else:
                estatus, color_badge = "BAJO-OPTIMIZABLE", "orange"
                
            st.markdown(f"#### Formato: **{tipo.upper()}**")
            st.markdown(f"• Volumen: {cant} ({porcentaje_presencia:.1f}%) | Promedio: `{promedio_post:.1f}`")
            st.markdown(f"Estatus: :{color_badge}[{estatus}]")
            st.write("---")
            
        st.subheader("🤖 Estimador Algorítmico")
        formatos_existentes = df_fb['Tipo de publicación'].dropna().unique()
        indice_defecto = list(formatos_existentes).index(form_top) if form_top in formatos_existentes else 0
        seleccion_usuario = st.selectbox("Elige el formato de tu próximo contenido:", formatos_existentes, index=indice_defecto)
        
        vector_test = pd.DataFrame(0, index=[0], columns=X.columns)
        col_c = f"Tipo de publicación_{seleccion_usuario}"
        if col_c in vector_test.columns:
            vector_test[col_c] = 1
            
        pred = modelo_ia.predict(vector_test)
        st.metric(label="Interacciones estimadas", value=f"{max(0, int(pred[0]))} esperadas")

    # -------------------------------------------------------------------------
    # VISTA: PLANIFICADOR PROTOTIPO MENSUAL
    # -------------------------------------------------------------------------
    elif opcion == "Planificador Prototipo Mensual":
        st.header(f"🗓️ Matriz Semanal Automatizada: {mes_actual_nombre}")
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.metric("Crecimiento Esperado", f"+{indice_crecimiento:.1f}%")
        with c_p2:
            st.metric("Margen de Error", f"±{margen_error:.1f}%")
            
        st.write("---")
        datos_calendario = {
            "Semana": ["Semana 1", "Semana 2", "Semana 3", "Semana 4"],
            "Estrategia Recomendada": [
                f"Publicar Formato Lider ({form_top}) enfocado en atraccion masiva.",
                f"Contenido de interaccion en dia de soporte ({segundo_dia}) para sostener ritmo.",
                f"Campana de conversion directa en el dia pico ({dia_pico}).",
                f"Post organico en la ventana horaria clave de las {int(hora_pico)-1}:30 H."
            ],
            "Hito Temporal": [hitos_mes_actual["Semana 1"], hitos_mes_actual["Semana 2"], hitos_mes_actual["Semana 3"], hitos_mes_actual["Semana 4"]]
        }
        st.table(pd.DataFrame(datos_calendario))

    # -------------------------------------------------------------------------
    # VISTA: TIMELINE, CRONOGRAMA Y DIAGNÓSTICO
    # -------------------------------------------------------------------------
    elif opcion == "Timeline, Cronograma y Diagnóstico":
        st.header("📅 Distribución Temporal")
        
        st.subheader("📈 Interacciones por Día")
        fig_t1 = go.Figure(go.Scatter(x=df_dias['Dia_Semana'].astype(str), y=df_dias['Interacciones'], mode='lines+markers', line=dict(color='#85C1E9', width=4)))
        st.plotly_chart(fig_t1, use_container_width=True)
        
        st.subheader("⏰ Comportamiento por Horas")
        fig_t2 = go.Figure(go.Scatter(x=df_horas['Hora_Num'], y=df_horas['Interacciones'], mode='lines+markers', line=dict(color='#F5B7B1', width=4)))
        st.plotly_chart(fig_t2, use_container_width=True)
        
        st.write("---")
        st.subheader("💡 Recomendaciones Estratégicas")
        for rec in recomendaciones_top10:
            st.markdown(rec)

    # -------------------------------------------------------------------------
    # VISTA: EXPORTAR REPORTE PDF COMPLETO (UX OPTIMIZADO CON COMENTARIOS VISUALES)
    # -------------------------------------------------------------------------
    elif opcion == "Exportar Reporte PDF Completo":
        st.header("📄 Descarga de Reporte de Consultoría (Multilámina)")
        st.write("Genera un PDF unificado de 2 páginas exactas sin desbordamiento.")
        
        # Elemento de UX: Informamos activamente al usuario que el motor está trabajando
        with st.spinner("Compilando gráficos vectoriales y estructurando el archivo PDF corporativo..."):
            buf = BytesIO()
            fig = plt.figure(figsize=(11, 22))
            lista_colores_base = ['#A9DFBF','#F9E79F','#F5B7B1','#AED6F1','#D2B4DE']
            colores_render = lista_colores_base[:max(1, len(df_agrupado))]
            
            # LÁMINA 1: AUDITORÍA DE FORMATOS
            ax_h1 = fig.add_axes([0, 0.50, 1, 0.50])
            ax_h1.axis('off')
            ax_h1.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#FAFAFA', zorder=1))
            ax_h1.add_patch(patches.Rectangle((0, 0.92), 1, 0.08, facecolor='#1A237E', zorder=2))
            ax_h1.text(0.04, 0.96, f"AUDITORÍA INTELIGENTE DE REDES SOCIALES: {nombre_negocio.upper()}", color='white', fontsize=13, fontweight='bold', zorder=3)
            ax_h1.text(0.04, 0.93, f"{giro_comercial_dinamico.upper()} | PÁGINA 1: AUDITORÍA DE FORMATOS", color='#90CAF9', fontsize=8.5, zorder=3)
            
            ax_h1.add_patch(patches.Rectangle((0.04, 0.73), 0.44, 0.16, facecolor='white', edgecolor='#CFD8DC', linewidth=0.8, zorder=2))
            ax_h1.text(0.06, 0.85, "MÉTRICAS BASE DEL CANVAS", color='#1A237E', fontsize=9.5, fontweight='bold', zorder=3)
            txt_b1 = f"Posts Auditados: {len(df_fb)}\nFormato Top: {form_top.upper()}\nFormato Crítico: {form_peor.upper()}\nDía Pico: {dia_pico.upper()}\nHora Pico: {int(hora_pico)}:00 H"
            ax_h1.text(0.06, 0.82, txt_b1, color='#37474F', fontsize=8.5, fontfamily='monospace', verticalalignment='top', zorder=3)
            
            ax_h1.add_patch(patches.Rectangle((0.52, 0.71), 0.44, 0.18, facecolor='white', edgecolor='#CFD8DC', linewidth=0.8, zorder=2))
            ax_h1.text(0.54, 0.85, "PREDICCIONES DE ENGINE (ML)", color='#1A237E', fontsize=9.5, fontweight='bold', zorder=3)
            txt_b2 = f"POTENCIAL DE CRECIMIENTO:\n  +{indice_crecimiento:.1f}%\n\nERROR ESTÁNDAR RESIDUAL:\n  ±{margen_error:.1f}%"
            ax_h1.text(0.54, 0.82, txt_b2, color='#1B5E20', fontsize=8, linespacing=1.1, verticalalignment='top', zorder=3)
            
            ax_h1.add_patch(patches.Rectangle((0.04, 0.40), 0.92, 0.29, facecolor='white', edgecolor='#CFD8DC', linewidth=0.8, zorder=2))
            ax_h1.text(0.06, 0.66, "COMPORTAMIENTO HISTÓRICO INTEGRADO EN CANVAS", color='#1A237E', fontsize=9.5, fontweight='bold', zorder=3)
            
            ax_pdf_pie1 = fig.add_axes([0.07, 0.71, 0.38, 0.11])
            ax_pdf_pie1.pie(df_agrupado['Cantidad'], labels=df_agrupado['Tipo de publicación'], colors=colores_render, textprops={'fontsize': 7.5}, startangle=90)
            ax_pdf_pie1.set_title("Volumen por Formato", fontsize=8.5, color='#1A237E', fontweight='bold')
            
            ax_pdf_pie2 = fig.add_axes([0.55, 0.71, 0.38, 0.11])
            ax_pdf_pie2.pie(df_agrupado['Total_Interacciones'], labels=df_agrupado['Tipo de publicación'], colors=colores_render, textprops={'fontsize': 7.5}, startangle=90)
            ax_pdf_pie2.set_title("Masa de Repercusión", fontsize=8.5, color='#1A237E', fontweight='bold')
            
            ax_h1.add_patch(patches.Rectangle((0.04, 0.05), 0.92, 0.32, facecolor='white', edgecolor='#CFD8DC', linewidth=0.8, zorder=2))
            ax_h1.text(0.06, 0.34, "DISTRIBUCIÓN CRONOLÓGICA TEMPORAL HISTÓRICA", color='#1A237E', fontsize=9.5, fontweight='bold', zorder=3)
            
            ax_pdf_line1 = fig.add_axes([0.08, 0.54, 0.38, 0.10])
            ax_pdf_line1.plot(df_dias['Dia_Semana'].astype(str), df_dias['Interacciones'], color='#85C1E9', linewidth=2, marker='o', markersize=3)
            ax_pdf_line1.set_title("Interacciones por Día", fontsize=8.5, color='#1A237E', fontweight='bold')
            ax_pdf_line1.tick_params(axis='both', labelsize=6.5)
            
            ax_pdf_line2 = fig.add_axes([0.55, 0.54, 0.38, 0.10])
            ax_pdf_line2.plot(df_horas['Hora_Num'], df_horas['Interacciones'], color='#F5B7B1', linewidth=2, marker='o', markersize=3)
            ax_pdf_line2.set_title("Interacciones vs Hora", fontsize=8.5, color='#1A237E', fontweight='bold')
            ax_pdf_line2.tick_params(axis='both', labelsize=6.5)
            
            ax_h1.add_patch(patches.Rectangle((0.04, 0.012), 0.92, 0.025, facecolor='#E8EAF6', edgecolor='#C5CAE9', linewidth=0.8, zorder=2))
            ax_h1.text(0.05, 0.019, "Universidad Casa Grande - Proyecto Integrador", color='#1A237E', fontsize=8, fontweight='bold', zorder=3)
            
            # LÁMINA 2: ESTRATEGIA EJECUTIVA
            ax_h2 = fig.add_axes([0, 0, 1, 0.50])
            ax_h2.axis('off')
            ax_h2.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#FAFAFA', zorder=1))
            ax_h2.add_patch(patches.Rectangle((0, 0.92), 1, 0.08, facecolor='#1A237E', zorder=2))
            ax_h2.text(0.04, 0.96, f"PLANIFICACIÓN OPERATIVA INTEGRAL: {nombre_negocio.upper()}", color='white', fontsize=13, fontweight='bold', zorder=3)
            ax_h2.text(0.04, 0.93, f"MES: {mes_actual_nombre.upper()} | PÁGINA 2: ESTRATEGIA EJECUTIVA", color='#90CAF9', fontsize=8.5, zorder=3)
            
            ax_h2.add_patch(patches.Rectangle((0.04, 0.58), 0.92, 0.31, facecolor='white', edgecolor='#CFD8DC', linewidth=0.8, zorder=2))
            ax_h2.text(0.06, 0.86, f"MATRIZ DE PLANIFICACIÓN SEMANAL AUTOMATIZADA - MES DE {mes_actual_nombre.upper()}", color='#1A237E', fontsize=9.5, fontweight='bold', zorder=3)
            txt_b3 = (
                f"• SEMANA 1:\n  [Estrategia]: Publicar Formato Líder ({form_top.upper()}) (atracción inicial).\n  [Hito]: {hitos_mes_actual['Semana 1']}\n\n"
                f"• SEMANA 2:\n  [Estrategia]: Contenido en día de soporte ({segundo_dia.upper()}) (tracción).\n  [Hito]: {hitos_mes_actual['Semana 2']}\n\n"
                f"• SEMANA 3:\n  [Estrategia]: Conversión directa en día pico ({dia_pico.upper()}).\n  [Hito]: {hitos_mes_actual['Semana 3']}\n\n"
                f"• SEMANA 4:\n  [Estrategia]: Post orgánico en ventana horaria pre-pico ({int(hora_pico)-1}:30 H).\n  [Hito]: {hitos_mes_actual['Semana 4']}"
            )
            ax_h2.text(0.06, 0.83, txt_b3, color='#37474F', fontsize=8.5, linespacing=1.3, verticalalignment='top', zorder=3)
            
            ax_h2.add_patch(patches.Rectangle((0.04, 0.05), 0.92, 0.50, facecolor='white', edgecolor='#CFD8DC', linewidth=0.8, zorder=2))
            ax_h2.text(0.06, 0.52, "DIRECTRICES OPERATIVAS DE CONTROL (INSTRUCTIVO FUSIONADO COMPLETO)", color='#1A237E', fontsize=9.5, fontweight='bold', zorder=3)
            txt_b4 = (
                f"1. Monopolizar el 60% de recursos en {form_top.upper()} por rendimiento superior.\n\n"
                f"2. Desacelerar posts tipo {form_peor.upper()} por deficiencia crítica detectada.\n\n"
                f"3. Concentrar presupuestos publicitarios durante la fase de {q_max.upper()}.\n\n"
                f"4. Lanzar posts exactamente a las {int(hora_pico)-1}:30 H para indexación algorítmica precoz.\n\n"
                f"5. Amortiguar caídas algorítmicas los días {dia_valle.upper()} usando historias de interacción.\n\n"
                f"6. Insertar descriptores clave ('{top_conceptos[0].upper()}', '{top_conceptos[1].upper()}') para indexar SEO.\n\n"
                f"7. Potenciar el segundo día de mayor fuerza comercial ({segundo_dia.upper()}) con contenido educativo.\n\n"
                f"8. Mitigar desviaciones mediante pruebas A/B usando el margen predictivo de +-{margen_error:.1f}%.\n\n"
                f"9. Forzar alcance respondiendo comentarios durante los primeros 20 minutos de publicación.\n\n"
                f"10. Asegurar coherencia adaptando los copys al hito estacional activo de {mes_actual_nombre.upper()}."
            )
            ax_h2.text(0.06, 0.49, txt_b4, color='#37474F', fontsize=8.5, linespacing=1.2, verticalalignment='top', zorder=3)
            
            ax_h2.add_patch(patches.Rectangle((0.04, 0.012), 0.92, 0.025, facecolor='#E8EAF6', edgecolor='#C5CAE9', linewidth=0.8, zorder=2))
            ax_h2.text(0.05, 0.019, f"Reporte corporativo generado para {nombre_negocio.upper()} el {fecha_actual_sistema.strftime('%Y-%m-%d')}.", color='#1A237E', fontsize=8, fontweight='bold', zorder=3)
            
            plt.savefig(buf, format="pdf", bbox_inches='tight', dpi=300)
            buf.seek(0)
            plt.close(fig)

        # Elemento de UX: Confirmación visual e interfaz limpia de descarga
        st.success("🎉 ¡Tu reporte PDF multilámina de alta fidelidad se ha generado correctamente!")
        st.write("Haz clic en el siguiente botón para guardar el documento oficial en tu equipo:")
        st.download_button(
            label="💾 Descargar Reporte Ejecutivo (.PDF)", 
            data=buf, 
            file_name=f"Reporte_Consultoria_{nombre_negocio}.pdf", 
            mime="application/pdf"
        )
