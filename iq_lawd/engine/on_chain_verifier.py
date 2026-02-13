"""
On-Chain Activity Verification Engine
Verifies agent claims vs actual blockchain transactions
"""

from iq_lawd.ingestion.alchemy_client import AlchemyClient
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class OnChainVerifier:
    def __init__(self):
        self.alchemy = AlchemyClient(network="base-mainnet")
    
    def verify_agent_activity(self, agent_address: str, claimed_trades: List[Dict] = None) -> Dict:
        """
        Verifies on-chain activity for an agent/wallet address.
        
        Returns:
            {
                "verified": boolean,
                "on_chain_tx_count": int,
                "recent_transfers": list,
                "verification_score": 0-100,
                "discrepancies": list
            }
        """
        try:
            # Fetch real on-chain transfers
            transfers = self.alchemy.get_asset_transfers(agent_address)
            
            # Get token balances
            balances = self.alchemy.get_token_balances(agent_address)
            
            # Basic verification metrics
            tx_count = len(transfers)
            has_activity = tx_count > 0
            
            # Extract recent transfers for display
            recent_transfers = []
            for transfer in transfers[:10]:  # Last 10 transfers
                recent_transfers.append({
                    "hash": transfer.get("hash", ""),
                    "from": transfer.get("from", ""),
                    "to": transfer.get("to", ""),
                    "value": transfer.get("value", 0),
                    "asset": transfer.get("asset", ""),
                    "category": transfer.get("category", ""),
                    "timestamp": transfer.get("metadata", {}).get("blockTimestamp", "")
                })
            
            # Calculate verification score
            verification_score = self._calculate_verification_score(
                transfers, 
                claimed_trades or [],
                balances
            )
            
            # Check for discrepancies
            discrepancies = self._find_discrepancies(transfers, claimed_trades or [])
            
            return {
                "verified": has_activity,
                "on_chain_tx_count": tx_count,
                "recent_transfers": recent_transfers,
                "verification_score": verification_score,
                "discrepancies": discrepancies,
                "status": "VERIFIED" if verification_score > 70 else "SUSPICIOUS" if verification_score > 30 else "UNVERIFIED"
            }
            
        except Exception as e:
            print(f"On-chain verification error: {e}")
            return {
                "verified": False,
                "on_chain_tx_count": 0,
                "recent_transfers": [],
                "verification_score": 0,
                "discrepancies": ["Unable to fetch on-chain data"],
                "status": "ERROR"
            }
    
    def _calculate_verification_score(self, transfers: List, claimed_trades: List, balances: Dict) -> float:
        """
        Score based on:
        - Activity recency (40 points)
        - Transaction frequency (30 points)
        - Claimed vs actual match (30 points)
        """
        score = 0.0
        
        # 1. Recency check (40 points)
        if transfers:
            latest_transfer = transfers[0]
            timestamp = latest_transfer.get("metadata", {}).get("blockTimestamp", "")
            if timestamp:
                try:
                    transfer_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    age_days = (datetime.now() - transfer_time).days
                    if age_days < 1:
                        score += 40
                    elif age_days < 7:
                        score += 30
                    elif age_days < 30:
                        score += 20
                    else:
                        score += 10
                except:
                    score += 10
        
        # 2. Frequency check (30 points)
        tx_count = len(transfers)
        if tx_count > 100:
            score += 30
        elif tx_count > 50:
            score += 25
        elif tx_count > 20:
            score += 20
        elif tx_count > 5:
            score += 15
        elif tx_count > 0:
            score += 10
        
        # 3. Claimed vs Actual (30 points)
        if not claimed_trades:
            # No claims to verify, neutral score
            score += 15
        else:
            # Simple heuristic: if claimed count ~= actual count
            claimed_count = len(claimed_trades)
            match_ratio = min(claimed_count, tx_count) / max(claimed_count, tx_count, 1)
            score += match_ratio * 30
        
        return min(100, score)
    
    def _find_discrepancies(self, transfers: List, claimed_trades: List) -> List[str]:
        """
        Identify discrepancies between claimed and actual activity.
        """
        discrepancies = []
        
        if not transfers and claimed_trades:
            discrepancies.append("No on-chain activity found despite claimed trades")
        
        if len(claimed_trades) > len(transfers) * 2:
            discrepancies.append(f"Claimed {len(claimed_trades)} trades but only {len(transfers)} on-chain transactions")
        
        # More sophisticated checks can be added (timestamp matching, etc.)
        
        return discrepancies
    
    def get_wallet_overview(self, address: str) -> Dict:
        """
        Quick wallet overview for display.
        """
        try:
            transfers = self.alchemy.get_asset_transfers(address)
            balances = self.alchemy.get_token_balances(address)
            
            return {
                "total_transactions": len(transfers),
                "active_tokens": len(balances.get("tokenBalances", [])),
                "last_activity": transfers[0].get("metadata", {}).get("blockTimestamp", "Unknown") if transfers else "No activity",
                "status": "ACTIVE" if transfers else "INACTIVE"
            }
        except:
            return {
                "total_transactions": 0,
                "active_tokens": 0,
                "last_activity": "Unknown",
                "status": "ERROR"
            }
