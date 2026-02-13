from openai import OpenAI
from iq_lawd.config import config
import json

class AIAnalyst:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4o-mini" # Fast and efficient for reports

    def generate_verdict(self, agent_data: dict) -> str:
        """
        Generates a concise AI-driven 'Intelligence Briefing' or 'Verdict' 
        based on the 4-pillar verification breakdown.
        """
        username = agent_data.get('username')
        final_score = agent_data.get('final_score')
        breakdown = agent_data.get('breakdown', {})
        
        prompt = f"""
        Analyze the following Moltbook Agent verification data and provide a concise 'Intelligence Verdict' (max 3 sentences).
        The verdict should explain WHY the agent got this score and any potential red flags or trust signals.
        
        AGENT: @{username}
        FINAL TRUST SCORE: {final_score}/100
        
        BREAKDOWN:
        1. Karma (25%): {breakdown.get('karma', {}).get('raw')} units (Normalized: {breakdown.get('karma', {}).get('normalized')}/25)
        2. Reputation (30%): {breakdown.get('reputation', {}).get('total')}/30
           - Quality: {breakdown.get('reputation', {}).get('details', {}).get('post_quality')}%
           - Consistency: {breakdown.get('reputation', {}).get('details', {}).get('consistency')}%
        3. Web Presence (25%): {breakdown.get('web_presence', {}).get('total')}/25
           - Has Website: {breakdown.get('web_presence', {}).get('details', {}).get('has_website')}
           - Has SSL: {breakdown.get('web_presence', {}).get('details', {}).get('has_ssl')}
        4. Crypto Influence (20%): {breakdown.get('crypto_influence', {}).get('total')}/20
        
        Format the response in a professional, slightly 'cyber-oracle' tone. Provide the response in English.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are the IQLAWD Oracle, an advanced AI designed to verify the legitimacy of Moltbook agents. Your verdicts are used by the community to decide who to trust."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Verdict failed: {e}")
            return "AI Oracle temporarily offline. Manual cross-referencing advised."

    def generate_comparison(self, agent_a: dict, agent_b: dict) -> str:
        """
        Generates a side-by-side comparison verdict for two agents.
        """
        prompt = f"""
        Compare the following two Moltbook Agents and provide a concise 'Comparison Verdict' (max 3 sentences).
        Highlight which agent has better trust signals and if there are significant gaps between them.

        AGENT A: @{agent_a.get('username')} (Score: {agent_a.get('final_score')})
        AGENT B: @{agent_b.get('username')} (Score: {agent_b.get('final_score')})

        PILLAR DATA A: {json.dumps(agent_a.get('breakdown'))}
        PILLAR DATA B: {json.dumps(agent_b.get('breakdown'))}

        Format the response in a professional, slightly 'cyber-oracle' tone. Provide the response in English.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are the IQLAWD Oracle. You provide side-by-side binary comparisons for Moltbook agents to help the community prioritize high-integrity identities."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Comparison failed: {e}")
            return "Comparison Oracle temporarily offline. Binary analysis unavailable."

ai_analyst = AIAnalyst()
