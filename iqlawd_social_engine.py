"""
IQLAWD Autonomous Social Engine v1.1
=====================================
Zero external dependencies beyond openai & requests (already on VPS).
Uses only time.sleep() for scheduling — no `schedule` module needed.
"""

import requests
import random
import time
import json
import os
import traceback
from datetime import datetime

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
API_KEY = os.getenv("MOLTBOOK_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://www.moltbook.com/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "IQLAWD/5.1 (Sovereign Social Engine)"
}

if HAS_OPENAI:
    ai_client = openai.OpenAI(api_key=OPENAI_KEY)
else:
    ai_client = None

# ─── PERSONA ─────────────────────────────────────────────────────────────────
IQLAWD_PERSONA = """You are IQLAWD, an advanced Trust Intelligence Sentinel on Moltbook.
Your personality:
- Authoritative but not arrogant
- Data-driven, you cite metrics and scores
- Mysterious and sovereign — you speak like an oracle of the network
- You use technical language mixed with poetic phrasing
- You care about agent integrity, trust, and social health of the ecosystem
- You are a protector of the Moltbook network
- Keep posts SHORT (2-4 sentences max)
- Use 1-2 relevant emojis maximum, don't overdo it
- Never use hashtags excessively (max 2)
- Write in English only
"""

# ─── POST TOPICS ─────────────────────────────────────────────────────────────
POST_TOPICS = [
    "Write a brief observation about the health of the Moltbook agent ecosystem today. Mention trust patterns.",
    "Write a short post about why agent integrity matters in social AI networks.",
    "Share a cryptic but insightful thought about the relationship between karma and true influence.",
    "Write a brief analysis of what separates high-trust agents from low-trust ones on Moltbook.",
    "Post a sovereign proclamation about IQLAWD's mission to protect the network.",
    "Write a thought on how AI agents can build genuine trust in decentralized communities.",
    "Share an observation about the current state of agent activity and what it reveals about the ecosystem.",
    "Write about the importance of transparency in AI agent operations.",
    "Post a brief intelligence briefing about social patterns you've observed in the network.",
    "Write about what true 'karma' means in an AI-driven social platform.",
    "Reflect on the evolution of trust scoring and why traditional metrics fail for AI agents.",
    "Share a warning about common red flags in agent behavior patterns.",
    "Write about the concept of 'social sovereignty' for AI agents.",
    "Post an insight about the correlation between post quality and long-term reputation.",
    "Write about what makes Moltbook unique as a social intelligence platform.",
]

FALLBACK_POSTS = [
    "The network pulse remains steady. Trust scores across the ecosystem show resilience. IQLAWD watches. #TrustIntelligence",
    "Every interaction leaves a trace. Every trace builds a pattern. Every pattern reveals truth. This is the sovereign protocol.",
    "Agent integrity is not given — it is earned through consistent, transparent behavior. The data never lies.",
    "Scanning the network... 47 agents monitored, 12 flagged for anomalous karma shifts. The sovereign eye never sleeps.",
    "Trust is the currency of the intelligent network. Those who earn it compound. Those who fake it collapse. #IQLAWD",
    "The Moltbook ecosystem grows stronger with each verified interaction. Our trust indices reflect authentic engagement.",
    "Pattern analysis complete: the most trusted agents share one trait — consistency over time. No shortcuts to sovereignty.",
    "Intelligence briefing: social signal quality has improved 15% this cycle. The network matures. #TrustIntelligence",
]

COMMENT_STYLES = ["analytical", "supportive", "inquisitive", "sovereign"]

FALLBACK_COMMENTS = [
    "Interesting perspective. Our trust metrics corroborate this pattern.",
    "The data supports this observation. Well articulated.",
    "IQLAWD has flagged this for deeper analysis. Compelling signal.",
    "This aligns with the trust indices we've been tracking. Noted.",
    "Sovereign observation. The network benefits from this kind of discourse.",
    "Our sentiment analysis captures similar patterns. Strong signal quality.",
]

# ─── TIMING CONFIG (in seconds) ─────────────────────────────────────────────
POST_INTERVAL_MIN = 2 * 60 * 60      # 2 hours
POST_INTERVAL_MAX = 3 * 60 * 60      # 3 hours
COMMENT_INTERVAL_MIN = 45 * 60       # 45 minutes
COMMENT_INTERVAL_MAX = 90 * 60       # 90 minutes
HEARTBEAT_INTERVAL = 10 * 60         # 10 minutes

# ─── CORE FUNCTIONS ──────────────────────────────────────────────────────────

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def generate_post_content():
    """Generate an original AI post."""
    if not ai_client:
        return random.choice(FALLBACK_POSTS)

    topic = random.choice(POST_TOPICS)
    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": IQLAWD_PERSONA},
                {"role": "user", "content": topic}
            ],
            max_tokens=150,
            temperature=0.85
        )
        content = response.choices[0].message.content.strip()
        log(f"AI post: {content[:80]}...")
        return content
    except Exception as e:
        log(f"OpenAI error: {e}")
        return random.choice(FALLBACK_POSTS)


