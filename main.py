import sys
from datetime import datetime
from iq_lawd.engine.trust_score import TrustScoreCalculator
from iq_lawd.engine.utility_score import UtilityScoreCalculator
from iq_lawd.engine.risk_monitor import RiskMonitor
from iq_lawd.engine.behavior_trace import BehaviorTrace

def main():
    print("=== IQLAWD Agent Trust Intelligence System ===")
    
    # Inisialisasi Engine
    trust_engine = TrustScoreCalculator()
    utility_engine = UtilityScoreCalculator()
    risk_monitor = RiskMonitor()
    tracer = BehaviorTrace()

    # --- Simulasi Data Agen (Mock) ---
    agent_id = "0xAgentJamesBond"
    print(f"\nAnalyzing Agent: {agent_id}")
    
    # Data Transaksi (Mock)
    mock_trades = [
        {"roi": 10.5, "timestamp": "2023-10-26T10:00:00"},
        {"roi": -2.1, "timestamp": "2023-10-26T12:00:00"},
        {"roi": 5.0,  "timestamp": "2023-10-26T14:00:00"},
        {"roi": 8.2,  "timestamp": "2023-10-26T16:00:00"}
    ]
    
    # Data Catatan On-Chain (Transparency)
    mock_notes = [
        {"tx_hash": "0x123", "reason": "Market momentum breakout detected"},
        {"tx_hash": "0x124", "reason": None}, # Tidak transparan
        {"tx_hash": "0x125", "reason": "Take profit at resistance"}
    ]
    
    # Data Market Impact (Volatility)
    mock_market = {
        "priceChange": {"h1": 2.5}, # Harga naik 2.5% setelah entry (Bagus)
        "volume": 500000
    }
    
    # Data Utilitas
    mock_usage = {
        "tx_count": 450,        # 450 transaksi/bulan
        "unique_callers": 15,   # 15 smart contract lain bergantung padanya
        "human_pct": 80         # 80% interaksi manusia
    }

    # --- Eksekusi Analisis ---
    
    # 1. Hitung Trust Score
    trust_score, trust_details = trust_engine.compute_total_trust_score({
        "trade_history": mock_trades,
        "notes": mock_notes,
        "market_data": mock_market,
        "performance": None
    })
    
    # 2. Hitung Utility Score
    utility_score, utility_details = utility_engine.compute_total_utility_score(mock_usage)
    
    # 3. Cek Risiko
    drift_status = risk_monitor.check_strategy_drift(mock_trades, mock_trades) # Mocking same history
    
    # 4. Log Trace
    tracer.log_event(agent_id, "ANALYSIS_COMPLETE", f"Trust: {trust_score}, Utility: {utility_score}")

    # --- Output Laporan ---
    print("\n[REPORT GENERATED]")
    print(f"TRUST SCORE  : {trust_score} / 100")
    print(f"Details      : {trust_details}")
    print("-" * 30)
    print(f"UTILITY SCORE: {utility_score} / 100")
    print(f"Details      : {utility_details}")
    print("-" * 30)
    print(f"RISK STATUS  : Strategy Drift = {drift_status}")
    print("==============================================")

if __name__ == "__main__":
    main()
