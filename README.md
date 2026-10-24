# Card Monitoring & Risk Framework

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

A modular, rule-based risk scoring and transaction monitoring framework designed to evaluate payment card transactions in real-time, flag anomalies, and automate fraud decisions (`APPROVE`, `REVIEW`, `DECLINE`).

---

## 🚀 Key Features

* **Multi-Factor Risk Scoring:** Combines deterministic threshold rules (transaction amounts, velocity limits) with probabilistic risk weights.
* **Automated Decision Pipeline:** Routes transactions into clear operational queues (`APPROVE` for low risk, `REVIEW` for manual investigation, `DECLINE` for high risk).
* **Extensible Rule Engine:** Easily plug in custom fraud rules, geolocation blacklists, or machine learning risk models.
* **Testing Suite:** Fully tested using `pytest` to ensure robust handling of edge cases.

---

## 📁 Repository Architecture

```text
card-monitoring-risk-framework/
├── data/                    # Sample transactional datasets for testing & simulation
├── notebooks/               # Jupyter notebooks for exploratory data analysis & risk distributions
├── src/                     # Core source package
│   ├── __init__.py
│   └── risk_engine.py       # Main risk evaluation and scoring logic
├── tests/                   # Automated unit tests
│   └── test_risk_engine.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
