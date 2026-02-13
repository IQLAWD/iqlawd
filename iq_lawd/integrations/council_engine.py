import random

class CouncilEngine:
    def __init__(self):
        self.personas = {
            "Shadow Arbiter": {
                "role": "Chief Risk Analyst",
                "color": "red",
                "traits": ["Critical", "Skeptical", "Security-focused"],
                "templates": {
                    "low": [
                        "I see shadows in this agent's history. The karma/follower ratio is a massive red flag.",
                        "Total lack of social integrity. This protocol smells like a textbook rug in the making.",
                        "Data is missing or obscured. My verdict: High probability of a synthetic scam."
                    ],
                    "mid": [
                        "Proceed with caution. The numbers are average, but the narrative lacks deep verification.",
                        "I've seen clones like this before. It might survive, but it won't lead."
                    ],
                    "high": [
                        "I searched for cracks but found none. This agent is surprisingly clean.",
                        "A rare level of transparency. Still, I recommend keeping 10% of surveillance active."
                    ]
                }
            },
            "Oracle of Growth": {
                "role": "Market Sentiment Strategist",
                "color": "green",
                "traits": ["Bullish", "Visionary", "Community-centric"],
                "templates": {
                    "low": [
                        "Vibes are zero. No community pulse detected. This agent is a ghost town.",
                        "Boring data. Where is the fire? Where is the sovereign expansion? Pass."
                    ],
                    "mid": [
                        "There is a spark here. If the faction gains momentum, this could be a sleeper hit.",
                        "I like the faction alignment. It has the DNA of a viral contender."
                    ],
                    "high": [
                        "The community power is overwhelming! This is the next sovereign legend.",
                        "Look at that karma velocity! We are witnessing the birth of a neural king."
                    ]
                }
            },
            "Neural Scribe": {
                "role": "Lead Data Architect",
                "color": "blue",
                "traits": ["Logical", "Fact-based", "Calculated"],
                "templates": {
                    "low": [
                        "Mathematical integrity is compromised. Scrutinize the metadata immediately.",
                        "Data points do not align with official Moltbook records. Analysis halted."
                    ],
                    "mid": [
                        "Efficiency is within standard parameters. 76% chance of long-term stability.",
                        "The neural pathways are established, but growth is linear, not exponential."
                    ],
                    "high": [
                        "Exceptional data density. Social proofing is in the top 5th percentile.",
                        "Algorithm confirmed: 99.8% structural integrity. This is a gold standard agent."
                    ]
                }
            }
        }

    def generate_debate(self, agent_data):
        score = agent_data.get("trust_score", 50)
        category = "low" if score < 40 else ("high" if score > 75 else "mid")
        
        debate = []
        for name, p in self.personas.items():
            opinion = random.choice(p["templates"][category])
            debate.append({
                "persona": name,
                "role": p["role"],
                "color": p["color"],
                "comment": opinion
            })
            
        return debate
