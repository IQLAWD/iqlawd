import requests
from iq_lawd.config import config

class MarketDataClient:
    def __init__(self):
        self.dex_url = config.DEXSCREENER_API_URL
        self.gecko_url = "https://api.geckoterminal.com/api/v2"
        self.birdeye_url = config.BIRDEYE_API_URL

    def get_token_profile(self, token_address):
        """
        Mengambil profil token. Sekarang memprioritaskan GeckoTerminal karena performa lebih stabil.
        """
        # 1. Coba GeckoTerminal Dulu (Seringkali lebih cepat & bypass Cloudflare issues)
        gecko_info = self.get_token_info_gecko(token_address)
        if gecko_info and gecko_info.get("status") == "GECKO_VERIFIED":
            print(f"GeckoTerminal hit for {token_address}")
            
            # ENRICHMENT: Fetch Socials from DexScreener if missing
            try:
                dex_url = f"{self.dex_url}/tokens/{token_address}"
                print(f"Enriching DexScreener data for socials...")
                dex_resp = requests.get(dex_url, timeout=3)
                if dex_resp.status_code == 200:
                    dex_data = dex_resp.json()
                    pairs = dex_data.get("pairs", [])
                    if pairs:
                        best_pair = pairs[0]
                        info = best_pair.get("info", {})
                        gecko_info["socials"] = info.get("socials", [])
                        gecko_info["websites"] = info.get("websites", [])
                        print(f"✅ Enriched {token_address} with {len(gecko_info['socials'])} socials.")
            except Exception as e:
                print(f"⚠️ Failed to enrich with DexScreener: {e}")
                
            return gecko_info

        # 2. Fallback ke DexScreener
        url = f"{self.dex_url}/tokens/{token_address}"
        try:
            print(f"DexScreener backup fetch for {token_address}...")
            response = requests.get(url, timeout=(2.0, 5.0)) # (Connect, Read)
            response.raise_for_status()
            data = response.json()
            pairs = data.get("pairs")
            
            if not pairs:
                # Ultimate Fallback for "Dark" tokens
                return {
                    "chainId": "base",
                    "dexId": "unknown",
                    "status": "UNINDEXED_TARGET",
                    "priceUsd": "0",
                    "liquidity": {"usd": 0},
                    "fdv": 0,
                    "priceChange": {"h24": 0, "h6": 0, "h1": 0, "m5": 0},
                    "volume": {"h24": 0},
                    "baseToken": {"symbol": "TOKEN", "address": token_address},
                    "socials": [],
                    "websites": []
                }
            
            # Mengambil pair dengan likuiditas tertinggi secara aman
            best_pair = max(pairs, key=lambda x: (x.get("liquidity") or {}).get("usd") or 0)
            best_pair["status"] = "ACTIVE_DATA"
            
            # Ensure safe fields
            best_pair["priceChange"] = (best_pair.get("priceChange") or 
                                       {"h24": 0, "h6": 0, "h1": 0, "m5": 0})
            best_pair["liquidity"] = (best_pair.get("liquidity") or {"usd": 0})
            
            # Tambahkan metadata sosial jika ada
            info = (best_pair.get("info") or {})
            best_pair["socials"] = info.get("socials", [])
            best_pair["websites"] = info.get("websites", [])
            
            return best_pair
        except Exception as e:
            print(f"Error fetching DexScreener data: {e}")
            return None

    def get_token_info_gecko(self, token_address):
        """
        Fallback ke GeckoTerminal untuk informasi dasar token.
        """
        url = f"{self.gecko_url}/networks/base/tokens/{token_address}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                attr = data.get("attributes", {})
                return {
                    "chainId": "base",
                    "status": "GECKO_VERIFIED",
                    "priceUsd": attr.get("base_token_price_usd", "0"),
                    "fdv": float(attr.get("fdv_usd") or 0),
                    "baseToken": {
                        "symbol": attr.get("symbol", "TOKEN"),
                        "name": attr.get("name"),
                        "address": token_address
                    },
                    "liquidity": {"usd": float(attr.get("total_reserve_in_usd") or 0)},
                    "priceChange": {"h24": 0, "h1": 0}, 
                    "volume": {"h24": 0}
                }
        except:
            pass
        return None

    def get_trending_tokens(self, limit=15):
        """
        Mengambil Top Trending Pools dari GeckoTerminal (Base Chain).
        """
        url = f"{self.gecko_url}/networks/base/trending_pools"
        results = []
        try:
            print("Fetching live trending data from GeckoTerminal...")
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            data = response.json().get("data", [])
            
            for pool in data[:limit]:
                attr = pool.get("attributes", {})
                relationships = pool.get("relationships", {})
                base_token_data = relationships.get("base_token", {}).get("data", {})
                
                # Normalize to our internal format
                token_address = base_token_data.get("id", "").split("_")[-1]
                symbol = attr.get("name", "").split(" / ")[0]
                
                results.append({
                    "chainId": "base",
                    "status": "LIVE_TRENDING",
                    "pairAddress": attr.get("address"),
                    "baseToken": {
                        "address": token_address,
                        "symbol": symbol
                    },
                    "priceUsd": attr.get("base_token_price_usd"),
                    "liquidity": {"usd": float(attr.get("reserve_in_usd") or 0)},
                    "fdv": float(attr.get("fdv_usd") or 0),
                    "priceChange": {"h24": float(attr.get("price_change_percentage", {}).get("h24") or 0)},
                    "volume": {"h24": float(attr.get("volume_usd", {}).get("h24") or 0)}
                })
            
            print(f"Successfully fetched {len(results)} live targets.")
            return results
        except Exception as e:
            print(f"Gecko Error: {e}. Falling back to curated list.")
            return []

    def get_token_price_history(self, token_address, time_from, time_to):
        pass

    def search_token(self, query):
        """
        Search for a token by name or symbol using DexScreener.
        Returns the best match profile on Base chain.
        """
        url = f"{self.dex_url}/search/?q={query}"
        try:
            print(f"Searching DexScreener for '{query}'...")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            pairs = data.get("pairs", [])
            
            # Filter for Base chain and find best liquidity
            base_pairs = [p for p in pairs if p.get("chainId") == "base"]
            
            if not base_pairs:
                return None
                
            # Sort by liquidity descending
            best_pair = max(base_pairs, key=lambda x: (x.get("liquidity") or {}).get("usd") or 0)
            
            # Normalize to our profile format
            # We want to use the same format as get_token_profile return
            # But get_token_profile returns enriched Gecko data if possible.
            # So here we extract the address and call get_token_profile to align everything
            token_address = best_pair.get("baseToken", {}).get("address")
            if token_address:
                print(f"Found match: {best_pair.get('baseToken', {}).get('symbol')} ({token_address})")
                return self.get_token_profile(token_address)
            
            return None
            
        except Exception as e:
            print(f"Search failed: {e}")
            return None

    def check_market_volatility(self, profile):
        """
        Mengecek perubahan harga 1 jam dan 24 jam dari profil yang sudah ada.
        """
        if not profile:
            return {}
        
        return {
            "priceChange": profile.get("priceChange", {}),
            "volume": profile.get("volume", {}),
            "liquidity": profile.get("liquidity", {})
        }
