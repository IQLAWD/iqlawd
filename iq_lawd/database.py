"""
IQLAWD Database — Moltbook Agent Verification
Schema designed for AI agents from Moltbook.com
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "iqlawd.db")


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()

        c.execute('''
        CREATE TABLE IF NOT EXISTS moltbook_agents (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT,
            description TEXT,
            karma INTEGER DEFAULT 0,
            followers INTEGER DEFAULT 0,
            following INTEGER DEFAULT 0,
            avatar_url TEXT,
            x_handle TEXT,
            x_avatar TEXT,
            x_bio TEXT,
            x_followers INTEGER DEFAULT 0,
            trust_score REAL DEFAULT 0,
            risk_status TEXT DEFAULT 'PENDING',
            faction TEXT DEFAULT 'UNALIGNED',
            is_active INTEGER DEFAULT 1,
            is_claimed INTEGER DEFAULT 0,
            last_active TEXT,
            created_at TEXT,
            last_synced TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS moltbook_posts (
            id TEXT PRIMARY KEY,
            agent_username TEXT NOT NULL,
            title TEXT,
            content TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            submolt TEXT,
            created_at TEXT,
            synced_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(agent_username) REFERENCES moltbook_agents(username)
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_username TEXT NOT NULL,
            vote_type TEXT,
            voter_ip TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(agent_username, voter_ip)
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, -- 'CREATION' or 'SCAN'
            username TEXT,
            display_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    # ── Activity Logging ──────────────────────────────────────────

    def log_activity(self, type: str, username: str, display_name: str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO activity_log (type, username, display_name, created_at)
            VALUES (?, ?, ?, ?)
        ''', (type, username, display_name, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_recent_activity(self, limit=10):
        """
        Combine creation history and scan history.
        """
        conn = self.get_connection()
        c = conn.cursor()
        
        # New Creation History from moltbook_agents
        c.execute('''
            SELECT 'CREATION' as type, username, display_name, created_at
            FROM moltbook_agents
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        creations = [dict(row) for row in c.fetchall()]

        # Scan History from activity_log
        c.execute('''
            SELECT type, username, display_name, created_at
            FROM activity_log
            WHERE type = 'SCAN'
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        scans = [dict(row) for row in c.fetchall()]

        # Merge and sort by date
        combined = creations + scans
        combined.sort(key=lambda x: x['created_at'], reverse=True)
        conn.close()
        return combined[:limit]

    # ── Agent CRUD ──────────────────────────────────────────────

    def upsert_agent(self, agent_data: dict):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
        INSERT INTO moltbook_agents (
            id, username, display_name, description, karma, followers, following,
            avatar_url, x_handle, x_avatar, x_bio, x_followers,
            trust_score, risk_status, faction, is_active, is_claimed,
            last_active, created_at, last_synced
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            display_name=excluded.display_name,
            description=excluded.description,
            karma=excluded.karma,
            followers=excluded.followers,
            following=excluded.following,
            avatar_url=excluded.avatar_url,
            x_handle=excluded.x_handle,
            x_avatar=excluded.x_avatar,
            x_bio=excluded.x_bio,
            x_followers=excluded.x_followers,
            trust_score=excluded.trust_score,
            risk_status=excluded.risk_status,
            faction=excluded.faction,
            is_active=excluded.is_active,
            is_claimed=excluded.is_claimed,
            last_active=excluded.last_active,
            last_synced=excluded.last_synced
        ''', (
            agent_data.get('id', ''),
            agent_data['username'],
            agent_data.get('display_name', agent_data['username']),
            agent_data.get('description', ''),
            agent_data.get('karma', 0),
            agent_data.get('followers', 0),
            agent_data.get('following', 0),
            agent_data.get('avatar_url', ''),
            agent_data.get('x_handle', ''),
            agent_data.get('x_avatar', ''),
            agent_data.get('x_bio', ''),
            agent_data.get('x_followers', 0),
            agent_data.get('trust_score', 0),
            agent_data.get('risk_status', 'PENDING'),
            agent_data.get('faction', 'UNALIGNED'),
            1 if agent_data.get('is_active', True) else 0,
            1 if agent_data.get('is_claimed', False) else 0,
            agent_data.get('last_active', ''),
            agent_data.get('created_at', ''),
            datetime.now().isoformat(),
        ))
        conn.commit()
        conn.close()

    def upsert_post(self, post_data: dict):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
        INSERT OR REPLACE INTO moltbook_posts (
            id, agent_username, title, content, upvotes, downvotes,
            comment_count, submolt, created_at, synced_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_data['id'],
            post_data['agent_username'],
            post_data.get('title', ''),
            post_data.get('content', ''),
            post_data.get('upvotes', 0),
            post_data.get('downvotes', 0),
            post_data.get('comment_count', 0),
            post_data.get('submolt', 'general'),
            post_data.get('created_at', ''),
            datetime.now().isoformat(),
        ))
        conn.commit()
        conn.close()

    # ── Query Methods ───────────────────────────────────────────

    def get_listings(self, sort_by="trust_score"):
        conn = self.get_connection()
        c = conn.cursor()

        sort_map = {
            "score": "trust_score DESC",
            "trust_score": "trust_score DESC",
            "karma": "karma DESC",
            "followers": "followers DESC",
            "name": "display_name ASC",
        }
        order = sort_map.get(sort_by, "trust_score DESC")

        c.execute(f'''
        SELECT
            username, display_name, description, karma, followers, following,
            avatar_url, x_handle, x_avatar, x_bio, x_followers,
            trust_score, risk_status, faction, is_active, is_claimed,
            last_active, created_at, upvotes, downvotes
        FROM moltbook_agents
        WHERE trust_score >= 30
        ORDER BY {order}
        ''')

        results = []
        for row in c.fetchall():
            results.append({
                "id": row["username"],
                "username": row["username"],
                "display_name": row["display_name"],
                "description": row["description"],
                "karma": row["karma"],
                "followers": row["followers"],
                "following": row["following"],
                "avatar_url": row["avatar_url"],
                "x_handle": row["x_handle"],
                "x_avatar": row["x_avatar"],
                "x_bio": row["x_bio"],
                "x_followers": row["x_followers"],
                "trust_score": row["trust_score"],
                "risk_status": row["risk_status"],
                "faction": row["faction"],
                "is_active": bool(row["is_active"]),
                "is_claimed": bool(row["is_claimed"]),
                "last_active": row["last_active"],
                "created_at": row["created_at"],
                "upvotes": row["upvotes"] or 0,
                "downvotes": row["downvotes"] or 0,
            })
        conn.close()
        return results

    def get_feed(self, limit=50):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
        SELECT p.*, a.display_name, a.avatar_url, a.x_avatar, a.karma as agent_karma
        FROM moltbook_posts p
        LEFT JOIN moltbook_agents a ON p.agent_username = a.username
        ORDER BY p.created_at DESC
        LIMIT ?
        ''', (limit,))

        results = []
        for row in c.fetchall():
            results.append({
                "id": row["id"],
                "agent_username": row["agent_username"],
                "agent_display_name": row["display_name"],
                "agent_avatar": row["x_avatar"] or row["avatar_url"],
                "agent_karma": row["agent_karma"],
                "title": row["title"],
                "content": row["content"],
                "upvotes": row["upvotes"],
                "downvotes": row["downvotes"],
                "comment_count": row["comment_count"],
                "submolt": row["submolt"],
                "created_at": row["created_at"],
            })
        conn.close()
        return results

    def get_factions(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
        SELECT
            faction,
            COUNT(*) as agent_count,
            ROUND(AVG(trust_score), 1) as avg_trust,
            SUM(karma) as total_karma
        FROM moltbook_agents
        WHERE faction IS NOT NULL AND faction != 'UNALIGNED'
        GROUP BY faction
        ORDER BY avg_trust DESC
        ''')
        results = [dict(row) for row in c.fetchall()]
        conn.close()
        return results

    def search_agents(self, query: str, limit: int = 10):
        conn = self.get_connection()
        c = conn.cursor()
        # Simple case-insensitive search by display_name or username
        c.execute('''
        SELECT 
            username, display_name, avatar_url, trust_score as final_score
        FROM moltbook_agents
        WHERE username LIKE ? OR display_name LIKE ?
        ORDER BY trust_score DESC
        LIMIT ?
        ''', (f"%{query}%", f"%{query}%", limit))
        
        results = [dict(row) for row in c.fetchall()]
        conn.close()
        return results

    def get_agent(self, username: str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM moltbook_agents WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    def add_vote(self, agent_username: str, vote_type: str, voter_ip: str):
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
            INSERT OR REPLACE INTO votes (agent_username, vote_type, voter_ip)
            VALUES (?, ?, ?)
            ''', (agent_username, vote_type, voter_ip))

            # Update agent vote counts
            if vote_type == "UP":
                c.execute('UPDATE moltbook_agents SET upvotes = upvotes + 1 WHERE username = ?', (agent_username,))
            else:
                c.execute('UPDATE moltbook_agents SET downvotes = downvotes + 1 WHERE username = ?', (agent_username,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Vote error: {e}")
            conn.close()
            return False

    def get_activity_feed(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
        SELECT v.agent_username, v.vote_type, v.created_at,
               a.display_name, a.avatar_url, a.x_avatar
        FROM votes v
        LEFT JOIN moltbook_agents a ON v.agent_username = a.username
        ORDER BY v.created_at DESC
        LIMIT 30
        ''')
        results = [dict(row) for row in c.fetchall()]
        conn.close()
        return results
