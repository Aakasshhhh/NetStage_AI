# NetSage AI - Responsible AI Governance & Model Audit Log

This document records system performance metrics and 5 specific edge cases where the AI diagnosis or remediation plan required human operator correction before deployment.

---

## 1. System Performance Summary

- **Total Evaluated Scenarios:** 30 Cases
- **Deterministic Rule Catch Rate:** 63.3% (19/30 cases flagged by regex rule checks)[cite: 2]
- **AI Semantic Diagnosis Agreement Rate:** 76.6% (23/30 initial correct diagnoses)[cite: 2]
- **Human-in-the-Loop Intervention Rate:** 23.4% (7 cases requiring review, modification, or rejection)[cite: 2]

---

## 2. Documented Human Override Cases (Responsible AI)

### Case 1: NET-005 (Extended ACL Web Traffic Block)

- **Symptom:** Branch users cannot access HTTP web server at 10.1.1.50.
- **Raw AI Proposal:** Recommended inserting a global `permit ip any any` above the deny rule.
- **Human Operator Finding:** A broad `permit ip any any` violates the principle of least privilege and introduces security vulnerabilities.
- **Operator Correction:** Modified the rule to strictly permit destination port 80:
  ```ios
  ip access-list extended 101
  permit tcp any host 10.1.1.50 eq 80
  ```
