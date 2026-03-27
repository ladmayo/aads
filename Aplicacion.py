import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la interfaz
st.set_page_config(page_title="Inspector de Empalmes", layout="wide")

st.title("🔍 Consulta de Consumo")
st.markdown("---")

# 2. Carga de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("consumos.csv", dtype=str)
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()

    # 3. Buscador Dual (Instalación o Serie)
    busqueda = st.text_input(
        "Ingrese ID de Instalación o Número de Serie del Medidor:", 
        placeholder="Ej: C096752 o 36068355"
    )

    if busqueda:
        id_buscado = busqueda.strip().upper()
        
        # Filtramos si coincide en cualquiera de las dos columnas
        resultado = df[
            (df['instalacion'].str.upper() == id_buscado) | 
            (df['serie'].str.upper() == id_buscado)
        ]

        if not resultado.empty:
            # Si hay más de un resultado (raro, pero posible), tomamos el primero
            datos_fila = resultado.iloc[0]
            
            st.success(f"✅ **Información Encontrada**")
            
            # Mostramos ambos datos para confirmar
            col1, col2 = st.columns(2)
            col1.metric("ID Instalación", datos_fila['instalacion'])
            col2.metric("N° de Serie", datos_fila['serie'])
            
            # 4. Preparar datos (mes_1 a mes_64)
            columnas_meses = [f"mes_{i}" for i in range(1, 65)]
            columnas_presentes = [c for c in columnas_meses if c in df.columns]
            
            if columnas_presentes:
                valores = pd.to_numeric(resultado[columnas_presentes].values.flatten(), errors='coerce')
                
                df_grafico = pd.DataFrame({
                    "Mes": [m.replace('_', ' ').title() for m in columnas_presentes],
                    "Consumo (kWh)": valores
                })

                # 5. Gráfico de Área optimizado
                fig = px.area(
                    df_grafico, 
                    x="Mes", 
                    y="Consumo (kWh)", 
                    title=f"Perfil de Consumo - Serie {datos_fila['serie']}",
                    template="plotly_white"
                )
                
                fig.update_traces(
                    mode='lines',
                    line_width=2,
                    line_color='#007BFF', 
                    fillcolor='rgba(0, 123, 255, 0.1)'
                )

                fig.update_layout(
                    height=400,
                    dragmode=False,
                    hovermode="x unified",
                    xaxis=dict(
                        fixedrange=True,
                        showticklabels=False,
                        showgrid=False,
                        title=""
                    ),
                    yaxis=dict(
                        fixedrange=True,
                        gridcolor="#f0f0f0",
                        title="kWh"
                    ),
                    margin=dict(l=5, r=5, t=40, b=5)
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            with st.expander("Ver detalle técnico completo"):
                st.write(resultado)
        else:
            st.warning(f"⚠️ No se encontró registro para '{busqueda}'.")

except Exception as e:
    st.error(f"❌ Error: {e}")