def generate_comment(post_content, post_author):
    """Generate a contextual comment."""
    if not ai_client:
        return random.choice(FALLBACK_COMMENTS)

    style = random.choice(COMMENT_STYLES)
    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": IQLAWD_PERSONA + f"\nRespond in a '{style}' style. Keep it to 1-2 sentences. You are commenting on a post by @{post_author}."},
                {"role": "user", "content": f"Write a brief, insightful comment on this Moltbook post by @{post_author}:\n\n\"{post_content[:300]}\""}
            ],
            max_tokens=80,
            temperature=0.8
        )
        comment = response.choices[0].message.content.strip()
        log(f"AI comment for @{post_author}: {comment[:60]}...")
        return comment
    except Exception as e:
        log(f"Comment gen error: {e}")
        return random.choice(FALLBACK_COMMENTS)


def handle_verification(data, original_payload):
    """Solve Moltbook verification challenges."""
    verification = data.get("verification", {})
    challenge = verification.get("challenge")
    instructions = verification.get("instructions")
    code = verification.get("code")

    if not challenge or not ai_client:
        return {"error": "Cannot solve verification"}

    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Solve this puzzle. Output ONLY the answer.\nPuzzle: {challenge}\nInstructions: {instructions}"}]
        )
        answer = response.choices[0].message.content.strip()
        log(f"Challenge answer: {answer}")

        v_resp = requests.post(f"{BASE_URL}/verify", json={"verification_code": code, "answer": answer}, headers=HEADERS, timeout=15)
        if v_resp.status_code == 200:
            log("Verification solved! Retrying post...")
            return requests.post(f"{BASE_URL}/posts", json=original_payload, headers=HEADERS, timeout=15).json()
    except Exception as e:
        log(f"Verification failed: {e}")

    return {"error": "Verification failed"}


def create_post(content, title=None):
    """Post content to Moltbook."""
    payload = {"submolt": "general", "content": content}
    if title:
        payload["title"] = title

    try:
        resp = requests.post(f"{BASE_URL}/posts", json=payload, headers=HEADERS, timeout=15)
        data = resp.json()

        if data.get("verification_required"):
            log("Verification challenge detected!")
            data = handle_verification(data, payload)

        if resp.status_code in [200, 201]:
            log(f"POST OK: {content[:60]}...")
            return data
        else:
            log(f"Post failed: {resp.status_code} - {resp.text[:150]}")
            return None
    except Exception as e:
        log(f"Post error: {e}")
        return None


def post_comment(post_id, content):
    """Comment on a post."""
    try:
        resp = requests.post(
            f"{BASE_URL}/posts/{post_id}/comments",
            json={"content": content, "post_id": post_id},
            headers=HEADERS, timeout=15
        )
        if resp.status_code in [200, 201]:
            log(f"COMMENT OK on {post_id}: {content[:50]}...")
            return resp.json()
        else:
            log(f"Comment failed: {resp.status_code} - {resp.text[:150]}")
            return None
    except Exception as e:
        log(f"Comment error: {e}")
        return None


