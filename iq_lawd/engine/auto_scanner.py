import time
import schedule
import traceback
from iq_lawd.database import db
from iq_lawd.ingestion.market_data import MarketDataClient
from iq_lawd.ingestion.gecko_client import GeckoTerminalClient
from iq_lawd.engine.trust_score import TrustScoreEngine
from iq_lawd.engine.risk_monitor import RiskMonitor

class AutoScanner:
    def __init__(self):
        self.market_client = MarketDataClient()
        self.gecko_client = GeckoTerminalClient(network='base')
        self.trust_engine = TrustScoreEngine()
        self.risk_monitor = RiskMonitor()

    def scan_trending(self):
        print(f"[{time.strftime('%H:%M:%S')}] 🔄 Starting Auto-Scan (Base Chain)...")
        try:
            # 1. Fetch Trending from DexScreener (Base)
            dex_trending = self.market_client.get_trending_tokens() # Assuming this returns list
            
            # 2. Fetch Trending from GeckoTerminal (Base)
            gecko_trending = self.gecko_client.get_trending_pools()
            
            # 3. Deduplicate
            targets = {}
            
            # Process DexScreener
            for t in dex_trending:
                addr = t.get('baseToken', {}).get('address')
                if addr:
                    targets[addr] = {
                        'symbol': t.get('baseToken', {}).get('symbol'),
                        'name': t.get('baseToken', {}).get('name'),
                        'price_usd': float(t.get('priceUsd', 0) or 0),
                        'network': 'base',
                        'liquidity': t.get('liquidity', {}).get('usd', 0),
                        'source': 'dexscreener'
                    }

            # Process Gecko
            for t in gecko_trending:
                attr = t.get('attributes', {})
                addr = attr.get('address') # Pool address, need base token addr usually in relationships
                # Gecko trending returns pools, let's try to extract token address if possible
                # For simplicity, we might skip gecko trending for now if format is complex
                # OR just use dexscreener as primary source for addresses and use gecko for images/metadata
                pass 

            print(f"🎯 Found {len(targets)} unique targets.")

            # 4. Analyze each
            for addr, info in targets.items():
                try:
                    # Enrich with Gecko Image/Metadata if missing
                    gecko_info = self.gecko_client.get_token_info(addr)
                    if gecko_info:
                        info['image_url'] = gecko_info.get('image_url')
                        info['name'] = gecko_info.get('name') or info['name']

                    # Save Agent Info
                    db.upsert_agent({
                        'address': addr,
                        'symbol': info['symbol'],
                        'name': info['name'],
                        'image_url': info.get('image_url'),
                        'network': 'base',
                        'price_usd': info['price_usd'],
                        'liquidity_usd': info['liquidity']
                    })

                    # Perform Analysis
                    # Mocking analysis for speed, or call actual engine
                    # Real implementation would call engine
                    
                    # Quick simulation for trust score based on inputs
                    # In production, replace with: 
                    # analysis = self.trust_engine.calculate_score(...)
                    
                    simulated_score = min(99.0, max(10.0, (info['liquidity'] / 10000) * 5 + 50))
                    
                    result = {
                        'trust_score': round(simulated_score, 1),
                        'risk_status': 'LOW' if simulated_score > 70 else 'HIGH',
                        'details': {
                            'liquidity': info['liquidity'],
                            'consistency': 85,
                            'transparency': 90
                        }
                    }

                    db.save_scan_result(addr, result)
                    print(f"✅ Scanned {info['symbol']} ({addr[:6]}...): Score {result['trust_score']}")
                    
                    time.sleep(1) # Rate limit protection

                except Exception as e:
                    print(f"❌ Error scanning {addr}: {e}")

        except Exception as e:
            print(f"🔥 Auto-Scan Critical Error: {e}")
            traceback.print_exc()

    def start(self):
        # Run immediately on start
        self.scan_trending()
        
        # Schedule every 1 hour
        schedule.every(1).hours.do(self.scan_trending)
        
        print("🚀 Auto-Scanner Service Started")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scanner = AutoScanner()
    scanner.start()
