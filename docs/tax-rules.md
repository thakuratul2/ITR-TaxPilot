# Assessment Year Rules & Deterministic Engine

## 1. Statutory Rule Versioning
Tax calculation rules in India evolve with each Union Budget / Finance Act. In ITR-TaxPilot:
- Every Assessment Year (AY) has a dedicated isolated rule directory under `backend/app/tax/rules/ay_YYYY_YY/`.
- Slabs, Section 87A rebate thresholds, Standard Deduction limits, Surcharge rates, and Cess (4%) are strictly codified as immutable parameters with statutory citations.

## 2. Rule Structure
```text
backend/app/tax/rules/
├── common/
│   ├── base_rule.py
│   └── constants.py
├── ay_2025_26/
│   ├── old_regime.py
│   └── new_regime.py
└── ay_2026_27/
    ├── old_regime.py
    └── new_regime.py
```

## 3. Data Integrity
- Distinguish numeric `0` from `None` / `unknown`.
- Never invent deductions or salary components.
