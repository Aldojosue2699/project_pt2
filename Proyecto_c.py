import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import socket

# Configuración de la página
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("Análisis Histórico de Acciones (2010-2024)")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("15 Years Stock Data of NVDA AAPL MSFT GOOGL and AMZN.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df.copy()

df = load_data()

# Sidebar con controles
st.sidebar.header("Parámetros de Visualización")

# Mostrar IP local y puerto estimado
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
port = 8501  # Cambia esto si usas otro puerto en ejecución
st.sidebar.markdown(f"🔗 [Abrir app en navegador](http://{local_ip}:{port})")
st.sidebar.info(f"URL local: http://{local_ip}:{port}")

tickers = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'NVDA']
selected_tickers = st.sidebar.multiselect(
    'Seleccione empresas:',
    tickers,
    default=['AAPL', 'NVDA']
)

date_range = st.sidebar.date_input(
    "Rango de fechas:",
    value=[df['Date'].min(), df['Date'].max()],
    min_value=df['Date'].min(),
    max_value=df['Date'].max()
)

price_type = st.sidebar.radio(
    "Tipo de precio:",
    ['Close', 'Open', 'High', 'Low'],
    horizontal=True
)

# Filtrar datos por fechas
filtered_df = df[(df['Date'] >= pd.to_datetime(date_range[0])) & 
                 (df['Date'] <= pd.to_datetime(date_range[1]))]

# Validación de datos
if filtered_df.empty or len(selected_tickers) == 0:
    st.warning("No hay datos disponibles para los filtros seleccionados.")
    st.stop()

# Mostrar métricas
st.header("Métricas Clave")
if len(filtered_df) >= 2:
    cols = st.columns(len(selected_tickers))
    for idx, ticker in enumerate(selected_tickers):
        with cols[idx]:
            latest = filtered_df.iloc[-1]
            previous = filtered_df.iloc[-2]
            close_now = latest[f'Close_{ticker}']
            close_prev = previous[f'Close_{ticker}']
            delta = (close_now - close_prev) / close_prev * 100
            st.metric(
                label=f"Último cierre - {ticker}",
                value=f"${close_now:.2f}",
                delta=f"{delta:.2f}%",
                delta_color="inverse" if delta < 0 else "normal"
            )
else:
    st.info("No hay suficientes datos para mostrar métricas.")

# Evolución de precios
st.header("Evolución de Precios")
fig = go.Figure()
for ticker in selected_tickers:
    fig.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df[f'{price_type}_{ticker}'],
        name=ticker,
        mode='lines'
    ))
fig.update_layout(
    hovermode="x unified",
    height=500,
    yaxis_title="Precio (USD)"
)
st.plotly_chart(fig, use_container_width=True)

# Gráfico de velas
st.header("Análisis Técnico - Gráficos de Velas")

def create_candlestick(ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=filtered_df['Date'],
        open=filtered_df[f'Open_{ticker}'],
        high=filtered_df[f'High_{ticker}'],
        low=filtered_df[f'Low_{ticker}'],
        close=filtered_df[f'Close_{ticker}'],
        name=ticker
    ))
    fig.update_layout(
        title=f'Gráfico de Velas - {ticker}',
        xaxis_rangeslider_visible=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

candle_cols = st.columns(len(selected_tickers))
for idx, ticker in enumerate(selected_tickers):
    with candle_cols[idx]:
        st.plotly_chart(create_candlestick(ticker), use_container_width=True)

# Gráfico de volumen
st.header("Volumen de Trading")
volume_fig = make_subplots(specs=[[{"secondary_y": True}]])
for ticker in selected_tickers:
    volume_fig.add_trace(go.Bar(
        x=filtered_df['Date'],
        y=filtered_df[f'Volume_{ticker}'],
        name=f'Volumen {ticker}',
        opacity=0.3
    ), secondary_y=False)
volume_fig.update_layout(
    barmode='stack',
    height=400,
    showlegend=True
)
st.plotly_chart(volume_fig, use_container_width=True)

# Mostrar datos brutos
if st.checkbox("Mostrar datos brutos"):
    st.subheader("Datos Históricos")
    st.dataframe(filtered_df, use_container_width=True)
