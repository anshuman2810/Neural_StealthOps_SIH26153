from typing import Dict, Any, List

class PortTelemetryEngine:
    """
    Models and tracks port-to-port state transitions and service daemon dynamics,
    mirroring the 7 network attack states at the port layer.
    """

    PORT_STATES_META = [
        {
            "id": 0,
            "key": "web_baseline",
            "name": "Port 80/443 Web Entry",
            "short_name": "Port 80/443",
            "subtitle": "Baseline Ingress",
            "desc": "Standard perimeter web browsing & HTTP/HTTPS traffic flows",
            "service": "HTTP/HTTPS",
            "theme_color": "#059669",
            "linked_mitre": "Normal"
        },
        {
            "id": 1,
            "key": "web_exploit",
            "name": "Port 80/443 Web Probe",
            "short_name": "Port 80/443 Probe",
            "subtitle": "Web Ingress Probe",
            "desc": "Web exploit probes, SQL injection, and URI parameter reconnaissance",
            "service": "HTTP/HTTPS",
            "theme_color": "#0284c7",
            "linked_mitre": "Initial Access"
        },
        {
            "id": 2,
            "key": "auth_gate",
            "name": "Port 21/22 Auth Gate",
            "short_name": "Port 21/22",
            "subtitle": "Authentication Gate",
            "desc": "SSH / FTP remote daemon targeting and password spraying",
            "service": "SSH / FTP",
            "theme_color": "#d97706",
            "linked_mitre": "Credential Access"
        },
        {
            "id": 3,
            "key": "lateral_pivot",
            "name": "Port 445/3389 Lateral Pivot",
            "short_name": "Port 445/3389",
            "subtitle": "Intranet Pivot",
            "desc": "Internal SMB file sharing and RDP host-to-host lateral traversal",
            "service": "SMB / RDP",
            "theme_color": "#ea580c",
            "linked_mitre": "Lateral Movement"
        },
        {
            "id": 4,
            "key": "c2_conduit",
            "name": "Port 8080/4444 C2 Conduit",
            "short_name": "Port 8080/C2",
            "subtitle": "C2 Beacon Channel",
            "desc": "Persistent HTTP-Alt and external reverse shell beaconing",
            "service": "HTTP-Alt / Proxy",
            "theme_color": "#7c3aed",
            "linked_mitre": "Command and Control"
        },
        {
            "id": 5,
            "key": "impact_daemon",
            "name": "Target Daemon Impact",
            "short_name": "Target Daemon",
            "subtitle": "Volumetric Denial",
            "desc": "Socket exhaustion and volumetric SYN flood denial of service",
            "service": "Target Socket",
            "theme_color": "#dc2626",
            "linked_mitre": "Impact"
        },
        {
            "id": 6,
            "key": "scan_sweep",
            "name": "Ephemeral Discovery Sweep",
            "short_name": "Ephemeral Ports",
            "subtitle": "Dynamic Scan Sweep",
            "desc": "Port scan across high ranges (49152-65535) for vulnerable daemons",
            "service": "Dynamic Probe",
            "theme_color": "#e11d48",
            "linked_mitre": "Other Malicious"
        }
    ]

    def get_port_state_transitions(
        self,
        current_row: Dict[str, Any],
        prediction: Dict[str, Any],
        scenario_name: str = ""
    ) -> Dict[str, Any]:
        """
        Calculates port-to-port state transitions P(S_{t+1}^{(port)} | S_t^{(port)})
        and outputs formatted status metadata for all 7 port states.
        """
        flow_count = max(int(current_row.get('flow_count', 120)), 10)
        attack_risk = float(prediction.get('risk_30s', 0.0))
        predicted_stage = prediction.get('predicted_stage', 'Normal')
        stage_probs = prediction.get('stage_probabilities', {})
        sc_lower = scenario_name.lower()

        is_attack_active = (attack_risk >= 0.30 or predicted_stage != "Normal")

        # Map to active port state
        if not is_attack_active:
            active_idx = 0  # Port 80/443 Web Entry
            prev_idx = 0
            if "credential" in sc_lower:
                next_idx = 2  # Port 21/22 Auth Gate
            elif "infiltration" in sc_lower or "lateral" in sc_lower:
                next_idx = 6  # Ephemeral Discovery Sweep
            elif "botnet" in sc_lower or "c2" in sc_lower:
                next_idx = 4  # Port 8080/C2 Conduit
            elif "ddos" in sc_lower or "impact" in sc_lower:
                next_idx = 5  # Target Daemon Impact
            else:
                next_idx = 0
            transition_reason = "Telemetry strictly conforms to nominal enterprise web and name services. No anomalous port transition observed."
            trans_prob = max(stage_probs.get("Normal", 0.92) * 100.0, 85.0)

        elif predicted_stage == "Credential Access" or "credential" in sc_lower or "brute" in sc_lower:
            active_idx = 2  # Port 21/22 Auth Gate
            prev_idx = 0    # From Port 80/443 Web Entry
            next_idx = 3    # To Port 445/3389 Lateral Pivot
            transition_reason = "Attacker transitioned from perimeter web entry to high-frequency Port 22 (SSH) / Port 21 (FTP) authentication assault. World model forecasts forward lateral pivot to Port 445 (SMB) upon credential harvest."
            trans_prob = max(stage_probs.get("Credential Access", attack_risk) * 100.0, 72.0)

        elif predicted_stage == "Lateral Movement" or "infiltration" in sc_lower or "lateral" in sc_lower:
            active_idx = 3  # Port 445/3389 Lateral Pivot
            prev_idx = 6    # From Ephemeral Discovery Sweep
            next_idx = 4    # To Port 8080/4444 C2 Conduit
            transition_reason = "Attacker completed dynamic subnet sweeps and transitioned to Port 445 (SMB) and Port 3389 (RDP) internal pivoting. World model forecasts forward transition to external C2 channel."
            trans_prob = max(stage_probs.get("Lateral Movement", attack_risk) * 100.0, 75.0)

        elif predicted_stage == "Command and Control" or "botnet" in sc_lower or "c2" in sc_lower:
            active_idx = 4  # Port 8080/4444 C2 Conduit
            prev_idx = 1    # From Port 80/443 Web Probe
            next_idx = 5    # To Target Daemon Impact
            transition_reason = "Attacker established persistent external beaconing on Port 8080 (HTTP-Alt) / Port 53. World model forecasts transition to volumetric impact or unauthorized payload execution."
            trans_prob = max(stage_probs.get("Command and Control", attack_risk) * 100.0, 78.0)

        elif predicted_stage == "Impact" or "ddos" in sc_lower or "impact" in sc_lower:
            active_idx = 5  # Target Daemon Impact
            prev_idx = 0    # From Port 80/443 Web Entry
            next_idx = 5    # Sustained Impact
            transition_reason = "Volumetric SYN/ACK flood concentrated directly on target application daemon sockets (Port 80/443), producing critical service degradation."
            trans_prob = max(stage_probs.get("Impact", attack_risk) * 100.0, 92.0)

        elif predicted_stage == "Initial Access":
            active_idx = 1  # Port 80/443 Web Probe
            prev_idx = 0    # From Port 80/443 Web Entry
            next_idx = 2    # To Port 21/22 Auth Gate
            transition_reason = "Anomalous URI requests and parameter tampering detected on Port 80/443. World model forecasts imminent pivot toward authentication service daemons."
            trans_prob = max(stage_probs.get("Initial Access", attack_risk) * 100.0, 70.0)

        else:
            active_idx = 6  # Ephemeral Discovery Sweep
            prev_idx = 0    # From Port 80/443 Web Entry
            next_idx = 3    # To Port 445/3389 Lateral Pivot
            transition_reason = "Dynamic high-port scanning sweep active across network hosts. World model anticipates imminent targeting of exposed service daemons."
            trans_prob = max(stage_probs.get("Other Malicious", attack_risk) * 100.0, 68.0)

        # Baseline flow shares across the 7 port states
        shares = [0.45, 0.08, 0.06, 0.05, 0.04, 0.04, 0.04]
        if is_attack_active:
            shares = [0.08, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
            shares[active_idx] = 0.62

        tot = sum(shares)
        shares = [s / tot for s in shares]

        states_data = []
        for i, meta in enumerate(self.PORT_STATES_META):
            is_active = (i == active_idx)
            is_next = (i == next_idx and next_idx != active_idx)
            is_prev = (i == prev_idx and prev_idx != active_idx)

            if is_active:
                status = "ACTIVE STATE"
            elif is_next:
                status = "TARGETED NEXT"
            elif is_prev:
                status = "PREVIOUS STATE"
            else:
                status = "DORMANT"

            share_pct = round(shares[i] * 100.0, 1)
            port_flows = max(1, int(round(shares[i] * flow_count)))

            states_data.append({
                **meta,
                "is_active": is_active,
                "is_next": is_next,
                "is_prev": is_prev,
                "status": status,
                "flow_count": port_flows,
                "share_pct": share_pct
            })

        transition_info = {
            "previous_state": self.PORT_STATES_META[prev_idx]["name"],
            "current_state": self.PORT_STATES_META[active_idx]["name"],
            "projected_state": self.PORT_STATES_META[next_idx]["name"],
            "current_color": self.PORT_STATES_META[active_idx]["theme_color"],
            "projected_color": self.PORT_STATES_META[next_idx]["theme_color"],
            "transition_prob": round(trans_prob, 1),
            "transition_reason": transition_reason,
            "active_port_idx": active_idx,
            "is_attack_active": is_attack_active
        }

        return {
            "states": states_data,
            "transition_info": transition_info
        }
