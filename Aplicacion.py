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
            fila = resultado.iloc[0] # Tomamos la primera coincidencia
            
            st.success(f"✅ **Información Encontrada**")
            
            # Mostramos datos clave en tarjetas grandes
            col1, col2 = st.columns(2)
            col1.metric("ID Instalación", fila['instalacion'])
            col2.metric("N° de Serie", fila['serie'])
            
            # 4. Preparar datos (mes_1 a mes_64)
            columnas_totales = [f"mes_{i}" for i in range(1, 65)]
            columnas_presentes = [c for c in columnas_totales if c in df.columns]
            
            if columnas_presentes:
                # Convertir a numérico
                valores = pd.to_numeric(resultado[columnas_presentes].values.flatten(), errors='coerce')
                
                df_completo = pd.DataFrame({
                    "Mes": [m.replace('_', ' ').title() for m in columnas_presentes],
                    "Consumo": valores
                })

                # --- GRÁFICO 1: HISTÓRICO COMPLETO (64 meses) ---
                st.subheader("📅 Histórico Completo (64 Meses)")
                fig_hist = px.area(df_completo, x="Mes", y="Consumo", template="plotly_white")
                fig_hist.update_traces(mode='lines', line_color='#007BFF', fillcolor='rgba(0, 123, 255, 0.1)')
                fig_hist.update_layout(
                    height=300, dragmode=False, hovermode="x unified",
                    xaxis=dict(fixedrange=True, showticklabels=False, showgrid=False, title=""),
                    yaxis=dict(fixedrange=True, title="kWh"),
                    margin=dict(l=5, r=5, t=30, b=5)
                )
                st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})

                # --- GRÁFICO 2: ÚLTIMO AÑO (Detalle mes_53 a mes_64) ---
                st.subheader("📈 Detalle Último Año")
                # Filtramos las últimas 12 columnas (si existen)
                ultimos_12 = df_completo.tail(12)
                
                fig_det = px.line(ultimos_12, x="Mes", y="Consumo", markers=True, template="plotly_white")
                fig_det.update_traces(line_color='#28A745', line_width=3, marker=dict(size=8))
                fig_det.update_layout(
                    height=350, dragmode=False, hovermode="x unified",
                    xaxis=dict(fixedrange=True, tickangle=45, title=""),
                    yaxis=dict(fixedrange=True, title="kWh"),
                    margin=dict(l=5, r=5, t=30, b=5)
                )
                st.plotly_chart(fig_det, use_container_width=True, config={'displayModeBar': False})
            
            with st.expander("Ver tabla de datos brutos"):
                st.write(resultado)
        else:
            st.warning(f"⚠️ No se encontró registro para '{busqueda}'.")

except Exception as e:
    st.error(f"❌ Error: {e}")
