import requests
import time

class DexScreenerClient:
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex/tokens"

    def get_token_data(self, token_address):
        """
        Fetch token data from DexScreener by contract address.
        """
        try:
            url = f"{self.base_url}/{token_address}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                if not pairs:
                    return None
                
                # Sort by liquidity to find the main pair
                main_pair = sorted(pairs, key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)[0]
                
                base_token = main_pair.get('baseToken', {})
                info = main_pair.get('info', {})
                socials = info.get('socials', [])
                
                # Extract Twitter handle if available in socials
                x_handle = None
                for s in socials:
                    if s.get('type') == 'twitter':
                        url = s.get('url', '')
                        if 'twitter.com/' in url or 'x.com/' in url:
                            x_handle = url.split('/')[-1]
                
                return {
                    'name': base_token.get('name'),
                    'symbol': base_token.get('symbol'),
                    'address': base_token.get('address'),
                    'price_usd': main_pair.get('priceUsd'),
                    'liquidity': main_pair.get('liquidity', {}).get('usd'),
                    'volume_24h': main_pair.get('volume', {}).get('h24'),
                    'fdv': main_pair.get('fdv'),
                    'market_cap': main_pair.get('marketCap'),
                    'socials': socials,
                    'x_handle': x_handle,
                    'dex_link': main_pair.get('url'),
                    'pair_address': main_pair.get('pairAddress'),
                    'chain_id': main_pair.get('chainId')
                }
            return None
        except Exception as e:
            print(f"DexScreener Error: {e}")
            return None

if __name__ == "__main__":
    # Test with a known token (e.g. Zerebro on Base)
    client = DexScreenerClient()
    test_ca = "0x8a18357065C7B97A10543e2646D5FA89E752c6f1" # Just a placeholder
    data = client.get_token_data(test_ca)
    print(data)
