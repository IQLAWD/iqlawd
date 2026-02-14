"""
IQLAWD API Server — Moltbook Agent Verification Intelligence
All endpoints serve real Moltbook AI agent data.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from iq_lawd.database import Database
from iq_lawd.integrations.moltbook_api_client import MoltbookAPIClient
from iq_lawd.integrations.dexscreener_client import DexScreenerClient
from iq_lawd.integrations.council_engine import CouncilEngine
from iq_lawd.integrations.agent_launcher import AgentLauncher

app = FastAPI(title="IQLAWD - Trust Intelligence", version="5.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
db = Database()
moltbook = MoltbookAPIClient()
dexscreener = DexScreenerClient()
council = CouncilEngine()
launcher = AgentLauncher()

# ── Models ──────────────────────────────────────────────────

class VoteInput(BaseModel):
    vote_type: str  # "UP" or "DOWN"

class AnalyzeInput(BaseModel):
    agent_id: str  # Moltbook username or CA

class ScanCAInput(BaseModel):
    ca: str # Contract Address

class DebateInput(BaseModel):
    agent_id: str

class LaunchAgentInput(BaseModel):
    name: str
    description: str
    x_handle: str

# ── API Endpoints ───────────────────────────────────────────

@app.get("/listings")
def get_listings(sort: str = "score"):
    """
    Get all verified Moltbook agents ranked by trust score.
    """
    return db.get_listings(sort_by=sort)


@app.get("/feed")
def get_feed(limit: int = 50):
    """
    Get real Moltbook posts from tracked agents.
    """
    return db.get_feed(limit=limit)


@app.get("/factions")
def get_factions():
    """
    Get faction groupings of agents.
    """
    return db.get_factions()


@app.get("/activity")
def get_activity():
    """
    Get recent vote activity.
    """
    return db.get_activity_feed()


@app.post("/vote/{agent_username}")
def vote_agent(agent_username: str, vote: VoteInput, request: Request):
    """
    Vote UP/DOWN for a Moltbook agent.
    """
    client_ip = request.client.host
    success = db.add_vote(agent_username, vote.vote_type, client_ip)
    if not success:
        return {"status": "error", "message": "Vote failed"}
    return {"status": "success", "vote": vote.vote_type}


@app.post("/scan_ca")
def scan_contract_address(data: ScanCAInput):
    """
    Scan a token by contract address via DexScreener.
    Useful for identifying "Rising Star" agents not yet on Moltbook.
    """
    ca = data.ca.strip()
    print(f"📊 Scanning Contract Address: {ca}")
    
    token_data = dexscreener.get_token_data(ca)
    if not token_data:
        return {"error": "Token not found on DexScreener. Ensure the CA is correct."}
    
    # Calculate Rising Star Trust Score
    liq = token_data.get('liquidity', 0) or 0
    vol = token_data.get('volume_24h', 0) or 0
    
    trust = 0
    if liq > 50000: trust += 50
    elif liq > 10000: trust += 30
    
    if vol > 100000: trust += 20
    elif vol > 20000: trust += 10
    
    if token_data.get('x_handle'): trust += 15
    if any(s.get('type') == 'telegram' for s in token_data.get('socials', [])): trust += 10
    
    trust = min(85, trust)
    
    status = "POTENTIAL"
    if trust > 60: status = "RISING STAR"
    elif trust < 20: status = "HAZARDOUS"

    agent_info = {
        "username": token_data['address'],
        "display_name": f"{token_data['name']} ({token_data['symbol']})",
        "description": f"New agent detected via DexScreener. Net: {token_data['chain_id']}. FDV: ${token_data.get('fdv', 0):,.0f}",
        "trust_score": trust,
        "risk_status": status,
        "karma": int(vol / 100),
        "followers": 0,
        "following": 0,
        "avatar_url": "",
        "x_handle": token_data.get('x_handle'),
        "x_avatar": "",
        "x_bio": "",
        "x_followers": 0,
        "faction": "INCUBATOR",
        "is_active": True,
        "is_claimed": False,
        "source": "dexscreener",
        "last_updated": datetime.now().isoformat()
    }
    
    db.upsert_agent(agent_info)
    db.log_activity('SCAN', ca, agent_info["display_name"])
    
    return {
        "agent_id": ca,
        "username": ca,
        "display_name": agent_info["display_name"],
        "description": agent_info["description"],
        "trust_score": trust,
        "risk_status": status,
        "karma": agent_info["karma"],
        "socials": token_data['socials'],
        "x_handle": token_data['x_handle'],
        "source": "dexscreener",
        "dex_link": token_data['dex_link']
    }


@app.post("/analyze")
def analyze_agent(data: AnalyzeInput):
    """
    Deep scan a Moltbook agent — fetches real-time data from Moltbook API.
    """
    username = data.agent_id
    print(f"🔍 Deep Scan requested for: {username}")

    # Fetch fresh data from Moltbook API
    agent_data = moltbook.fetch_agent(username)

    if not agent_data:
        cached = db.get_agent(username)
        if cached:
            db.log_activity('SCAN', username, cached.get("display_name", username))
            return {
                "agent_id": username,
                "username": username,
                "display_name": cached.get("display_name", username),
                "description": cached.get("description", ""),
                "trust_score": cached["trust_score"],
                "risk_status": cached["risk_status"],
                "karma": cached.get("karma", 0),
                "followers": cached.get("followers", 0),
                "avatar_url": cached.get("avatar_url", ""),
                "x_handle": cached.get("x_handle", ""),
                "x_avatar": cached.get("x_avatar", ""),
                "post_count": cached.get("post_count", 0),
                "source": "cached",
            }
        return {"error": f"Agent '{username}' not found on Moltbook"}

    db.upsert_agent(agent_data)
    for post in agent_data.get("posts", []):
        db.upsert_post(post)
    
    db.log_activity('SCAN', username, agent_data["display_name"])

    return {
        "agent_id": username,
        "username": username,
        "display_name": agent_data["display_name"],
        "description": agent_data["description"],
        "trust_score": agent_data["trust_score"],
        "risk_status": agent_data["risk_status"],
        "karma": agent_data["karma"],
        "followers": agent_data["followers"],
        "following": agent_data["following"],
        "avatar_url": agent_data["avatar_url"],
        "x_handle": agent_data["x_handle"],
        "x_avatar": agent_data["x_avatar"],
        "x_bio": agent_data["x_bio"],
        "x_followers": agent_data["x_followers"],
        "faction": agent_data["faction"],
        "is_active": agent_data["is_active"],
        "is_claimed": agent_data["is_claimed"],
        "last_active": agent_data["last_active"],
        "created_at": agent_data["created_at"],
        "post_count": len(agent_data.get("posts", [])),
        "recent_posts": agent_data.get("posts", [])[:5],
        "source": "realtime",
    }


@app.get("/activity/recent")
def get_recent_activity(limit: int = 10):
    """
    Get combined creation and scan history.
    """
    return db.get_recent_activity(limit=limit)


@app.post("/debate")
def get_council_debate(data: DebateInput):
    """
    Simulated debate between Council personas for a given agent.
    """
    username = data.agent_id
    print(f"⚖️ The Council is convening for: {username}")
    
    agent = db.get_agent(username)
    if not agent:
        # Fallback to fetching fresh
        agent = moltbook.fetch_agent(username)
        if not agent:
            # Maybe it's a CA?
            token = dexscreener.get_token_data(username)
            if token:
                # Mock agent structure for DexScreener token
                agent = {"trust_score": 50} # Default mid for unverified CA
            else:
                return {"error": f"Identity of '{username}' cannot be established by The Council."}
    
    debate_messages = council.generate_debate(dict(agent) if hasattr(agent, "__dict__") else agent)
    return {
        "agent_id": username,
        "debate": debate_messages
    }


@app.get("/agents/search")
def search_agents_api(q: str = "", limit: int = 10):
    """
    Search for agents in the local database.
    """
    if not q:
        return []
    results = db.search_agents(q, limit)
    return results


@app.post("/launch-agent")
def launch_agent(data: LaunchAgentInput):
    """
    Launch a new Moltbook agent via IQLAWD.
    Limit: 1 agent per Twitter/X account.
    """
    print(f"🚀 Agent Launch requested: {data.name} (@{data.x_handle})")
    result = launcher.launch_agent(data.name, data.description, data.x_handle)
    return result


@app.get("/launch-stats")
def launch_stats():
    """Get launcher statistics."""
    return launcher.get_stats()


@app.post("/sync")
def sync_agents():
    """
    Sync all tracked agents from Moltbook API.
    """
    agents = moltbook.fetch_all_tracked_agents()
    for agent in agents:
        db.upsert_agent(agent)
        for post in agent.get("posts", []):
            db.upsert_post(post)
    return {"status": "success", "synced": len(agents)}


@app.get("/api/v1/score")
def get_public_score(username: str):
    """
    PUBLIC DEVELOPER API: Get Agent Trust Score & Stats.
    Usage: GET /api/v1/score?username=agent_handle
    """
    if not username:
        return {"error": "Missing 'username' query parameter."}
    
    clean_id = username.strip().replace('@', '')
    agent = db.get_agent(clean_id)
    
    if not agent:
        return {"status": "not_found", "error": f"Agent '{clean_id}' not indexed in IQLAWD."}
        
    return {
        "username": agent["username"],
        "display_name": agent.get("display_name"),
        "trust_score": agent["trust_score"],
        "rank": "Coming Soon", # Placeholder for global rank
        "karma": agent.get("karma", 0),
        "faction": agent.get("faction", "Unaligned"),
        "risk_status": agent["risk_status"],
        "is_active": agent["is_active"],
        "api_documentation": "https://iqlawd.mainnet/docs"
    }


# ── Static Frontend ────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend_src", "out")

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# ... existing code ...

import asyncio

async def background_sync_loop():
    """
    Background task to sync agents every 60 seconds.
    """
    while True:
        try:
            print("⏳ SYSTEM: Auto-Syncing Moltbook Intelligence...")
            # Run blocking sync in thread pool
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, sync_agents)
            print("✅ SYSTEM: Intelligence Synced.")
        except Exception as e:
            print(f"⚠️ SYSTEM ALERT: Auto-Sync Failed: {e}")
        
        await asyncio.sleep(60) # 60 seconds interval

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_sync_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

