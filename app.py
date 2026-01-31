import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(page_title="Análise de Sentenças", layout="wide")

st.title("100 Acidentes de Trânsito em Piracicaba")
st.subheader("Visualização Georreferenciada de Sentenças")

# 1. Função para carregar e limpar os dados
@st.cache_data
def load_data():
    file_path = 'sentencas_georreferenciadas.csv'
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        header = f.readline() # Pular cabeçalho
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 6: continue

            # Extraindo campos relevantes        
            wkt = parts[0]
            processo = parts[1]
            data_fato = parts[2]
            lat = float(parts[-2])
            lon = float(parts[-1])
            conduta = ",".join(parts[3:-2])
            
            data.append([processo, data_fato, conduta, lat, lon])
            
    return pd.DataFrame(data, columns=['Processo', 'Data', 'Conduta_Culposa', 'lat', 'lon'])

df = load_data()

# 2. Sidebar para filtros
st.sidebar.header("Configurações do Mapa")
tipo_mapa = st.sidebar.radio(
    "Selecione o tipo de visualização:",
    ["Cluster de Marcadores", "Mapa de Calor"]
)

# 3. Criação do Mapa com Folium
# Centralizando o mapa na média das coordenadas
mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=13)

if tipo_mapa == "Cluster de Marcadores":
    marker_cluster = MarkerCluster().add_to(mapa)
    for _, row in df.iterrows():
        # Criando o pop-up com a informação da conduta culposa
        popup_text = f"<b>Processo:</b> {row['Processo']}<br><b>Conduta:</b> {row['Conduta_Culposa']}"
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(marker_cluster)

elif tipo_mapa == "Mapa de Calor":
    # Preparando dados para o heatmap
    heat_data = [[row['lat'], row['lon']] for _, row in df.iterrows()]
    HeatMap(heat_data).add_to(mapa)
    
# 4. Exibição no Streamlit
st_folium(mapa, width=1200, height=600, returned_objects=[])