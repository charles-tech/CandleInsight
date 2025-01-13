import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def main():
    st.title("Yahoo Finance Data Viewer")

    # Inputs do usuário
    ticker = st.text_input("Digite o ticker do ativo:")
    start_date = st.date_input("Digite a data inicial:")
    end_date = st.date_input("Digite a data final:")

    if ticker and start_date and end_date:
        # Download dos dados
        data = yf.download(ticker, start=start_date, end=end_date)

        if not data.empty:
            # Certifica-se que todas as colunas necessárias estão presentes
            required_columns = {'Open', 'High', 'Low', 'Close'}
            if required_columns.issubset(data.columns):
                # Agrupa por mês para captura da primeira abertura e último fechamento dos meses
                monthly_data = data.resample('M').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last'
                })

                # Calcula o menor e o maior preço no período todo
                overall_min = monthly_data['Low'].min()
                overall_max = monthly_data['High'].max()

                # Mostra resultados da tabela com valores mensais formatados
                st.write(f"Valores mensais para {ticker.upper()} entre {start_date} e {end_date}")
                monthly_summary = monthly_data[['Open', 'Low', 'High', 'Close']]
                monthly_summary.index = monthly_summary.index.strftime('%d/%m/%Y')
                st.table(monthly_summary)

                # Mostra resultados da segunda tabela
                st.write(f"Resumo global para {ticker.upper()} entre {start_date} e {end_date}")
                overall_data = pd.DataFrame({
                    "Tipo": ["Menor Preço", "Maior Preço"],
                    "Valor": [overall_min, overall_max]
                })
                st.table(overall_data)

                # Gráfico Candlestick Mensal
                fig = go.Figure(data=[go.Candlestick(
                    x=monthly_data.index.strftime('%d/%m/%Y'),
                    open=monthly_data['Open'],
                    high=monthly_data['High'],
                    low=monthly_data['Low'],
                    close=monthly_data['Close'],
                    increasing_line_color='green', 
                    decreasing_line_color='red'
                )])

                # Adiciona linhas horizontais para menor e maior preço
                fig.add_hline(y=overall_min, line=dict(color='blue', dash='dash'), annotation_text="Menor Preço")
                fig.add_hline(y=overall_max, line=dict(color='purple', dash='dash'), annotation_text="Maior Preço")

                fig.update_layout(title=f"Gráfico Candlestick Mensal de {ticker.upper()}",
                                  xaxis_title="Data",
                                  yaxis_title="Preço",
                                  xaxis_rangeslider_visible=False)

                st.plotly_chart(fig)
            else:
                st.write("Dados insuficientes para criar o gráfico. Verifique se todos os campos de preço estão baixados.")
        else:
            st.write("Não foi possível recuperar dados para o ticker especificado.")

# Executa a aplicação
if __name__ == "__main__":
    main()
