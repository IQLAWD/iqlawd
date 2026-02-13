#!/usr/bin/env python3
"""Final fix: patch database.py get_listings to return frontend-compatible fields, 
   and add /factions route to server.py"""
import paramiko
import time

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)

sftp = ssh.open_sftp()

def run(cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"OUT: {out[:3000]}")
    if err:
        print(f"ERR: {err[:1500]}")
    return out, err

# ========================================
# STEP 1: Patch database.py - get_listings
# ========================================
print("📝 Step 1: Patching database.py get_listings")

patch_db_script = '''
import re

filepath = "/root/iq_lawd_v2/iq_lawd/database.py"
with open(filepath, "r") as f:
    content = f.read()

# Find and replace get_listings method
old_method = """    def get_listings(self, sort_by='trust_score', limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()

        order_clause = "s.trust_score DESC"
        if sort_by == 'newest':
            order_clause = "a.first_seen DESC"
        elif sort_by == 'votes':
            order_clause = "(upvotes - downvotes) DESC"

        query = f\\'\\'\\'
        SELECT
            a.*,
            s.trust_score,
            s.risk_status,
            (SELECT COUNT(*) FROM votes WHERE agent_id = a.id AND vote_type = 'UP') as upvotes,
            (SELECT COUNT(*) FROM votes WHERE agent_id = a.id AND vote_type = 'DOWN') as downvotes
        FROM agents a
        LEFT JOIN (
            SELECT agent_id, trust_score, risk_status
            FROM scan_results
            WHERE id IN (SELECT MAX(id) FROM scan_results GROUP BY agent_id)
        ) s ON a.id = s.agent_id
        ORDER BY {order_clause}
        LIMIT ?
        \\'\\'\\'

        cursor.execute(query, (limit,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results"""

new_method = """    def get_listings(self, sort_by='trust_score', limit=50):
        import json as _json
        conn = self.get_connection()
        cursor = conn.cursor()

        order_clause = "s.trust_score DESC"
        if sort_by == 'newest':
            order_clause = "a.first_seen DESC"
        elif sort_by == 'votes':
            order_clause = "(upvotes - downvotes) DESC"
        elif sort_by == 'score':
            order_clause = "s.trust_score DESC"

        query = f\\'\\'\\'
        SELECT
            a.*,
            s.trust_score,
            s.risk_status,
            s.details_json,
            (SELECT COUNT(*) FROM votes WHERE agent_id = a.id AND vote_type = 'UP') as upvotes,
            (SELECT COUNT(*) FROM votes WHERE agent_id = a.id AND vote_type = 'DOWN') as downvotes
        FROM agents a
        LEFT JOIN (
            SELECT agent_id, trust_score, risk_status, details_json
            FROM scan_results
            WHERE id IN (SELECT MAX(id) FROM scan_results GROUP BY agent_id)
        ) s ON a.id = s.agent_id
        ORDER BY {order_clause}
        LIMIT ?
        \\'\\'\\'

        cursor.execute(query, (limit,))
        results = []
        for row in cursor.fetchall():
            r = dict(row)
            # Parse details_json to extract extra fields
            details = {}
            if r.get('details_json'):
                try:
                    details = _json.loads(r['details_json'])
                except:
                    pass
            # Map to frontend-compatible format
            results.append({
                'username': r.get('id', ''),
                'display_name': r.get('name') or r.get('symbol', 'Unknown'),
                'avatar_url': r.get('image_url', ''),
                'final_score': r.get('trust_score', 0) or 0,
                'karma': details.get('karma', 0),
                'verification_status': details.get('verification_status', 'PENDING'),
                'faction': details.get('faction', 'Neutral'),
                'risk_status': r.get('risk_status', 'STABLE'),
                'upvotes': r.get('upvotes', 0),
                'downvotes': r.get('downvotes', 0),
                'price_usd': r.get('price_usd'),
                'price_change_24h': r.get('price_change_24h'),
                'liquidity_usd': r.get('liquidity_usd'),
                'network': r.get('network', 'base'),
                'symbol': r.get('symbol', ''),
                'social': details.get('social', {}),
            })
        conn.close()
        return results"""

if old_method in content:
    content = content.replace(old_method, new_method)
    with open(filepath, "w") as f:
        f.write(content)
    print("SUCCESS: Patched get_listings!")
else:
    print("WARNING: Could not find exact old method. Trying fuzzy match...")
    # Try to find by function signature
    import re
    pattern = r"(    def get_listings\\(self.*?)(    def )"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_method + "\\n\\n" + match.group(2) + content[match.end():]
        with open(filepath, "w") as f:
            f.write(content)
        print("SUCCESS: Patched via regex!")
    else:
        print("FAILED: Could not find method to patch")
'''

