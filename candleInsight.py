import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def download_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date)

def transform_data(data):
    data['Month-Year'] = data.index.to_period('M')
    monthly_data = data.resample('M').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
    return monthly_data

def display_data_in_streamlit(ticker, start_date, end_date, monthly_data):
    overall_min = monthly_data['Low'].min()
    overall_max = monthly_data['High'].max()

    st.write(f"Valores mensais para {ticker.upper()} entre {start_date} e {end_date}")
    monthly_summary = monthly_data[['Low', 'High']].rename(columns={'Low': 'Min_Close', 'High': 'Max_Close'})
    monthly_summary.index = monthly_summary.index.strftime('%d/%m/%Y')
    st.table(monthly_summary)

    st.write(f"Resumo global para {ticker.upper()} entre {start_date} e {end_date}")
    overall_data = pd.DataFrame({"Tipo": ["Menor Preço", "Maior Preço"], "Valor": [overall_min, overall_max]})
    st.table(overall_data)

    fig = go.Figure(data=[go.Candlestick(
        x=monthly_data.index.strftime('%d/%m/%Y'),
        open=monthly_data['Open'],
        high=monthly_data['High'],
        low=monthly_data['Low'],
        close=monthly_data['Close'],
        increasing_line_color='green', 
        decreasing_line_color='red'
    )])

    fig.add_hline(y=overall_min, line=dict(color='blue', dash='dash'), annotation_text="Menor Preço")
    fig.add_hline(y=overall_max, line=dict(color='purple', dash='dash'), annotation_text="Maior Preço")

    fig.update_layout(title=f"Gráfico Candlestick Mensal de {ticker.upper()}",
                      xaxis_title="Data", yaxis_title="Preço",
                      xaxis_rangeslider_visible=False)

    st.plotly_chart(fig)

def main():
    st.title("Yahoo Finance Data Viewer")

    # Inputs do usuário
    ticker = st.text_input("Digite o ticker do ativo:")
    start_date = st.date_input("Digite a data inicial:")
    end_date = st.date_input("Digite a data final:")

    if ticker and start_date and end_date:
        data = download_data(ticker, start_date, end_date)
        if not data.empty:
            monthly_data = transform_data(data)
            display_data_in_streamlit(ticker, start_date, end_date, monthly_data)
        else:
            st.write("Não foi possível recuperar dados para o ticker especificado.")

if __name__ == "__main__":
    main()
