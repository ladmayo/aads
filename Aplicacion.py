import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la interfaz
st.set_page_config(page_title="Inspector de Empalmes", layout="wide")

st.title("🔍 Consulta de Consumo por Instalación")
st.markdown("---")

# 2. Función optimizada para cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos.csv")

try:
    df = cargar_datos()

    # 3. Buscador
    busqueda = st.text_input("Ingrese el número de Instalación (ID):", placeholder="Ej: 123456")

    if busqueda:
        # Filtrado
        resultado = df[df['instalacion'].astype(str) == str(busqueda)]

        if not resultado.empty:
            medidor = resultado['numero de medidor'].values[0]
            st.info(f"**Medidor asociado:** {medidor}")
            
            # 4. Procesamiento de los 64 meses
            columnas_meses = [f"mes_{i}" for i in range(1, 65)]
            columnas_presentes = [c for c in columnas_meses if c in df.columns]
            
            if len(columnas_presentes) > 0:
                valores = resultado[columnas_presentes].values.flatten()
                
                df_grafico = pd.DataFrame({
                    "Mes": [m.replace('_', ' ').title() for m in columnas_presentes],
                    "Consumo (kWh)": valores
                })

                # 5. Gráfico
                fig = px.line(
                    df_grafico, 
                    x="Mes", 
                    y="Consumo (kWh)", 
                    title=f"Historial de Consumo - Instalación {busqueda}",
                    markers=True,
                    template="plotly_white"
                )
                
                fig.update_xaxes(nticks=15, tickangle=45)
                fig.update_layout(hovermode="x unified")
                
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Ver tabla de datos técnicos"):
                st.dataframe(resultado)
        else:
            st.warning("⚠️ No se encontró la instalación.")

except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'datos.csv'.")
except Exception as e:
    st.error(f"⚠️ Error: {e}")
