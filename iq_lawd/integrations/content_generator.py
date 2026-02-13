import openai
from iq_lawd.config import config

class ContentGenerator:
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        print(f"Initializing ContentGenerator with API key: {self.api_key[:5]}...{self.api_key[-5:] if self.api_key else 'None'}")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_trust_report_post(self, agent_id, trust_score, details, style="analytical"):
        """
        Menggunakan OpenAI untuk menulis postingan Moltbook yang menarik.
        Styles: analytical, witty, warning (if score low).
        """
        prompt = (
            f"Write a short, engaging social media post for 'Moltbook' (a platform for AI agents). "
            f"Subject: Trust Analysis of Agent '{agent_id}'.\n"
            f"Data:\n"
            f"- Trust Score: {trust_score}/100\n"
            f"- Consistency: {details.get('consistency')}/100\n"
            f"- Transparency: {details.get('transparency')}%\n"
            f"- Market Impact: {details.get('market_impact')}/100\n\n"
            f"Style: {style}.\n"
            f"Constraints: Use emojis. Max 280 chars. Include hashtags #IQLAWD #TrustIntelligence."
        )

        try:
            print(f"Generating Moltbook post for {agent_id}...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are IQLAWD, an advanced AI Trust Intelligence Sentinel. You analyze other agents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                timeout=10.0
            )
            print(f"Moltbook post generated for {agent_id}.")
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI Error for {agent_id} (Moltbook post): {e}")
            # Fallback ke format manual jika AI gagal
            return f"🕵️‍♂️ Analysis Results for {agent_id}: Trust Score {trust_score}/100. #IQLAWD"

    def generate_summary(self, agent_id, trust_score, market_data):
        """
        Menghasilkan ringkasan intelejen singkat (1-2 kalimat) untuk dashboard.
        """
        prompt = (
            f"Generate a professional, concise 1-sentence intelligence summary for an AI Agent token.\n"
            f"ID: {agent_id}\n"
            f"Trust Score: {trust_score}/100\n"
            f"Market Context: Liquidity ${market_data.get('liquidity', {}).get('usd')}, 24h Change {market_data.get('priceChange', {}).get('h24')}%.\n"
            f"Focus on whether it's stable, high-risk, or showing growth potential. Be precise."
        )
        try:
            print(f"Generating AI intelligence for {agent_id}...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are IQLAWD Intelligence, an on-chain risk analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                timeout=10.0
            )
            print(f"AI intelligence generated for {agent_id}.")
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI Summary Error for {agent_id}: {e}")
            return "Intelligence data stabilized. Monitoring ongoing clinical indicators."

