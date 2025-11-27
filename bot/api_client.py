"""
Cliente HTTP para comunicarse con la API Django - SIMPLIFICADO
"""
import requests
from typing import Dict, List, Optional
from .config import API_URL, REQUEST_TIMEOUT, BOT_SECRET


REQUEST_TIMEOUT = 10


class APIClient:
    """Cliente para hacer requests a la API Django"""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
    
    # =============== AUTENTICACIÓN ===============
    
    def telegram_auth(self, chat_id: str, username: str = '') -> Optional[Dict]:
        """Autenticarse con Telegram (sin contraseña)"""
        try:
            url = f"{self.base_url}/users/telegram/auth/"
            headers = {'X-Bot-Token': BOT_SECRET}
            data = {
                "telegram_chat_id": chat_id,
                "telegram_username": username
            }
            response = requests.post(url, json=data, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            print(f"Error en telegram_auth: {e}")
            return None
    
    # =============== MENÚ ===============
    
    def get_menu(self) -> Optional[Dict]:
        """Obtener menú para el bot"""
        try:
            url = f"{self.base_url}/menu/categories/bot-menu/"
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error en get_menu: {e}")
            return None
    
    # =============== PEDIDOS ===============
    
    def create_order(self, token: str, lat: float, lon: float, items: List[Dict], 
                     notes: str = '', reference: str = '') -> Optional[Dict]:
        """Crear pedido"""
        try:
            url = f"{self.base_url}/orders/"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            data = {
                "delivery_latitude": lat,
                "delivery_longitude": lon,
                "delivery_reference": reference,
                "notes": notes,
                "items": items
            }
            response = requests.post(url, json=data, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error crear pedido: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error en create_order: {e}")
            return None
    
    def get_order(self, token: str, order_id: int) -> Optional[Dict]:
        """Obtener detalle de pedido"""
        try:
            url = f"{self.base_url}/orders/{order_id}/"
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error en get_order: {e}")
            return None
    
    # =============== PAGOS ===============
    
    def create_payment(self, token: str, order_id: int) -> Optional[Dict]:
        """Crear pago y generar QR"""
        try:
            url = f"{self.base_url}/payments/create_qr/"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            data = {"order_id": order_id}
            response = requests.post(url, json=data, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error crear pago: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error en create_payment: {e}")
            return None
    
    def confirm_payment(self, token: str, payment_id: int) -> Optional[Dict]:
        """Confirmar pago"""
        try:
            url = f"{self.base_url}/payments/{payment_id}/confirm/"
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post(url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error confirmar pago: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error en confirm_payment: {e}")
            return None