with sftp.file('/root/iq_lawd_v2/patch_db.py', 'w') as f:
    f.write(patch_db_script)

run("cd /root/iq_lawd_v2 && python3 patch_db.py")

# ========================================
# STEP 2: Add /factions route to server.py
# ========================================
print("\n📝 Step 2: Adding /factions route")

# Write factions module
factions_module = '''# Factions endpoint module
def register_factions_route(app, db):
    @app.get("/factions")
    def get_factions():
        import json
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                json_extract(sr.details_json, '$.faction') as faction,
                COUNT(*) as count,
                AVG(sr.trust_score) as avg_trust,
                SUM(CASE WHEN sr.risk_status = 'STABLE' THEN 1 ELSE 0 END) as stable_count
            FROM scan_results sr
            WHERE sr.id IN (SELECT MAX(id) FROM scan_results GROUP BY agent_id)
            AND json_extract(sr.details_json, '$.faction') IS NOT NULL
            GROUP BY faction
            """)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Factions error: {e}")
            return []
'''

with sftp.file('/root/iq_lawd_v2/iq_lawd/api/factions.py', 'w') as f:
    f.write(factions_module)

# Patch server.py to import factions
patch_server_script = '''
filepath = "/root/iq_lawd_v2/iq_lawd/api/server.py"
with open(filepath, "r") as f:
    content = f.read()

changed = False

# Add import if not present
if "factions" not in content:
    content = content.replace(
        "from iq_lawd.database import db",
        "from iq_lawd.database import db\\nfrom iq_lawd.api.factions import register_factions_route"
    )
    changed = True

# Add registration if not present
if "register_factions_route" not in content or "register_factions_route(app" not in content:
    # Add after CORS middleware
    content = content.replace(
        '# --- Endpoints ---',
        '# Register additional routes\\nregister_factions_route(app, db)\\n\\n# --- Endpoints ---'
    )
    changed = True

if changed:
    with open(filepath, "w") as f:
        f.write(content)
    print("SUCCESS: Patched server.py with factions!")
else:
    print("Already patched")
'''

with sftp.file('/root/iq_lawd_v2/patch_server_factions.py', 'w') as f:
    f.write(patch_server_script)

run("cd /root/iq_lawd_v2 && python3 patch_server_factions.py")

sftp.close()

# ========================================
# STEP 3: Restart backend
# ========================================
print("\n🔄 Step 3: Restarting backend...")
run("pm2 restart iqlawd-api")
time.sleep(5)

# ========================================
# STEP 4: Verify
# ========================================
print("\n✅ Step 4: Verify all endpoints")
run("pm2 list")

print("\n/listings (formatted):")
run("curl -s http://localhost:8000/listings?sort=score 2>&1 | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps(d[0] if d else {}, indent=2))'")

print("\n/factions:")
run("curl -s http://localhost:8000/factions 2>&1")

print("\nBackend logs:")
run("pm2 logs iqlawd-api --nostream --lines 5 2>&1")

# Save PM2
run("pm2 save")

ssh.close()
print("\n✅ ALL FIXES COMPLETE!")
