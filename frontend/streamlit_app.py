import streamlit as st
import time
from utils import (
    fetch_supported_currencies,
    convert_currency_api,
    display_conversion_result,
    check_api_health,
    get_currency_flag_emoji,
    format_currency
)

st.set_page_config(
    page_title="Currency Converter",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
    <div class="main-header">
        <h1>Currency Converter Pro</h1>
        <p>Convierte monedas en tiempo real con tasas actualizadas</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not check_api_health():
        st.error("""
         **Error de Conexión**
        
        No se puede conectar con la API. Asegúrate de que el backend esté ejecutándose:
        
        ```bash
        cd backend
        uvicorn main:app --reload --port 8000
        ```
        """)
        st.stop()
    
    with st.sidebar:
        st.header("Configuración")
        st.success("API Conectada")
        
        currency_data = fetch_supported_currencies()
        
        if currency_data:
            st.info(f"{currency_data['total_currencies']} monedas disponibles")
            
            mode = st.selectbox(
                "Modo de operación:",
                ["Conversor Simple", "Tasas Populares"]
            )
        else:
            st.error("Error cargando datos")
            st.stop()
    
    if mode == "Conversor Simple":
        show_simple_converter(currency_data)
    else:
        show_popular_rates(currency_data)

def show_simple_converter(currency_data):
    """Mostrar el conversor simple"""
    st.subheader("Conversor de Monedas")
    
    popular_currencies = list(currency_data['popular_currencies'].keys())
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        from_currency = st.selectbox(
            "Desde:",
            popular_currencies,
            index=popular_currencies.index("USD") if "USD" in popular_currencies else 0,
            format_func=lambda x: f"{get_currency_flag_emoji(x)} {x} - {currency_data['popular_currencies'].get(x, x)}"
        )
    
    with col2:
        to_currency = st.selectbox(
            "Hacia:",
            popular_currencies,
            index=popular_currencies.index("EUR") if "EUR" in popular_currencies else 1,
            format_func=lambda x: f"{get_currency_flag_emoji(x)} {x} - {currency_data['popular_currencies'].get(x, x)}"
        )
    
    with col3:
        amount = st.number_input(
            "Cantidad:",
            min_value=0.01,
            value=100.0,
            step=0.01
        )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        convert_btn = st.button("Convertir", use_container_width=True, type="primary")
    
    if convert_btn:
        with st.spinner("Convirtiendo..."):
            result = convert_currency_api(from_currency, to_currency, amount)
            
            if result:
                st.balloons()
                display_conversion_result(result)
                
                st.info(f" Tasa actualizada el: {result.get('timestamp', 'N/A')}")
            else:
                st.error(" No se pudo realizar la conversión")

def show_popular_rates(currency_data):
    """Mostrar tasas de monedas populares"""
    st.subheader(" Tasas de Cambio Populares")
    
    import requests
    try:
        response = requests.get("http://localhost:8000/rates/USD", timeout=10)
        if response.status_code == 200:
            rates_data = response.json()
            
            st.info(f"Tasas actualizadas: {rates_data.get('timestamp', 'N/A')}")
            
            popular_currencies = currency_data['popular_currencies']
            rates_list = []
            
            for curr_code, curr_name in popular_currencies.items():
                if curr_code in rates_data['rates']:
                    rate = rates_data['rates'][curr_code]
                    rates_list.append({
                        "Moneda": f"{get_currency_flag_emoji(curr_code)} {curr_code}",
                        "Nombre": curr_name,
                        "Tasa (USD)": f"{rate:.4f}",
                        "100 USD =": format_currency(100 * rate, curr_code)
                    })
            
            if rates_list:
                import pandas as pd
                df = pd.DataFrame(rates_list)
                st.dataframe(df, use_container_width=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    eur_rate = rates_data['rates'].get('EUR', 0)
                    st.metric(
                        label="🇪🇺 EUR",
                        value=f"{eur_rate:.4f}",
                        delta="Euro"
                    )
                
                with col2:
                    cop_rate = rates_data['rates'].get('COP', 0)
                    st.metric(
                        label="🇨🇴 COP",
                        value=f"{cop_rate:.2f}",
                        delta="Peso Colombiano"
                    )
                
                with col3:
                    gbp_rate = rates_data['rates'].get('GBP', 0)
                    st.metric(
                        label="🇬🇧 GBP",
                        value=f"{gbp_rate:.4f}",
                        delta="Libra Esterlina"
                    )
                
                with col4:
                    jpy_rate = rates_data['rates'].get('JPY', 0)
                    st.metric(
                        label="🇯🇵 JPY",
                        value=f"{jpy_rate:.2f}",
                        delta="Yen Japonés"
                    )
        else:
            st.error(" No se pudieron obtener las tasas")
    
    except Exception as e:
        st.error(f" Error: {e}")

def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Currency Converter Pro | Desarrollado con FastAPI + Streamlit</p>
        <p>Datos proporcionados por ExchangeRate-API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()