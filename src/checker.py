"""
NetSage AI - Deterministic Rule Checker Engine
Author: Akash Verma
Module: src/checker.py
"""

import re
from typing import Dict, Any, List


class NetworkRuleChecker:
    """
    Deterministic rule engine that validates captured Cisco IOS CLI outputs
    using pattern matching and regex heuristics.
    """

    def __init__(self):
        self.rules = [
            {
                "id": "RULE_ADMIN_DOWN",
                "pattern": r"is\s+administratively\s+down",
                "finding": "Interface is in an administratively shutdown state.",
                "fix": [
                    "configure terminal",
                    "interface GigabitEthernet0/0.10",
                    "no shutdown",
                    "end",
                    "write memory"
                ]
            },
            {
                "id": "RULE_NAT_MISSING_OVERLOAD",
                "pattern": r"ip\s+nat\s+inside\s+source\s+list\s+\d+\s+interface\s+\S+(?!\s+overload)",
                "finding": "Dynamic NAT configuration is missing the 'overload' keyword (PAT).",
                "fix": [
                    "configure terminal",
                    "no ip nat inside source list 1 interface Gi0/0",
                    "ip nat inside source list 1 interface Gi0/0 overload",
                    "end"
                ]
            },
            {
                "id": "RULE_MISSING_ENCAPSULATION",
                "pattern": r"encapsulation\s+dot1Q\s+missing",
                "finding": "Router sub-interface is missing IEEE 802.1Q VLAN encapsulation tag.",
                "fix": [
                    "configure terminal",
                    "interface GigabitEthernet0/0.20",
                    "encapsulation dot1Q 20",
                    "ip address 192.168.20.1 255.255.255.0",
                    "end"
                ]
            },
            {
                "id": "RULE_ERR_DISABLED",
                "pattern": r"err-disabled",
                "finding": "Port security violation triggered an err-disabled state.",
                "fix": [
                    "configure terminal",
                    "interface Fa0/3",
                    "shutdown",
                    "no shutdown",
                    "end"
                ]
            },
            {
                "id": "RULE_CDP_DISABLED",
                "pattern": r"CDP\s+is\s+not\s+enabled",
                "finding": "Cisco Discovery Protocol (CDP) is disabled globally on the device.",
                "fix": [
                    "configure terminal",
                    "cdp run",
                    "end"
                ]
            },
            {
                "id": "RULE_DHCP_EXHAUSTION",
                "pattern": r"leased\s+(\d+);\s+zero\s+available",
                "finding": "DHCP address pool scope is completely exhausted.",
                "fix": [
                    "configure terminal",
                    "ip dhcp pool LAN_POOL",
                    "network 192.168.1.0 255.255.255.0",
                    "end"
                ]
            }
        ]

    def evaluate(self, show_output: str, topology_note: str = "") -> Dict[str, Any]:
        """
        Scans CLI outputs and topology notes against the deterministic rules.
        """
        combined_text = f"{show_output} {topology_note}"
        findings: List[str] = []
        suggested_fixes: List[str] = []

        for rule in self.rules:
            if re.search(rule["pattern"], combined_text, re.IGNORECASE):
                findings.append(rule["finding"])
                suggested_fixes.extend(rule["fix"])

        if findings:
            return {
                "flagged": True,
                "status": "Deterministic Rule Triggered",
                "findings": findings,
                "suggested_fix": suggested_fixes
            }

        return {
            "flagged": False,
            "status": "Deterministic Pass (No hard syntax errors detected)",
            "findings": ["No static regex violations detected. Telemetry passed to AI Semantic Engine."],
            "suggested_fix": []
        }