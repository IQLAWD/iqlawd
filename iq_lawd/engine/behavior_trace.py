from datetime import datetime

class BehaviorTrace:
    def __init__(self):
        self.logs = []

    def log_event(self, agent_id, event_type, details, market_reaction="neutral", trust_delta=0.0):
        """
        Mencatat event eksekusi agen.
        [TIMESTAMP] Agent executed trade -> Market reaction: neutral -> Trust delta: +0.3
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "event_type": event_type,
            "details": details,
            "market_reaction": market_reaction,
            "trust_delta": trust_delta
        }
        self.logs.append(entry)
        print(f"[{entry['timestamp']}] {event_type} | Reaction: {market_reaction} | Trust Delta: {trust_delta}")

    def get_logs(self, agent_id=None):
        """
        Retrieve logs for specific agent or all logs if agent_id is None.
        """
        if agent_id:
            return [log for log in self.logs if log['agent_id'] == agent_id]
        return self.logs
