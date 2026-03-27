import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la interfaz
st.set_page_config(page_title="Inspector de Empalmes", layout="wide")

st.title("🔍 Consulta de Consumo por Instalación")
st.markdown("---")

# 2. Carga de datos
@st.cache_data
def cargar_datos():
    # Leemos el archivo consumos.csv
    df = pd.read_csv("consumos.csv", dtype=str)
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()

    # 3. Buscador
    busqueda = st.text_input("Ingrese el número de Instalación (ID):", placeholder="Ej: C096752")

    if busqueda:
        id_buscado = busqueda.strip().upper()
        resultado = df[df['instalacion'].str.upper() == id_buscado]

        if not resultado.empty:
            # Extraemos el valor limpio de la serie
            n_serie = resultado['serie'].values[0]
            st.success(f"✅ **Instalación encontrada**")
            st.info(f"**Número de Serie:** {n_serie}")
            
            # 4. Preparar datos (mes_1 a mes_64)
            columnas_meses = [f"mes_{i}" for i in range(1, 65)]
            columnas_presentes = [c for c in columnas_meses if c in df.columns]
            
            if columnas_presentes:
                # Convertir consumos a numérico para graficar
                valores = pd.to_numeric(resultado[columnas_presentes].values.flatten(), errors='coerce')
                
                df_grafico = pd.DataFrame({
                    "Mes": [m.replace('_', ' ').title() for m in columnas_presentes],
                    "Consumo (kWh)": valores
                })

                # 5. Gráfico de Área SIN puntos y SIN etiquetas amontonadas
                fig = px.area(
                    df_grafico, 
                    x="Mes", 
                    y="Consumo (kWh)", 
                    title=f"Historial de Consumo - {id_buscado}",
                    template="plotly_white"
                )
                
                # Configuración visual táctil y limpia
                fig.update_traces(
                    mode='lines',        # Solo líneas, sin puntos
                    line_width=2,
                    line_color='#007BFF', 
                    fillcolor='rgba(0, 123, 255, 0.1)'
                )

                fig.update_layout(
                    height=400,          # Altura optimizada para móvil
                    dragmode=False,      # Desactiva zoom por arrastre
                    hovermode="x unified",
                    xaxis=dict(
                        fixedrange=True,      # Bloquea zoom manual
                        showticklabels=False, # OCULTA "Mes 1", "Mes 2", etc.
                        showgrid=False,       
                        title=""              
                    ),
                    yaxis=dict(
                        fixedrange=True,      # Bloquea zoom manual
                        gridcolor="#f0f0f0",
                        title="kWh"
                    ),
                    margin=dict(l=5, r=5, t=40, b=5) # Márgenes mínimos para ganar ancho
                )
                
                # Renderizar gráfico sin barra de herramientas
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            with st.expander("Ver detalle técnico"):
                st.dataframe(resultado)
        else:
            st.warning(f"⚠️ No se encontró la instalación '{busqueda}'.")

except Exception as e:
    st.error(f"❌ Error: {e}")
