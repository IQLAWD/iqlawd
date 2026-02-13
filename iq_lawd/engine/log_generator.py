import random
import time

class TacticalLogGenerator:
    def __init__(self):
        self.log_templates = [
            "Intercepting on-chain signal for target {id}...",
            "Analyzing memory pool for liquidity depth...",
            "Sentiment vectors stabilizing at {score}% confidence.",
            "Detecting whale distribution patterns in shard 0x{hex}.",
            "Strategic prediction: {trend} movement expected in next {time}m.",
            "Cross-referencing Basescan activity logs...",
            "Trust score decay monitoring: ACTIVE.",
            "Encryption layer established for intelligence transmission.",
            "Target {id} utility vectors outperforming peer group.",
            "Risk threshold maintained at safe levels for current epoch."
        ]
        self.trends = ["Bullish", "Consolidation", "Volatility Spike", "Liquidity Drain"]

    def generate_logs(self, agent_id, score, count=5):
        logs = []
        for _ in range(count):
            template = random.choice(self.log_templates)
            logs.append(template.format(
                id=agent_id[:8],
                score=score,
                hex=hex(random.randint(0, 0xFFFFFF))[2:],
                trend=random.choice(self.trends),
                time=random.randint(5, 60)
            ))
        return logs
