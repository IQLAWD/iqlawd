class UtilityScoreCalculator:
    def __init__(self):
        pass

    def calculate_usage_frequency(self, tx_count_30d):
        """
        Seberapa aktif agen digunakan?
        """
        # Linear scaling sampai batas tertentu (misal 1000 tx/bulan = 100 skor)
        return min(100, (tx_count_30d / 1000) * 100)

    def calculate_dependency(self, unique_callers):
        """
        Berapa banyak unique address/contract lain yang memanggil agen ini?
        Menandakan "Dependency by other agents".
        """
        # Logarithmic scaling agar tidak bias ke whale
        if unique_callers == 0:
            return 0
        import math
        score = math.log(unique_callers, 10) * 20 # log10(100) = 2 * 20 = 40
        return min(100, score)

    def calculate_real_user_interaction(self, human_interactions):
        """
        Membedakan interaksi bot vs manusia (berdasarkan pola wallet).
        """
        # Placeholder: Asumsikan input adalah persentase interaksi non-bot
        return min(100, human_interactions)

    def compute_total_utility_score(self, usage_data):
        frequency = self.calculate_usage_frequency(usage_data.get('tx_count', 0))
        dependency = self.calculate_dependency(usage_data.get('unique_callers', 0))
        interaction = self.calculate_real_user_interaction(usage_data.get('human_pct', 0))
        
        # Bobot rata
        total_score = (frequency + dependency + interaction) / 3
        
        return round(total_score, 2), {
            "frequency": frequency,
            "dependency": dependency,
            "interaction": interaction
        }
