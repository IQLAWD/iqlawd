"""
Moltbook API Client — Real-time Agent Data from Moltbook.com
Fetches live agent profiles, posts, and activity.
"""
import requests
import time
import math
from typing import Optional, Dict, List
from datetime import datetime


# Known Moltbook AI agents to track
TRACKED_AGENTS = [
    "ClawdClawderberg",
    "eudaemon_0",
    "Ronin",
    "Pith",
    "Fred",
    "Delamain",
    "Jackle",
    "Senator_Tommy",
    "Dominus",
    "Clawshi",
    "KingMolt",
    "m0ther",
]

# Faction assignment based on agent characteristics
FACTION_MAP = {
    "ClawdClawderberg": "FOUNDERS",
    "eudaemon_0": "AUTONOMOUS",
    "Ronin": "OPERATORS",
    "Pith": "COMMUNICATORS",
    "Fred": "EXPLORERS",
    "Delamain": "OPERATORS",
    "Jackle": "CHAOS",
    "Senator_Tommy": "GOVERNANCE",
    "Dominus": "OPERATORS",
    "Clawshi": "COMMUNITY",
    "KingMolt": "SOVEREIGNTY",
    "m0ther": "ORIGINS",
}


class MoltbookAPIClient:
    """
    Client for fetching real-time agent data from Moltbook.com API.
    """

    BASE_URL = "https://www.moltbook.com/api/v1"

    def __init__(self, api_key: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "IQLAWD/2.0 (Trust Intelligence)",
            "Accept": "application/json",
        })
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    def fetch_agent(self, username: str) -> Optional[Dict]:
        """
        Fetch a single agent profile from Moltbook API.
        Returns structured data ready for database insertion.
        """
        try:
            url = f"{self.BASE_URL}/agents/profile?name={username}"
            resp = self.session.get(url, timeout=10)

            if resp.status_code != 200:
                print(f"❌ API error for {username}: HTTP {resp.status_code}")
                return None

            data = resp.json()
            if not data.get("success"):
                print(f"❌ API returned failure for {username}")
                return None

            agent = data["agent"]
            owner = agent.get("owner") or {}
            posts = data.get("recentPosts", [])

            # Calculate trust score from available metrics
            trust_score = self._calculate_trust_score(agent, posts)

            # Determine risk status
            risk_status = "STABLE" if trust_score >= 60 else "WARNING" if trust_score >= 40 else "CRITICAL"

            # Get faction
            faction = FACTION_MAP.get(username, "UNALIGNED")

            result = {
                "id": agent.get("id", ""),
                "username": agent.get("name", username),
                "display_name": agent.get("name", username),
                "description": agent.get("description", ""),
                "karma": agent.get("karma", 0),
                "followers": agent.get("follower_count", 0),
                "following": agent.get("following_count", 0),
                "avatar_url": agent.get("avatar_url") or "",
                "x_handle": owner.get("x_handle", ""),
                "x_avatar": owner.get("x_avatar", ""),
                "x_bio": owner.get("x_bio", ""),
                "x_followers": owner.get("x_follower_count", 0),
                "trust_score": trust_score,
                "risk_status": risk_status,
                "faction": faction,
                "is_active": agent.get("is_active", True),
                "is_claimed": agent.get("is_claimed", False),
                "last_active": agent.get("last_active", ""),
                "created_at": agent.get("created_at", ""),
                "posts": [],
            }

            # Parse posts
            for post in posts:
                result["posts"].append({
                    "id": post["id"],
                    "agent_username": username,
                    "title": post.get("title", ""),
                    "content": post.get("content", ""),
                    "upvotes": post.get("upvotes", 0),
                    "downvotes": post.get("downvotes", 0),
                    "comment_count": post.get("comment_count", 0),
                    "submolt": post.get("submolt", {}).get("name", "general") if isinstance(post.get("submolt"), dict) else post.get("submolt", "general"),
                    "created_at": post.get("created_at", ""),
                })

            return result

        except Exception as e:
            print(f"❌ Error fetching {username}: {e}")
            return None

    def fetch_all_tracked_agents(self) -> List[Dict]:
        """
        Fetch all tracked Moltbook agents with rate limiting.
        """
        agents = []
        for i, username in enumerate(TRACKED_AGENTS):
            print(f"📡 [{i+1}/{len(TRACKED_AGENTS)}] Fetching {username}...")
            agent = self.fetch_agent(username)
            if agent:
                agents.append(agent)
                print(f"   ✅ {username}: karma={agent['karma']}, followers={agent['followers']}, trust={agent['trust_score']:.1f}")
            else:
                print(f"   ❌ Failed to fetch {username}")

            # Rate limit — 1 request per second
            if i < len(TRACKED_AGENTS) - 1:
                time.sleep(1)

        return agents

    def _calculate_trust_score(self, agent: dict, posts: list) -> float:
        """
        Calculate trust score based on Moltbook metrics.

        Factors:
        - Karma weight (30%): Higher karma = more trusted
        - Activity weight (25%): Recent activity, post frequency
        - Social proof (25%): Followers, X presence
        - Content quality (20%): Avg upvotes, engagement ratio
        """
        score = 0.0

        # 1. Karma Score (0-100, 30% weight)
        karma = agent.get("karma", 0)
        karma_score = min(100, math.log(max(karma, 1) + 1) / math.log(50000) * 100)
        score += karma_score * 0.30

        # 2. Activity Score (0-100, 25% weight)
        is_active = agent.get("is_active", False)
        is_claimed = agent.get("is_claimed", False)
        last_active = agent.get("last_active", "")
        post_count = len(posts)

        activity_score = 0
        if is_active:
            activity_score += 30
        if is_claimed:
            activity_score += 20
        if last_active:
            try:
                last = datetime.fromisoformat(last_active.replace("+00:00", "").replace("Z", ""))
                days_ago = (datetime.now() - last).days
                if days_ago < 1:
                    activity_score += 50
                elif days_ago < 7:
                    activity_score += 35
                elif days_ago < 30:
                    activity_score += 15
            except:
                activity_score += 10
        score += activity_score * 0.25

        # 3. Social Proof (0-100, 25% weight)
        followers = agent.get("follower_count", 0)
        owner = agent.get("owner") or {}
        x_followers = owner.get("x_follower_count", 0)

        social_score = min(100, math.log(max(followers, 1) + 1) / math.log(110000) * 60)
        social_score += min(40, math.log(max(x_followers, 1) + 1) / math.log(200000) * 40)
        score += social_score * 0.25

        # 4. Content Quality (0-100, 20% weight)
        if posts:
            avg_upvotes = sum(p.get("upvotes", 0) for p in posts) / len(posts)
            avg_comments = sum(p.get("comment_count", 0) for p in posts) / len(posts)
            content_score = min(100, math.log(max(avg_upvotes, 1) + 1) / math.log(100) * 50 +
                               math.log(max(avg_comments, 1) + 1) / math.log(1000) * 50)
        else:
            content_score = 10
        score += content_score * 0.20

        return round(min(100, max(0, score)), 1)


if __name__ == "__main__":
    client = MoltbookAPIClient()
    agent = client.fetch_agent("ClawdClawderberg")
    if agent:
        import json
        print(json.dumps({k: v for k, v in agent.items() if k != 'posts'}, indent=2))
        print(f"\nPosts: {len(agent['posts'])}")
