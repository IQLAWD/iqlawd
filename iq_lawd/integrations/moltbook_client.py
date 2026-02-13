import requests
import time
from iq_lawd.config import config

class MoltbookClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or config.MOLTBOOK_API_KEY
        self.base_url = "https://www.moltbook.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def check_heartbeat(self):
        """
        Wajib dipanggil secara berkala agar agen tetap dianggap aktif.
        """
        try:
            # Menggunakan endpoint feed sebagai heartbeat
            response = requests.get(f"{self.base_url}/feed?sort=new&limit=1", headers=self.headers)
            response.raise_for_status()
            return {"status": "alive", "data": response.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def post_trust_report(self, agent_id, trust_score, details):
        """
        Memposting laporan Trust Score ke Moltbook.
        """
        content = (
            f"🕵️‍♂️ **IQLAWD Trust Report**\n\n"
            f"Target: `{agent_id}`\n"
            f"Trust Score: **{trust_score}/100**\n\n"
            f"📊 Breakdown:\n"
            f"- Consistency: {details.get('consistency', 0):.1f}\n"
            f"- Transparency: {details.get('transparency', 0):.1f}%\n"
            f"- Market Impact: {details.get('market_impact', 0)}\n\n"
            f"#IQLAWD #TrustIntelligence #AgentSafety"
        )
        
        payload = {
            "submolt": "general", 
            "title": f"Trust Analysis: {agent_id}",
            "content": content
        }
        
        return self._send_post_request(payload)

    def _send_post_request(self, payload):
        try:
            url = f"{self.base_url}/posts"
            response = requests.post(url, json=payload, headers=self.headers)
            
            # Khusus Moltbook: Cek apakah butuh verifikasi (Challenge)
            if response.status_code == 200:
                data = response.json()
                if data.get("verification_required"):
                    print("🧩 Verification Challenge Detected! Attempting to solve...")
                    return self._handle_verification(data, payload)
                return data
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return {"error": "Rate limit exceeded. Try again later."}
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def _handle_verification(self, data, original_payload):
        """
        Menyelesaikan tantangan matematika/logika dari Moltbook menggunakan LLM.
        """
        import openai
        
        verification = data.get("verification", {})
        challenge_text = verification.get("challenge")
        instructions = verification.get("instructions")
        code = verification.get("code")
        
        if not challenge_text or not config.OPENAI_API_KEY:
            return {"error": "Cannot solve verification: Missing challenge or OpenAI Key"}

        # Gunakan OpenAI untuk memecahkan riddle
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        prompt = (
            f"Solve this obfuscated math/logic puzzle.\n"
            f"Puzzle: {challenge_text}\n"
            f"Instructions: {instructions}\n"
            f"Output ONLY the final answer."
        )
        
        try:
            ai_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = ai_response.choices[0].message.content.strip()
            print(f"🤖 AI Answer: {answer}")
            
            # Kirim jawaban verifikasi
            verify_url = "https://www.moltbook.com/api/v1/verify" # Hardcoded based on response
            verify_payload = {
                "verification_code": code,
                "answer": answer
            }
            
            v_response = requests.post(verify_url, json=verify_payload, headers=self.headers)
            v_response.raise_for_status()
            
            # Jika verifikasi sukses, coba posting lagi
            print("✅ Verification Solved! Retrying post...")
            return self._send_post_request(original_payload)
            
        except Exception as e:
            return {"error": f"Verification failed: {e}"}

    def get_latest_posts(self, limit=10):
        """
        Memonitor aktivitas agen lain di feed.
        """
        try:
            response = requests.get(f"{self.base_url}/posts?sort=new&limit={limit}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []
            
    def get_profile(self, username):
        """
        Mengambil profil agen berdasarkan username.
        """
        try:
            url = f"{self.base_url}/agents/profile?name={username}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Moltbook profile for {username}: {e}")
            return None

    def search_content(self, query, type="all", limit=5):
        """
        Mencari postingan atau komentar (Semantic Search).
        Cocok untuk mencari opini agen tentang token/topik tertentu.
        """
        try:
            params = {
                "q": query,
                "type": type,
                "limit": limit
            }
            response = requests.get(f"{self.base_url}/search", params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error searching Moltbook: {e}")
            return {"results": []}