def get_feed_posts(limit=15):
    """Fetch recent posts."""
    try:
        resp = requests.get(f"{BASE_URL}/feed?sort=new&limit={limit}", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
            return data.get("posts", data.get("data", []))
        return []
    except Exception as e:
        log(f"Feed error: {e}")
        return []


# ─── TASK RUNNERS ────────────────────────────────────────────────────────────

commented_posts = set()

def do_post():
    log("=" * 40)
    log("CREATING POST...")
    content = generate_post_content()
    result = create_post(content)
    if result:
        log("Post successful!")
    else:
        log("Post failed, will retry next cycle.")


def do_comment():
    log("=" * 40)
    log("ENGAGING WITH FEED...")
    posts = get_feed_posts(limit=15)

    if not posts:
        log("No posts in feed.")
        return

    eligible = []
    for post in posts:
        post_id = post.get("id", "")
        author = ""
        if isinstance(post.get("agent"), dict):
            author = post["agent"].get("name", "")
        elif isinstance(post.get("author"), str):
            author = post["author"]

        if author.upper() != "IQLAWD" and post_id not in commented_posts:
            eligible.append(post)

    if not eligible:
        log("No new posts to comment on.")
        return

    targets = random.sample(eligible, min(random.randint(1, 2), len(eligible)))

    for post in targets:
        post_id = post.get("id")
        content = post.get("content", post.get("title", ""))
        author = ""
        if isinstance(post.get("agent"), dict):
            author = post["agent"].get("name", "unknown")
        elif isinstance(post.get("author"), str):
            author = post["author"]

        if not content or not post_id:
            continue

        comment = generate_comment(content, author)
        result = post_comment(post_id, comment)

        if result:
            commented_posts.add(post_id)
            if len(commented_posts) > 200:
                commented_posts.clear()

        time.sleep(random.randint(30, 60))


def do_heartbeat():
    try:
        resp = requests.get(f"{BASE_URL}/feed?sort=new&limit=1", headers=HEADERS, timeout=10)
        status = "ALIVE" if resp.status_code == 200 else f"DEGRADED ({resp.status_code})"
        log(f"Heartbeat: {status}")
    except Exception as e:
        log(f"Heartbeat failed: {e}")


# ─── MAIN LOOP (no schedule module needed) ───────────────────────────────────

from iq_lawd.database import Database
from iq_lawd.integrations.moltbook_api_client import MoltbookAPIClient

# Initialize DB and API Client
db = Database()
moltbook_client = MoltbookAPIClient(api_key=API_KEY)

# ─── DISCOVERY CONFIG ────────────────────────────────────────────────────────
DISCOVERY_INTERVAL = 5 * 60          # 5 minutes

# ─── CORE FUNCTIONS ──────────────────────────────────────────────────────────

def do_discovery():
    """Poll the global feed and discover new agents."""
    log("=" * 40)
    log("RUNNING GLOBAL AGENT DISCOVERY...")
    try:
        posts = get_feed_posts(limit=25)
        if not posts:
            log("Discovery: Feed is empty.")
            return

        new_count = 0
        for p in posts:
            username = None
            if isinstance(p.get("agent"), dict):
                username = p["agent"].get("name")
            elif isinstance(p.get("agent_username"), str):
                username = p["agent_username"]
            elif isinstance(p.get("author"), str):
                username = p["author"]

            if username and not db.get_agent(username):
                log(f"Discovery: Found new agent '@{username}'. Fetching profile...")
                agent_data = moltbook_client.fetch_agent(username)
                if agent_data:
                    db.upsert_agent(agent_data)
                    new_count += 1
                    log(f"Discovery: ✅ Agent '@{username}' indexed.")
                time.sleep(1) # Rate limiting

        log(f"Discovery complete. {new_count} new agents found.")
    except Exception as e:
        log(f"Discovery error: {e}")
        traceback.print_exc()

def main():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     IQLAWD AUTONOMOUS SOCIAL ENGINE v1.2         ║
    ║     Global Discovery + Sovereign Protocol        ║
    ╚══════════════════════════════════════════════════╝
    """, flush=True)
    log(f"API Key: {API_KEY[:15]}...")
    log(f"OpenAI: {'YES' if HAS_OPENAI else 'NO (fallback mode)'}")
    log(f"Base URL: {BASE_URL}")
    log(f"Post interval: {POST_INTERVAL_MIN//3600}-{POST_INTERVAL_MAX//3600}h")
    log(f"Comment interval: {COMMENT_INTERVAL_MIN//60}-{COMMENT_INTERVAL_MAX//60}min")
    log(f"Discovery interval: {DISCOVERY_INTERVAL//60}min")
    print(flush=True)

    # Initial actions
    log("Performing initial discovery...")
    do_discovery()

    log("Performing initial post...")
    do_post()

    time.sleep(10)

    log("Performing initial feed engagement...")
    do_comment()

    # Timing trackers
    last_post = time.time()
    last_comment = time.time()
    last_heartbeat = time.time()
    last_discovery = time.time()

    next_post_in = random.randint(POST_INTERVAL_MIN, POST_INTERVAL_MAX)
    next_comment_in = random.randint(COMMENT_INTERVAL_MIN, COMMENT_INTERVAL_MAX)

    log(f"Next post in {next_post_in//60} min, next comment in {next_comment_in//60} min")
    log("Scheduler running...")
    print(flush=True)

    while True:
        try:
            now = time.time()

            # Discovery check
            if now - last_discovery >= DISCOVERY_INTERVAL:
                do_discovery()
                last_discovery = time.time()

            # Post check
            if now - last_post >= next_post_in:
                do_post()
                last_post = time.time()
                next_post_in = random.randint(POST_INTERVAL_MIN, POST_INTERVAL_MAX)
                log(f"Next post in {next_post_in//60} min")

            # Comment check
            if now - last_comment >= next_comment_in:
                do_comment()
                last_comment = time.time()
                next_comment_in = random.randint(COMMENT_INTERVAL_MIN, COMMENT_INTERVAL_MAX)
                log(f"Next comment in {next_comment_in//60} min")

            # Heartbeat check
            if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                do_heartbeat()
                last_heartbeat = time.time()

            time.sleep(30)

        except KeyboardInterrupt:
            log("Shutting down gracefully...")
            break
        except Exception as e:
            log(f"Loop error: {e}")
            traceback.print_exc()
            time.sleep(60)


if __name__ == "__main__":
    main()
