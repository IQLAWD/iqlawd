import requests
from iq_lawd.config import config

class AlchemyClient:
    def __init__(self, api_key=None, network="eth-mainnet"):
        self.api_key = api_key or config.ALCHEMY_API_KEY
        self.base_url = f"https://{network}.g.alchemy.com/v2/{self.api_key}"

    def get_asset_transfers(self, from_address, category=["external", "erc20"]):
        """
        Mengambil riwayat transfer aset untuk alamat tertentu.
        Useful untuk melacak aktivitas agen.
        """
        url = f"{self.base_url}"
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "fromAddress": from_address,
                    "category": category,
                    "withMetadata": True,
                    "excludeZeroValue": True,
                    "maxCount": "0x3e8" # 1000
                }
            ]
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("result", {}).get("transfers", [])
        except Exception as e:
            print(f"Error fetching transfers from Alchemy: {e}")
            return []

    def get_token_balances(self, address):
        """
        Mengecek saldo token untuk melihat eksposur risiko agen.
        """
        url = f"{self.base_url}"
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenBalances",
            "params": [address]
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("result", {})
        except Exception as e:
            print(f"Error fetching balances: {e}")
            return {}
