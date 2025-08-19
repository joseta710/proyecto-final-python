from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Añadir el directorio padre al path para importar shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.api_client import ExchangeRateClient

# Crear la aplicación FastAPI
app = FastAPI(
    title="Currency Converter API",
    description="API para conversión de monedas en tiempo real",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el cliente de la API
client = ExchangeRateClient()

@app.get("/")
def root():
    """Endpoint de verificación de salud de la API"""
    return {
        "message": "Currency Converter API is running!",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/convert")
def convert_currency(
    from_currency: str = Query(..., description="Moneda de origen (ej: USD)"),
    to_currency: str = Query(..., description="Moneda de destino (ej: EUR)"),
    amount: float = Query(..., gt=0, description="Cantidad a convertir")
):
    """Convertir una cantidad de una moneda a otra"""
    try:
        result = client.convert(from_currency, to_currency, amount)
        
        if result is None:
            raise HTTPException(
                status_code=400,
                detail="No se pudo realizar la conversión. Verifica las monedas ingresadas."
            )
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/rates/{base_currency}")
def get_exchange_rates(base_currency: str):
    """Obtener todas las tasas de cambio para una moneda base"""
    try:
        result = client.get_rates(base_currency)
        
        if result is None:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontraron tasas para la moneda: {base_currency}"
            )
        
        return {
            "base_currency": result['base'],
            "rates": result['rates'],
            "timestamp": result.get('date', '')
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo tasas: {str(e)}"
        )

@app.get("/currencies")
def get_supported_currencies():
    """Obtener lista de monedas soportadas y populares"""
    try:
        rates_data = client.get_rates("USD")
        popular = client.get_popular_currencies()
        
        if rates_data and 'rates' in rates_data:
            all_currencies = list(rates_data['rates'].keys())
        else:
            all_currencies = []
        
        return {
            "total_currencies": len(all_currencies),
            "all_currencies": sorted(all_currencies),
            "popular_currencies": popular,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo monedas: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)