import requests
import time

class GeckoTerminalClient:
    def __init__(self, network='base'):
        self.base_url = "https://api.geckoterminal.com/api/v2"
        self.network = network
        self.headers = {
            "Accept": "application/json"
        }

    def get_trending_pools(self):
        """Get trending pools on specific network"""
        try:
            url = f"{self.base_url}/networks/{self.network}/trending_pools"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return []
        except Exception as e:
            print(f"GeckoTerminal Error (Trending): {e}")
            return []

    def get_token_info(self, address):
        """Get token info including image"""
        try:
            url = f"{self.base_url}/networks/{self.network}/tokens/{address}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', {})
                attrs = data.get('attributes', {})
                return {
                    'name': attrs.get('name'),
                    'symbol': attrs.get('symbol'),
                    'image_url': attrs.get('image_url'),
                    'price_usd': attrs.get('price_usd'),
                    'volume_24h': attrs.get('volume_usd', {}).get('h24'),
                    'decimals': attrs.get('decimals')
                }
            return None
        except Exception as e:
            print(f"GeckoTerminal Error (Token Info): {e}")
            return None

    def get_ohlcv(self, pool_address, timeframe='hour'):
        """Get OHLCV content for charts"""
        try:
            # timeframe: day, hour, minute
            url = f"{self.base_url}/networks/{self.network}/pools/{pool_address}/ohlcv/{timeframe}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', {})
                return data.get('attributes', {}).get('ohlcv_list', [])
            return []
        except Exception as e:
            print(f"GeckoTerminal Error (OHLCV): {e}")
            return []
