class RiskMonitor:
    def __init__(self):
        pass

    def check_strategy_drift(self, recent_trades, historical_trades):
        """
        Mendeteksi apakah agen tiba-tiba mengubah aset atau frekuensi trading secara drastis
        dibandingkan pola historisnya.
        """
        if not historical_trades or not recent_trades:
            return "INSUFFICIENT_DATA"
            
        # Contoh sederhana: Cek rata-rata jumlah trade per hari
        # Jika tiba-tiba 5x lipat -> Drift Detected
        avg_hist = len(historical_trades) / 30 # Asumsi 30 hari
        avg_rec = len(recent_trades) / 1 # Asumsi 1 hari
        
        if avg_rec > avg_hist * 5:
            return "HIGH_DRIFT_DETECTED"
        elif avg_rec > avg_hist * 2:
            return "MODERATE_DRIFT"
        
        return "STABLE"

    def check_over_optimization(self, win_rate):
        """
        Jika win rate terlalu sempurna (misal 99%) dalam jangka pendek,
        mungkin indicative of overfitting atau ponzi scheme behavior pada data tertentu.
        """
        if win_rate > 95:
            return "SUSPICIOUS_PERFECTION"
        return "NORMAL"

    def monitor_trust_decay(self, trust_score_history):
        """
        Mendeteksi tren penurunan trust score.
        """
        if len(trust_score_history) < 2:
            return "STABLE"
            
        latest = trust_score_history[-1]
        prev = trust_score_history[-2]
        
        if latest < prev - 10:
            return "CRITICAL_DECAY"
        elif latest < prev:
            return "DECAYING"
            
        return "IMPROVING"
