"""
Risk Engine for Card Transaction Monitoring
Evaluates transactions against multiple risk vectors and outputs a decision.
"""

from typing import Dict, Any, List


class CardRiskEngine:
    def __init__(self, high_risk_countries: List[str] = None):
        self.high_risk_countries = high_risk_countries or ["XX", "YY", "ZZ"]  # Replace with actual codes

    def evaluate_transaction(self, transaction: Dict[str, Any], user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluates a single transaction payload and returns a risk score and recommendation.
        
        Transaction Schema Example:
        {
            "transaction_id": "tx_12345",
            "amount": 450.00,
            "currency": "USD",
            "country": "US",
            "velocity_24h": 3,
            "is_international": False
        }
        """
        risk_score = 0.0
        flags = []

        amount = transaction.get("amount", 0.0)
        country = transaction.get("country", "US")
        velocity = transaction.get("velocity_24h", 0)
        is_international = transaction.get("is_international", False)

        # 1. Amount Threshold Rule
        if amount > 1000.0:
            risk_score += 40.0
            flags.append("HIGH_AMOUNT_THRESHOLD")
        elif amount > 500.0:
            risk_score += 20.0
            flags.append("MEDIUM_AMOUNT_THRESHOLD")

        # 2. Velocity Check (Frequent transactions in a short window)
        if velocity > 5:
            risk_score += 35.0
            flags.append("HIGH_VELOCITY_SPIKE")
        elif velocity > 3:
            risk_score += 15.0
            flags.append("MODERATE_VELOCITY")

        # 3. Geographic Risk
        if country in self.high_risk_countries:
            risk_score += 50.0
            flags.append("HIGH_RISK_JURISDICTION")
        elif is_international:
            risk_score += 10.0
            flags.append("INTERNATIONAL_TRANSACTION")

        # 4. Determine Action / Decision
        if risk_score >= 70.0:
            decision = "DECLINE"
        elif risk_score >= 40.0:
            decision = "REVIEW"
        else:
            decision = "APPROVE"

        return {
            "transaction_id": transaction.get("transaction_id"),
            "risk_score": round(risk_score, 2),
            "decision": decision,
            "triggered_flags": flags
        }


# Quick local test
if __name__ == "__main__":
    engine = CardRiskEngine()
    sample_tx = {
        "transaction_id": "TX998822",
        "amount": 1250.00,
        "currency": "USD",
        "country": "US",
        "velocity_24h": 6,
        "is_international": False
    }
    print(engine.evaluate_transaction(sample_tx))
