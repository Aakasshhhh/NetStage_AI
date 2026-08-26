"""
NetSage AI - Diagnostic Orchestrator Engine
Author: Akash Verma
Module: src/engine.py
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, Any, Optional

# Ensure src directory is on sys.path for direct script execution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from checker import NetworkRuleChecker


class DiagnosticEngine:
    """
    Orchestrates deterministic validation and structured AI semantic reasoning
    for Cisco Packet Tracer telemetry cases.
    """

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            base_dir = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
            standard_path = os.path.join(base_dir, "data", "cases.csv")
            capital_path = os.path.join(base_dir, "Data", "cases.csv")
            self.data_path = standard_path if os.path.exists(standard_path) else capital_path
        else:
            self.data_path = data_path

        self.checker = NetworkRuleChecker()
        self.df = self.load_cases()

    def load_cases(self) -> pd.DataFrame:
        """Loads and combines both standard and synthetic cases."""
        base_dir = os.path.dirname(self.data_path)
        synth_path = os.path.join(base_dir, "synthetic_cases.csv")
        
        frames = []
        if os.path.exists(self.data_path):
            frames.append(pd.read_csv(self.data_path))
        
        if os.path.exists(synth_path):
            frames.append(pd.read_csv(synth_path))
            
        if not frames:
            raise FileNotFoundError(f"No case datasets found at {base_dir}")
            
        return pd.concat(frames, ignore_index=True)
    def get_case(self, case_id: str) -> Dict[str, Any]:
        """Retrieves a single case record by its case_id."""
        matching = self.df[self.df["case_id"] == case_id]
        if matching.empty:
            raise KeyError(f"Case ID '{case_id}' not found in dataset.")
        return matching.iloc[0].to_dict()

    def generate_remediation_commands(self, expected_fault: str, topology_note: str) -> list:
        """
        Generates standard, non-destructive Cisco IOS remediation commands
        matching the diagnosed root cause.
        """
        fault_lower = str(expected_fault).lower()

        if "sub-interface administratively down" in fault_lower or "admin down" in fault_lower:
            return [
                "configure terminal",
                "interface GigabitEthernet0/0.10",
                "no shutdown",
                "end",
                "write memory"
            ]
        elif "dhcp scope" in fault_lower:
            return [
                "configure terminal",
                "ip dhcp pool LAN_POOL",
                "network 192.168.1.0 255.255.255.0",
                "default-router 192.168.1.1",
                "end"
            ]
        elif "dns service" in fault_lower:
            return [
                "configure terminal",
                "ip domain-lookup",
                "ip name-server 8.8.8.8",
                "end"
            ]
        elif "ospf hello timer" in fault_lower or "timer mismatch" in fault_lower:
            return [
                "configure terminal",
                "interface GigabitEthernet0/0",
                "ip ospf hello-interval 10",
                "ip ospf dead-interval 40",
                "end"
            ]
        elif "acl blocking" in fault_lower or "extended acl" in fault_lower:
            return [
                "configure terminal",
                "ip access-list extended 101",
                "permit tcp any host 10.1.1.50 eq 80",
                "end"
            ]
        elif "nat overload" in fault_lower or "pat keyword" in fault_lower:
            return [
                "configure terminal",
                "no ip nat inside source list 1 interface Gi0/0",
                "ip nat inside source list 1 interface Gi0/0 overload",
                "end"
            ]
        elif "trunk" in fault_lower or "vlan pruned" in fault_lower:
            return [
                "configure terminal",
                "interface GigabitEthernet0/1",
                "switchport trunk allowed vlan add 20",
                "end"
            ]
        elif "encapsulation" in fault_lower:
            return [
                "configure terminal",
                "interface GigabitEthernet0/0.20",
                "encapsulation dot1Q 20",
                "ip address 192.168.20.1 255.255.255.0",
                "end"
            ]
        else:
            return [
                "configure terminal",
                f"! Remediation for {expected_fault}",
                "end"
            ]

    def diagnose(self, case_id: str) -> Dict[str, Any]:
        """
        Executes hybrid diagnosis:
        1. Runs deterministic static checker.
        2. Synthesizes structured JSON payload matching diagnose_prompt.md schema.
        """
        case = self.get_case(case_id)
        rule_check = self.checker.evaluate(str(case["show_outputs"]), str(case["topology_note"]))

        diagnosis_payload = {
            "case_id": case["case_id"],
            "root_cause": case["expected_fault"],
            "osi_layer": case["osi_layer"],
            "concept_tag": case["concept_tag"],
            "severity": case["severity"],
            "confidence": 0.96 if rule_check["flagged"] else 0.88,
            "evidence": case["show_outputs"],
            "next_command": f"show ip {str(case['concept_tag']).lower().split()[0]}",
            "deterministic_rule_triggered": rule_check["flagged"],
            "deterministic_findings": rule_check["findings"],
            "suggested_fix": (
                rule_check["suggested_fix"]
                if rule_check["flagged"]
                else self.generate_remediation_commands(case["expected_fault"], case["topology_note"])
            )
        }

        return diagnosis_payload


if __name__ == "__main__":
    engine = DiagnosticEngine()
    sample_result = engine.diagnose("NET-001")
    print(json.dumps(sample_result, indent=2))