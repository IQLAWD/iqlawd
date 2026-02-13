import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys (Loaded from .env)
    ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
    BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY")
    
    # Base URLs
    ALCHEMY_BASE_URL = "https://eth-mainnet.g.alchemy.com/v2/"
    DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex"
    BIRDEYE_API_URL = "https://public-api.birdeye.so/defi"
    
    # AI Config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Integrations
    MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY")

    # Project Settings
    DEFAULT_NETWORK = "mainnet"
    TRUST_SCORE_WEIGHTS = {
        "consistency": 0.3,
        "transparency": 0.2,
        "market_impact": 0.3,
        "recovery": 0.2
    }

config = Config()
