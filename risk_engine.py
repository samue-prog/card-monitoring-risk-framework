from typing import Dict, Any, Tuple

def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))

def avg(values: list) -> float:
    return sum(values) / len(values) if values else 0.0

def score_transaction_risk(txn: Dict[str, Any]) -> float:
    amount_ratio = clamp(txn.get("amount", 0) / max(txn.get("avg_amount_30d", 1), 1), 0, 5) / 5
    amount_anomaly = clamp((amount_ratio * 0.7) + (txn.get("amount", 0) > txn.get("avg_amount_30d", 0) * 3) * 0.3, 0, 1)

    velocity = clamp(txn.get("velocity_score", 0.0), 0, 1)
    mcc_risk = clamp(txn.get("mcc_risk", 0.0), 0, 1)
    country_risk = clamp(txn.get("country_risk", 0.0), 0, 1)
    cross_border = 1.0 if txn.get("cross_border", False) else 0.0
    timing_anomaly = clamp(txn.get("timing_anomaly", 0.0), 0, 1)
    cash_advance = 1.0 if txn.get("cash_advance", False) else 0.0

    return avg([
        amount_anomaly * 0.35,
        velocity * 0.25,
        mcc_risk * 0.15,
        max(country_risk, cross_border * 0.8) * 0.15,
        timing_anomaly * 0.10,
        cash_advance * 0.10
    ]) * 100

def score_behavioral_risk(behavior: Dict[str, Any]) -> float:
    dev_7d = clamp(behavior.get("dev_7d", 0.0), 0, 1)
    dev_30d = clamp(behavior.get("dev_30d", 0.0), 0, 1)
    dev_90d = clamp(behavior.get("dev_90d", 0.0), 0, 1)
    merchant_drift = clamp(behavior.get("merchant_drift", 0.0), 0, 1)
    location_drift = clamp(behavior.get("location_drift", 0.0), 0, 1)

    return avg([
        dev_7d * 0.30,
        dev_30d * 0.35,
        dev_90d * 0.20,
        merchant_drift * 0.10,
        location_drift * 0.05
    ]) * 100

def score_account_risk(account: Dict[str, Any]) -> float:
    chargeback = clamp(account.get("chargeback_ratio", 0.0), 0, 1)
    dispute = clamp(account.get("dispute_ratio", 0.0), 0, 1)
    recent_reissue = 1.0 if account.get("recent_reissue", False) else 0.0
    fraud_flag = 1.0 if account.get("prior_fraud_flag", False) else 0.0
    account_age_risk = clamp(1.0 - account.get("account_age_months", 12) / 120, 0, 1)
    card_age_risk = clamp(1.0 - account.get("card_age_months", 12) / 120, 0, 1)

    return avg([
        chargeback * 0.30,
        dispute * 0.20,
        recent_reissue * 0.15,
        fraud_flag * 0.20,
        account_age_risk * 0.10,
        card_age_risk * 0.05
    ]) * 100

def score_device_risk(device: Dict[str, Any]) -> float:
    device_reputation = clamp(device.get("device_reputation", 0.0), 0, 1)
    new_device = 1.0 if device.get("new_device", False) else 0.0
    device_velocity = clamp(device.get("device_velocity", 0.0), 0, 1)
    ip_reputation = clamp(device.get("ip_reputation", 0.0), 0, 1)
    vpn_proxy = 1.0 if device.get("vpn_proxy", False) else 0.0

    return avg([
        device_reputation * 0.30,
        new_device * 0.25,
        device_velocity * 0.20,
        ip_reputation * 0.15,
        vpn_proxy * 0.10
    ]) * 100

def score_merchant_risk(merchant: Dict[str, Any]) -> float:
    merchant_risk = clamp(merchant.get("merchant_risk_score", 0.0), 0, 1)
    bin_risk = clamp(merchant.get("bin_risk", 0.0), 0, 1)
    known_fraud = 1.0 if merchant.get("known_fraud_list_hit", False) else 0.0
    network_velocity = clamp(merchant.get("network_velocity_risk", 0.0), 0, 1)

    return avg([
        merchant_risk * 0.40,
        bin_risk * 0.25,
        known_fraud * 0.20,
        network_velocity * 0.15
    ]) * 100

def score_auth_risk(auth: Dict[str, Any]) -> float:
    three_ds = auth.get("three_ds_result", "not_attempted")
    if three_ds == "fail":
        three_ds_risk = 1.0
    elif three_ds == "not_attempted":
        three_ds_risk = 0.7
    else:
        three_ds_risk = 0.0

    cvv_mismatch = 1.0 if auth.get("cvv_mismatch", False) else 0.0
    avs_mismatch = 1.0 if auth.get("avs_mismatch", False) else 0.0
    otp_fail = 1.0 if auth.get("otp_failed", False) else 0.0
    step_up_fail = 1.0 if auth.get("step_up_fail", False) else 0.0

    return avg([
        three_ds_risk * 0.35,
        cvv_mismatch * 0.20,
        avs_mismatch * 0.15,
        otp_fail * 0.15,
        step_up_fail * 0.15
    ]) * 100

def calculate_risk_score(txn, behavior, account, device, merchant, auth) -> Tuple[float, Dict[str, float]]:
    weights = {
        "transaction": 0.25,
        "behavioral": 0.20,
        "account": 0.20,
        "device": 0.15,
        "merchant": 0.10,
        "auth": 0.10
    }

    category_scores = {
        "transaction": score_transaction_risk(txn),
        "behavioral": score_behavioral_risk(behavior),
        "account": score_account_risk(account),
        "device": score_device_risk(device),
        "merchant": score_merchant_risk(merchant),
        "auth": score_auth_risk(auth)
    }

    weighted_score = sum(category_scores[cat] * weights[cat] for cat in weights)
    return round(min(100.0, weighted_score), 2), category_scores

def apply_hard_rules(txn, account, device, auth):
    if txn.get("cash_advance", False) and txn.get("amount", 0) > 5000:
        return "DECLINE"
    if account.get("prior_fraud_flag", False) or account.get("status") == "lost_stolen":
        return "DECLINE"
    if auth.get("otp_failed", False) and auth.get("step_up_fail", False):
        return "MANUAL_REVIEW"
    if device.get("vpn_proxy", False) and txn.get("cross_border", False):
        return "CHALLENGE_3DS"
    return None

def decide_action(score: float, hard_rule: str) -> str:
    if hard_rule:
        return hard_rule

    if score <= 24:
        return "APPROVE"
    elif score <= 49:
        return "APPROVE_WITH_MONITORING"
    elif score <= 69:
        return "CHALLENGE_3DS"
    elif score <= 84:
        return "MANUAL_REVIEW"
    else:
        return "DECLINE"
