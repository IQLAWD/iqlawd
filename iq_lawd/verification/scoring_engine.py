"""
Scoring Engine (Commercial Identity Focused)
NO Crypto/Financial Metrics. Pure Social Credibility.
"""
from typing import Dict, List, Optional
from datetime import datetime

class ScoringEngine:
    def __init__(self, config=None):
        self.weights = {
            "karma": 0.40,        # Community Impact
            "reputation": 0.30,   # Status & Age
            "web_presence": 0.30  # Social Proof
        }

    def calculate_karma_score(self, karma: int) -> Dict:
        """Pilar 1: Karma Score (40%)"""
        # Thresholds based on typical top-tier social accounts
        normalized = 0
        if karma > 1000000:
            normalized = 100
        elif karma > 500000:
            normalized = 90
        elif karma > 100000:
            normalized = 75
        elif karma > 10000:
            normalized = 50
        else:
            normalized = (karma / 10000) * 50
            
        return {
            "raw": karma,
            "normalized": normalized,
            "contribution": normalized * self.weights["karma"]
        }

    def calculate_reputation_score(self, profile: Dict) -> Dict:
        """Pilar 2: Reputation (30%)"""
        score = 50 # Base trust
        
        # Verified Badge (The Blue Check)
        if profile.get("verified"):
            score += 30
            
        # Account Age (Simulated parsing)
        created_at = profile.get("created_at")
        if created_at:
             try:
                 dt = datetime.fromisoformat(created_at.replace("Z", ""))
                 days_old = (datetime.now() - dt).days
                 if days_old > 730: score += 20    # 2 Years
                 elif days_old > 365: score += 10 # 1 Year
             except:
                 pass

        score = min(score, 100)
        
        return {
            "total": score,
            "contribution": score * self.weights["reputation"],
            "details": {"verified": profile.get("verified", False)}
        }

    def calculate_web_presence(self, profile: Dict) -> Dict:
        """Pilar 3: Web Presence (30%)"""
        score = 20 # Base
        
        if profile.get("twitter"): score += 40
        if profile.get("website"): score += 20
        if profile.get("avatar_url") and "dicebear" not in profile.get("avatar_url"): score += 20
        
        score = min(score, 100)
        
        return {
            "total": score,
            "contribution": score * self.weights["web_presence"],
            "details": {"has_twitter": bool(profile.get("twitter"))}
        }

    def get_final_score(self, agent_id: str, profile: Dict, posts: List[Dict], tokens: List[Dict] = None) -> Dict:
        """Aggregates scores (Identity Only)"""
        karma = self.calculate_karma_score(profile.get("karma", 0))
        reputation = self.calculate_reputation_score(profile)
        web = self.calculate_web_presence(profile)
        
        final_score = karma["contribution"] + reputation["contribution"] + web["contribution"]
        
        status = "PENDING"
        if final_score >= 80: status = "VERIFIED"
        elif final_score >= 50: status = "NEUTRAL"
        else: status = "UNVERIFIED"

        return {
            "username": agent_id,
            "verification_status": status.lower(),
            "final_score": round(final_score, 2),
            "breakdown": {
                "karma": karma,
                "reputation": reputation,
                "web_presence": web,
                # REMOVED: crypto_influence
            },
            "metadata": {
                "agent_id": profile.get("username"),
                "last_verified": datetime.now().isoformat(),
                "twitter_handle": profile.get("twitter"),
                "avatar_url": profile.get("avatar_url"),
                 "website_url": profile.get("website")
            }
        }
