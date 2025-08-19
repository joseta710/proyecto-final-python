import requests
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class ExchangeRateClient:
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4"
        self.api_key = os.getenv("API_KEY")
        
    def get_rates(self, base_currency: str = "USD") -> Optional[Dict]:
        """Obtener todas las tasas de cambio para una moneda base"""
        try:
            url = f"{self.base_url}/latest/{base_currency.upper()}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting rates: {e}")
            return None
    
    def convert(self, from_currency: str, to_currency: str, amount: float) -> Optional[Dict]:
        """Convertir entre dos monedas"""
        try:
            rates_data = self.get_rates(from_currency)
            if not rates_data or 'rates' not in rates_data:
                return None
            
            if to_currency.upper() not in rates_data['rates']:
                return None
                
            rate = rates_data['rates'][to_currency.upper()]
            converted_amount = amount * rate
            
            return {
                "from_currency": from_currency.upper(),
                "to_currency": to_currency.upper(),
                "original_amount": amount,
                "converted_amount": round(converted_amount, 4),
                "exchange_rate": rate,
                "timestamp": rates_data.get('date', '')
            }
        except Exception as e:
            print(f"Error converting: {e}")
            return None
    
    def get_popular_currencies(self) -> Dict[str, str]:
        """Obtener monedas más populares con sus nombres"""
        return {
            "USD": "US Dollar",
            "EUR": "Euro",
            "GBP": "British Pound",
            "JPY": "Japanese Yen",
            "AUD": "Australian Dollar",
            "CAD": "Canadian Dollar",
            "CHF": "Swiss Franc",
            "CNY": "Chinese Yuan",
            "COP": "Colombian Peso",
            "MXN": "Mexican Peso"
        }