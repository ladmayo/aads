import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la interfaz
st.set_page_config(page_title="Inspector de Empalmes", layout="wide")

st.title("🔍 Consulta de Consumo por Instalación")
st.markdown("---")

# 2. Carga de datos (Ahora usa consumos.csv)
@st.cache_data
def cargar_datos():
    # Leemos el archivo nuevo
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
            n_serie = resultado['serie'].values[0]
            st.success(f"✅ **Instalación encontrada**")
            st.info(f"**Número de Serie:** {n_serie}")
            
            # 4. Preparar datos (mes_1 a mes_64)
            columnas_meses = [f"mes_{i}" for i in range(1, 65)]
            columnas_presentes = [c for c in columnas_meses if c in df.columns]
            
            if columnas_presentes:
                valores = pd.to_numeric(resultado[columnas_presentes].values.flatten(), errors='coerce')
                
                df_grafico = pd.DataFrame({
                    "Mes": [m.replace('_', ' ').title() for m in columnas_presentes],
                    "Consumo (kWh)": valores
                })

                # 5. Gráfico con ZOOM DESACTIVADO para móvil
                fig = px.line(
                    df_grafico, 
                    x="Mes", 
                    y="Consumo (kWh)", 
                    title=f"Historial de Consumo - {id_buscado}",
                    markers=True
                )
                
                # CONFIGURACIÓN ANTIZOOM:
                fig.update_layout(
                    dragmode=False,          # Desactiva el arrastre para hacer zoom
                    hovermode="x unified",   # Muestra el valor al pasar el dedo/mouse
                    xaxis=dict(fixedrange=True), # Bloquea el zoom en el eje X
                    yaxis=dict(fixedrange=True), # Bloquea el zoom en el eje Y
                    margin=dict(l=10, r=10, t=50, b=10)
                )
                
                fig.update_xaxes(nticks=12, tickangle=45)
                
                # Mostrar gráfico (el parámetro config desactiva la barra de herramientas molesta)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            with st.expander("Ver detalle técnico"):
                st.dataframe(resultado)
        else:
            st.warning(f"⚠️ No se encontró la instalación '{busqueda}'.")

except Exception as e:
    st.error(f"❌ Error: {e}")
