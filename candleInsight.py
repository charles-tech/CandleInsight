import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def download_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.warning(f"Nenhum dado foi retornado para o ticker {ticker}.")
        return data
    except Exception as e:
        st.error(f"Erro ao baixar dados: {e}")
        return pd.DataFrame()

def check_data_columns(data):
    # Conversão explícita de todas as entradas da lista para strings
    column_list = [str(col) for col in data.columns]
    st.write(f"Colunas disponíveis: {', '.join(column_list)}")

def transform_data(data):
    try:
        monthly_data = data.resample('M').agg({'Open': 'first', 
                                               'High': 'max', 
                                               'Low': 'min', 
                                               'Close': 'last'})
        return monthly_data
    except KeyError as ke:
        st.error(f"Erro ao realizar agregação dos dados. Erro: {ke}")
        return None

def display_data_in_streamlit(ticker, start_date, end_date, monthly_data):
    overall_min = monthly_data['Low'].min()
    overall_max = monthly_data['High'].max()

    st.write(f"Valores mensais para {ticker.upper()} entre {start_date} e {end_date}")
    monthly_summary = monthly_data[['Open', 'Low', 'High', 'Close']]
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
    
    ticker = st.text_input("Digite o ticker do ativo:")
    start_date = st.date_input("Digite a data inicial:")
    end_date = st.date_input("Digite a data final:")

    if ticker and start_date and end_date:
        data = download_data(ticker, start_date, end_date)
        
        if not data.empty:
            if {'Open', 'High', 'Low', 'Close'}.issubset(data.columns):
                monthly_data = transform_data(data)
                if monthly_data is not None:
                    display_data_in_streamlit(ticker, start_date, end_date, monthly_data)
                else:
                    st.write("Erro na transformação dos dados.")
            else:
                st.write("Um ou mais campos de dados estão faltando. Confira a integridade dos dados.")
                check_data_columns(data)
        else:
            st.write("Não foi possível recuperar dados para o ticker especificado.")

if __name__ == "__main__":
    main()
