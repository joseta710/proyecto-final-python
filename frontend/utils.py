import requests
import streamlit as st
from typing import Dict, Optional
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

API_BASE_URL = "http://localhost:8000"

def get_currency_flag_emoji(currency_code: str) -> str:
    """Obtener emoji de bandera para el código de moneda"""
    flag_map = {
        'USD': '🇺🇸', 'EUR': '🇪🇺', 'GBP': '🇬🇧', 'JPY': '🇯🇵',
        'AUD': '🇦🇺', 'CAD': '🇨🇦', 'CHF': '🇨🇭', 'CNY': '🇨🇳',
        'COP': '🇨🇴', 'MXN': '🇲🇽', 'BRL': '🇧🇷', 'ARS': '🇦🇷'
    }
    return flag_map.get(currency_code.upper(), '💰')

@st.cache_data(ttl=300)
def fetch_supported_currencies():
    """Obtener lista de monedas soportadas desde la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/currencies", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error obteniendo monedas: {e}")
        return None

def convert_currency_api(from_curr: str, to_curr: str, amount: float) -> Optional[Dict]:
    """Convertir moneda usando la API"""
    try:
        params = {
            "from_currency": from_curr,
            "to_currency": to_curr,
            "amount": amount
        }
        response = requests.get(f"{API_BASE_URL}/convert", params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error de conversión: {response.json().get('detail', 'Error desconocido')}")
            return None
    except Exception as e:
        st.error(f"Error conectando con la API: {e}")
        return None

def format_currency(amount: float, currency: str) -> str:
    """Formatear cantidad con símbolo de moneda"""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
        'COP': '$', 'MXN': '$', 'CAD': 'C$', 'AUD': 'A$'
    }
    symbol = symbols.get(currency.upper(), currency.upper())
    
    if currency.upper() == 'JPY':
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

def display_conversion_result(result: Dict):
    """Mostrar resultado de conversión de manera atractiva"""
    if not result:
        return
    
    from_flag = get_currency_flag_emoji(result['from_currency'])
    to_flag = get_currency_flag_emoji(result['to_currency'])
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric(
            label=f"{from_flag} {result['from_currency']}",
            value=format_currency(result['original_amount'], result['from_currency'])
        )
    
    with col2:
        st.markdown(
            """
            <div style='text-align: center; padding: 20px; font-size: 24px;'>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.metric(
            label=f"{to_flag} {result['to_currency']}",
            value=format_currency(result['converted_amount'], result['to_currency']),
            delta=f"Tasa: {result['exchange_rate']:.4f}"
        )

def check_api_health() -> bool:
    """Verificar si la API está funcionando"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False