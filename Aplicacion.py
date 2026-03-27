import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la interfaz
st.set_page_config(page_title="Inspector de Empalmes", layout="wide")

st.title("🔍 Consulta de Consumo por Instalación")
st.markdown("---")

# 2. Carga de datos optimizada
@st.cache_data
def cargar_datos():
    import os
    archivo = "consumos.csv"
    
    # Verificación de seguridad
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"El archivo {archivo} no existe en el servidor.")
        
    if os.path.getsize(archivo) == 0:
        raise ValueError("El archivo 'datos.csv' está vacío (0 bytes).")

    # Intentamos leer con diferentes configuraciones
    try:
        # Forzamos la lectura ignorando errores de líneas mal formadas
        df = pd.read_csv(archivo, sep=',', on_bad_lines='skip', engine='python', dtype=str)
        if df.empty:
            raise ValueError("El DataFrame resultó vacío después de leer el CSV.")
        return df
    except Exception as e:
        # Si falla el anterior, intentamos una lectura ultra-básica
        return pd.read_csv(archivo, dtype=str)

try:
    df = cargar_datos()

    # 3. Buscador
    busqueda = st.text_input("Ingrese el número de Instalación (ID):", placeholder="Ej: C096752 o 102226007")

    if busqueda:
        # Limpiar espacios del usuario y buscar coincidencia exacta sin importar mayúsculas
        id_buscado = busqueda.strip().upper()
        resultado = df[df['instalacion'].str.upper() == id_buscado]

        if not resultado.empty:
            # Mostrar la serie
            n_serie = resultado['serie'].values[0]
            st.success(f"✅ **Instalación encontrada**")
            st.info(f"**Número de Serie:** {n_serie}")
            
            # 4. Preparar datos de los 64 meses
            columnas_meses = [f"mes_{i}" for i in range(1, 65)]
            # Solo usamos las columnas que realmente existan en el CSV
            columnas_presentes = [c for c in columnas_meses if c in df.columns]
            
            if columnas_presentes:
                # Convertimos los consumos a números para poder graficar
                valores = pd.to_numeric(resultado[columnas_presentes].values.flatten(), errors='coerce')
                
                df_grafico = pd.DataFrame({
                    "Mes": [m.replace('_', ' ').title() for m in columnas_presentes],
                    "Consumo (kWh)": valores
                })

                # 5. Gráfico interactivo
                fig = px.line(
                    df_grafico, 
                    x="Mes", 
                    y="Consumo (kWh)", 
                    title=f"Historial de Consumo - Instalación {id_buscado}",
                    markers=True,
                    line_shape="linear"
                )
                
                # Mejoras visuales para el celular
                fig.update_xaxes(nticks=15, tickangle=45)
                fig.update_layout(
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar tabla completa si se desea
            with st.expander("Ver detalle técnico completo"):
                st.write(resultado)
        else:
            st.warning(f"⚠️ No se encontró la instalación '{busqueda}'. Verifique si incluye letras (ej: C096752).")

except Exception as e:
    st.error(f"❌ Error al cargar la aplicación: {e}")
    st.info("Asegúrate de que el archivo se llame 'datos.csv' y esté en la raíz de tu GitHub.")
