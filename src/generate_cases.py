"""
NetSage AI - Dynamic Scenario Generator (Isolated Synthetic Data)
Generates realistic Cisco Packet Tracer failure cases and writes to data/synthetic_cases.csv
Author: Akash Verma
"""

import os
import random
import pandas as pd

FAULT_TEMPLATES = [
    {
        "concept_tag": "BGP",
        "osi_layer": "Layer 3",
        "severity": "Critical",
        "symptoms": [
            "BGP neighbor {ip1} fails to establish peering",
            "BGP session flapping between AS {as1} and AS {as2}",
            "BGP routes from AS {as1} not installed in routing table"
        ],
        "topologies": [
            "Edge Router R{r1} connecting to ISP Gateway via Gi0/{port}",
            "Border Router running eBGP with peer router at {ip1}"
        ],
        "show_outputs": [
            "BGP state = Active; neighbor {ip1} remote-as {as2}; (no route to peer IP)",
            "router bgp {as1}; neighbor {ip1} remote-as {as2}; ebgp-multihop not configured",
            "neighbor {ip1} route-map FILTER_OUT out; access-list 50 deny any"
        ],
        "expected_faults": [
            "Missing underlying Layer 3 route to BGP peer IP",
            "Missing eBGP multihop for multi-hop peering session",
            "Outbound BGP route-map ACL blocking prefix advertisement"
        ]
    },
    {
        "concept_tag": "ACL",
        "osi_layer": "Layer 4",
        "severity": "High",
        "symptoms": [
            "Client at {ip1} cannot establish SSH connection to {ip2}",
            "HTTPS traffic blocked between Branch subnet and Server {ip2}",
            "SNMP polling packets dropped between NMS and Router R{r1}"
        ],
        "topologies": [
            "Core Switch SVI with inbound ACL applied on Vlan{vlan}",
            "Border Router interface Gi0/{port} with outbound security filter"
        ],
        "show_outputs": [
            "access-list 110 deny tcp any host {ip2} eq 22; access-list 110 permit ip any any",
            "access-list 115 permit tcp any any eq 80; access-list 115 deny tcp any any eq 443",
            "access-list 120 deny udp any host {ip2} eq 161; access-list 120 permit ip any any"
        ],
        "expected_faults": [
            "Extended ACL rule explicitly denying destination port 22",
            "ACL blocking HTTPS port 443 while permitting HTTP port 80",
            "Inbound ACL blocking SNMP UDP port 161"
        ]
    },
    {
        "concept_tag": "VLAN Trunking",
        "osi_layer": "Layer 2",
        "severity": "High",
        "symptoms": [
            "Hosts in VLAN {vlan} cannot communicate across distribution switch",
            "Native VLAN mismatch CDP error logged on trunk link",
            "Dynamic Trunking Protocol (DTP) fails to form trunk on Gi0/{port}"
        ],
        "topologies": [
            "Trunk link between SW{r1} Gi0/{port} and SW{r2} Gi0/{port}",
            "Distribution switch interconnect carrying VLANs 10, 20, 30"
        ],
        "show_outputs": [
            "switchport trunk allowed vlan 10,30; (VLAN {vlan} excluded from allowed list)",
            "SW1 Gi0/{port}: native vlan 1; SW2 Gi0/{port}: native vlan {vlan}",
            "SW1: switchport mode dynamic auto; SW2: switchport mode dynamic auto"
        ],
        "expected_faults": [
            "Required VLAN omitted from switchport trunk allowed VLAN list",
            "Mismatched Native VLAN configuration across trunk link",
            "DTP mode dynamic auto on both sides preventing trunk negotiation"
        ]
    },
    {
        "concept_tag": "DHCP",
        "osi_layer": "Layer 7",
        "severity": "High",
        "symptoms": [
            "Workstations on subnet {ip1}/24 receiving APIPA 169.254.x.x addresses",
            "DHCP pool running out of leases for VLAN {vlan} clients",
            "DHCP client fails to receive default gateway parameter"
        ],
        "topologies": [
            "Central DHCP server on VLAN 50 serving remote VLAN {vlan}",
            "Router R{r1} acting as local DHCP Server for Branch LAN"
        ],
        "show_outputs": [
            "interface Gi0/0.{vlan}; (missing ip helper-address pointing to DHCP server)",
            "ip dhcp pool LAN_POOL; total 10; leased 10; zero available",
            "ip dhcp pool POOL_{vlan}; network 192.168.{vlan}.0; (missing default-router command)"
        ],
        "expected_faults": [
            "Missing IP Helper-Address relay configuration on sub-interface",
            "DHCP Scope address pool exhaustion",
            "DHCP scope missing default-router option parameter"
        ]
    }
]

def get_synthetic_csv_path() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    folder = "Data" if os.path.exists(os.path.join(base_dir, "Data")) else "data"
    return os.path.join(base_dir, folder, "synthetic_cases.csv")

def generate_synthetic_case(case_num: int) -> dict:
    template = random.choice(FAULT_TEMPLATES)
    
    r1, r2 = random.randint(1, 4), random.randint(5, 8)
    port = random.randint(1, 4)
    vlan = random.choice([20, 40, 50, 80, 100])
    as1, as2 = random.randint(65001, 65050), random.randint(65100, 65200)
    ip1 = f"192.168.{random.randint(10, 90)}.10"
    ip2 = f"10.0.{random.randint(1, 20)}.50"

    symptom = random.choice(template["symptoms"]).format(r1=r1, r2=r2, port=port, vlan=vlan, ip1=ip1, ip2=ip2, as1=as1, as2=as2)
    topology = random.choice(template["topologies"]).format(r1=r1, r2=r2, port=port, vlan=vlan, ip1=ip1, ip2=ip2, as1=as1, as2=as2)
    show_output = random.choice(template["show_outputs"]).format(r1=r1, r2=r2, port=port, vlan=vlan, ip1=ip1, ip2=ip2, as1=as1, as2=as2)
    expected_fault = random.choice(template["expected_faults"])

    return {
        "case_id": f"SYN-{case_num:03d}",
        "symptom": symptom,
        "topology_note": topology,
        "show_outputs": show_output,
        "expected_fault": expected_fault,
        "osi_layer": template["osi_layer"],
        "concept_tag": template["concept_tag"],
        "severity": template["severity"]
    }

def add_synthetic_cases(count: int = 5):
    csv_path = get_synthetic_csv_path()
    
    if os.path.exists(csv_path):
        df_synth = pd.read_csv(csv_path)
    else:
        df_synth = pd.DataFrame(columns=[
            "case_id", "symptom", "topology_note", "show_outputs",
            "expected_fault", "osi_layer", "concept_tag", "severity"
        ])
    
    current_count = len(df_synth)
    new_records = [generate_synthetic_case(current_count + i) for i in range(1, count + 1)]
    
    df_updated = pd.concat([df_synth, pd.DataFrame(new_records)], ignore_index=True)
    df_updated.to_csv(csv_path, index=False)
    print(f"Added {count} synthetic cases to: {csv_path} (Total synthetic: {len(df_updated)})")
    return df_updated

if __name__ == "__main__":
    import sys
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    add_synthetic_cases(num)