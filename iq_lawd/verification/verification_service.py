"""
Verification Service Orchestrator
Coordinates API Client, Scoring Engine, and Database for agent verification.
"""
from datetime import datetime, timedelta
from iq_lawd.integrations.moltbook_api_client import MoltbookAPIClient
from iq_lawd.verification.scoring_engine import ScoringEngine
from iq_lawd.verification.ai_analyst import ai_analyst
from iq_lawd.database import db
import json


class VerificationService:
    def __init__(self):
        self.api_client = MoltbookAPIClient()
        self.scoring_engine = ScoringEngine()
        self.db = db

    def verify_agent(self, username: str, force_refresh: bool = False) -> dict:
        """
        Main entry point to get/calculate trust score for an agent.
        Implements 7-day result caching.
        """
        # 1. Check if already verified recently
        existing = self.db.get_verified_details(username)
        if existing and not force_refresh:
            last_verified = datetime.fromisoformat(existing["last_verified"])
            # Faster refresh for realtime feel (1 min cache)
            if datetime.now() - last_verified < timedelta(minutes=1):
                print(f"📦 Returning cached verification for {username}")
                # Re-format internal DB result to match engine output if needed
                return existing

        print(f"🕵️‍♂️ Starting fresh verification for: {username}")

        # HARDCODED: IQLAWD System Agent
        clean_user = username.strip().upper()
        print(f"DEBUG: Checking '{username}' -> '{clean_user}'")
        if clean_user == "IQLAWD":
            print("🛡️ Verifying System Agent: IQLAWD")
            result = self._get_system_agent_profile()
            self.db.upsert_verified_agent(result)
            return result
        
        # 2. Fetch Data from Moltbook
        profile = self.api_client.get_agent_profile(username)
        if not profile:
            return {"error": f"Agent '{username}' not found on Moltbook."}
            
        posts = self.api_client.get_agent_posts(username, limit=50)
        tokens = self.api_client.get_agent_tokens(username)
        
        # 3. Calculate Score
        verification_result = self.scoring_engine.get_final_score(
            username, profile, posts, tokens
        )
        
        # Add basic info for DB storage
        verification_result["display_name"] = profile.get("name")
        verification_result["avatar_url"] = profile.get("avatar_url")
        verification_result["faction"] = self._assign_faction(username)
        
        # 4. Generate AI Verdict
        print(f"🤖 Requesting AI Intelligence Verdict for {username}...")
        ai_verdict = ai_analyst.generate_verdict(verification_result)
        verification_result["ai_verdict"] = ai_verdict
        
        # 5. Oracle Feed Post (RT-like behavior)
        if verification_result["final_score"] >= 85:
            msg = f"Oracle Seal of Approval granted to @{username}. High integrity detected."
            self.db.add_oracle_message(username, msg, "APPROVAL")
        elif verification_result["final_score"] < 40:
             msg = f"Caution: @{username} showing significant anomalies in reputation pillars."
             self.db.add_oracle_message(username, msg, "CAUTION")

        # 6. Persist to Database
        success = self.db.upsert_verified_agent(verification_result)
        if not success:
            print(f"⚠️ Failed to save verification result for {username}")

        return verification_result

    def get_leaderboard(self, sort_by='score', limit=50, min_score=0, verified_only=False, has_website=False, search=""):
        """Returns the current ranking of verified agents with optional filters including search"""
        results = self.db.get_verified_listings(
            sort_by=sort_by, 
            limit=limit, 
            min_score=min_score, 
            verified_only=verified_only, 
            has_website=has_website,
            search=search
        )
        
        # Realtime Discovery: If search yields no results, try to fetch from network
        if not results and search and len(search) > 2:
            print(f"🔎 Local search failed for '{search}'. Attempting network discovery...")
            # Check if agent exists on Moltbook
            profile = self.api_client.get_agent_profile(search)
            if profile:
                print(f"✅ Found '{search}' on network. Verifying now...")
                self.verify_agent(search, force_refresh=True)
                # Re-fetch from DB to get the verified record
                results = self.db.get_verified_listings(search=search)
            else:
                print(f"❌ '{search}' not found on network.")
                
        return results

    def process_vote(self, username: str, vote_type: str, ip_address: str):
        """Handles community voting"""
        return self.db.add_community_vote(username, vote_type.upper(), ip_address)

    def compare_agents(self, username_a: str, username_b: str) -> dict:
        """
        Fetches data for two agents and generates an AI comparison verdict.
        """
        agent_a = self.db.get_verified_details(username_a)
        agent_b = self.db.get_verified_details(username_b)

        if not agent_a or not agent_b:
            return {"error": "One or both agents not found in the verified database."}

        comparison_verdict = ai_analyst.generate_comparison(agent_a, agent_b)

        return {
            "agent_a": agent_a,
            "agent_b": agent_b,
            "comparison_verdict": comparison_verdict
        }


    def _get_system_agent_profile(self):
        """Returns the hardcoded profile for the system agent"""
        return {
            "username": "IQLAWD",
            "display_name": "IQLAWD System",
            "avatar_url": "/logo.png", # Frontend should handle relative path or I can try absolute URL if needed
            "verification_status": "verified",
            "final_score": 100.0,
            "ai_verdict": "CORE SYSTEM IDENTITY. This agent represents the verified authority of the IQLAWD network. Absolute trust established.",
            "breakdown": {
                "karma": {"raw": 999999, "normalized": 100, "contribution": 40},
                "reputation": {"total": 100, "contribution": 30, "details": {"score": 100}},
                "web_presence": {"total": 100, "contribution": 30, "details": {"website": 1, "twitter": 1}},
                "crypto_influence": {"total": 0, "contribution": 0, "details": {}}
            },
            "metadata": {
                "agent_id": "system-001",
                "twitter_handle": "IQLAWD_ai",
                "website_url": "https://iqlawd.ai"
            },
            "history": [] 
        }

    def _assign_faction(self, username: str) -> str:
        """Assigns faction based on username or metadata"""
        u = username.lower()
        if u in ['truth_terminal', 'aixbt', 'goat']:
            return "Truth Terminal"
        elif u in ['swarms', 'zerebro']:
            return "Swarm Zero"
        elif u in ['virtual', 'luna', 'ix']:
            return "Virtuals Protocol"
        elif u in ['clanker', 'iqlawd', 'proxies']:
            return "Base Native"
        return "Ronin" # Independent

    def get_social_pulse(self, limit=50):
        """
        Aggregates real agent posts + system events for 'The Pulse'
        Uses ALL known agents for a rich, always-populated feed.
        """
        feed = []
        
        # 1. Fetch Posts from ALL Known Agents (not just DB entries)
        known_agents = self.api_client.KNOWN_AGENTS
        for agent_key, agent_data in known_agents.items():
            try:
                posts = self.api_client.get_agent_posts(agent_data['username'], limit=2)
                for p in posts:
                    feed.append({
                        "type": "post",
                        "id": p.get("id"),
                        "username": agent_data.get("username"),
                        "avatar": agent_data.get("avatar_url", "/logo.png"),
                        "content": p.get("content"),
                        "timestamp": p.get("created_at"),
                        "metrics": {"likes": p.get("upvotes", 0), "replies": p.get("downvotes", 0)} 
                    })
            except Exception as e:
                print(f"⚠️ Failed to fetch posts for {agent_key}: {e}")
                
        # 2. Get System Events
        system_activity = self.db.get_activity_feed(limit=10)
        for act in system_activity:
            feed.append({
                "type": "event",
                "id": f"evt_{act.get('timestamp')}",
                "username": act.get("symbol"),
                "avatar": "/logo.png",
                "content": self._format_event_content(act),
                "timestamp": act.get("timestamp"),
                "metrics": None
            })
            
        # 3. Sort by Time, most recent first
        feed.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return feed[:limit]

    def _format_event_content(self, act):
        if act['type'] == 'vote':
            return f"Community voted {act['value']} on @{act['symbol']}"
        elif act['type'] == 'scan':
            return f"New deep scan initiated for @{act['symbol']}"
        return act.get('value', 'System Event')
        
    def get_faction_leaderboard(self):
        return self.db.get_faction_stats()

# Singleton instance
verification_service = VerificationService()
