from iq_lawd.config import config
from iq_lawd.config import config
import statistics

class TrustScoreCalculator:
    def __init__(self):
        self.weights = config.TRUST_SCORE_WEIGHTS

    def calculate_consistency(self, trade_history):
        """
        Sub-metric 1: Consistency Index
        Mengukur variabilitas profit dan interval trading.
        """
        if not trade_history:
            return 50.0 # Neutral start
        
        # Contoh logika: Menghitung standar deviasi dari ROI
        rois = [t.get('roi', 0) for t in trade_history]
        rois = [t.get('roi', 0) for t in trade_history]
        std_dev = statistics.stdev(rois) if len(rois) > 1 else 0
        
        # Semakin rendah deviasi, semakin tinggi skor konsistensi (max 100)
        consistency_score = max(0, 100 - (std_dev * 2)) 
        return consistency_score

    def calculate_transparency(self, on_chain_notes):
        """
        Sub-metric 2: Decision Transparency
        Apakah agen menyertakan metadata/catatan alasan di setiap transaksi?
        """
        if not on_chain_notes:
            return 0.0
        
        # Rasio transaksi dengan catatan vs total transaksi
        transparent_count = sum(1 for note in on_chain_notes if note.get('reason'))
        total_count = len(on_chain_notes)
        
        return (transparent_count / total_count) * 100 if total_count > 0 else 0

    def calculate_market_impact(self, market_data):
        """
        Sub-metric 3: Public Reaction Signal
        Analisis volatilitas setelah agen masuk.
        Jika volatilitas ekstrem/dump terjadi setelah buy, skor turun.
        """
        if not market_data:
            return 50.0
            
        price_change = market_data.get('priceChange', {}).get('h1', 0)
        
        # Jika harga naik atau stabil setalah in entry -> Bagus (Trust +)
        # Jika harga dump parah (-10% atau lebih) setelah in -> Buruk (Trust -)
        if price_change > 0:
            return min(100, 50 + price_change * 2)
        else:
            return max(0, 50 + price_change * 2)

    def calculate_recovery(self, performance_history):
        """
        Sub-metric 4: Failure Recovery
        Kemampuan agen bounce back setelah drawdown.
        """
        # Placeholder logic
        # Mendeteksi drawdown terbesar, lalu melihat apakah equity kembali ke ATH
        return 75.0 # Default optimistis untuk saat ini

    def compute_total_trust_score(self, agent_data):
        """
        Menghitung Weighted Average dari semua sub-metrik.
        """
        consistency = self.calculate_consistency(agent_data.get('trade_history'))
        transparency = self.calculate_transparency(agent_data.get('notes'))
        impact = self.calculate_market_impact(agent_data.get('market_data'))
        recovery = self.calculate_recovery(agent_data.get('performance'))
        
        total_score = (
            consistency * self.weights['consistency'] +
            transparency * self.weights['transparency'] +
            impact * self.weights['market_impact'] +
            recovery * self.weights['recovery']
        )
        
        return round(total_score, 2), {
            "consistency": consistency,
            "transparency": transparency,
            "market_impact": impact,
            "recovery": recovery
        }
