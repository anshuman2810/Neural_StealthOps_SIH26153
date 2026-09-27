from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "dataset"
ARTIFACTS_DIR = BASE_DIR / "artifacts_v2"
LEGACY_ARTIFACTS_DIR = BASE_DIR / "artifacts"
DEMO_DATA_DIR = BASE_DIR / "demo_data"

# Time window & modeling constants
WINDOW_SECONDS = 10
SEQ_LEN = 12
HORIZONS = (1, 3, 6)  # Corresponding to +10s, +30s, +60s
CHUNK_SIZE = 100_000

# Raw CIC-IDS2018 columns required
RAW_COLUMNS = [
    'Timestamp', 'Dst Port', 'Protocol', 'Flow Duration', 'Tot Fwd Pkts', 'Tot Bwd Pkts',
    'TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Flow Byts/s', 'Flow Pkts/s', 'Flow IAT Mean',
    'Flow IAT Std', 'Pkt Len Mean', 'Pkt Len Std', 'SYN Flag Cnt', 'ACK Flag Cnt',
    'RST Flag Cnt', 'FIN Flag Cnt', 'PSH Flag Cnt', 'Active Mean', 'Idle Mean', 'Label'
]

# Numeric source metrics to compute 10s mean values
MEAN_SOURCE = [
    'Flow Duration', 'Flow Byts/s', 'Flow Pkts/s', 'Flow IAT Mean', 'Flow IAT Std',
    'Pkt Len Mean', 'Pkt Len Std', 'SYN Flag Cnt', 'ACK Flag Cnt', 'RST Flag Cnt',
    'FIN Flag Cnt', 'PSH Flag Cnt', 'Active Mean', 'Idle Mean'
]

# Heavy-tailed volumetric metrics log-transformed via log1p
SKEWED = ['flow_count', 'total_packets', 'total_bytes', 'attack_flow_count', 'unique_dst_ports']

# Model input features matching artifacts_v2/attention_world_model.pt (21 features)
FEATURES = [
    'port_entropy', 'protocol_diversity',
    'mean_Flow Duration', 'mean_Flow Byts/s', 'mean_Flow Pkts/s', 'mean_Flow IAT Mean', 'mean_Flow IAT Std',
    'mean_Pkt Len Mean', 'mean_Pkt Len Std',
    'mean_SYN Flag Cnt', 'mean_ACK Flag Cnt', 'mean_RST Flag Cnt', 'mean_FIN Flag Cnt', 'mean_PSH Flag Cnt',
    'mean_Active Mean', 'mean_Idle Mean',
    'log_flow_count', 'log_total_packets', 'log_total_bytes', 'log_attack_flow_count', 'log_unique_dst_ports'
]

# MITRE ATT&CK Stage Alignment
STAGES = [
    'Normal',
    'Initial Access',
    'Credential Access',
    'Lateral Movement',
    'Command and Control',
    'Impact',
    'Other Malicious'
]

STAGE_TO_ID = {s: i for i, s in enumerate(STAGES)}
ID_TO_STAGE = {i: s for i, s in enumerate(STAGES)}

# Mapping dataset attack families to coarse MITRE stages
def mitre_stage_from_label(label: str) -> str:
    x = str(label).lower()
    if x in ('benign', 'label'):
        return 'Normal'
    if 'ftp' in x or 'ssh' in x:
        return 'Credential Access'
    if 'brute force' in x or 'xss' in x or 'sql' in x:
        return 'Initial Access'
    if 'dos' in x or 'ddos' in x:
        return 'Impact'
    if 'bot' in x:
        return 'Command and Control'
    if 'infilt' in x:
        return 'Lateral Movement'
    return 'Other Malicious'

# Stage severity levels for SOC alert priority
STAGE_SEVERITY = {
    'Normal': 'INFO',
    'Initial Access': 'MEDIUM',
    'Credential Access': 'HIGH',
    'Lateral Movement': 'CRITICAL',
    'Command and Control': 'CRITICAL',
    'Impact': 'CRITICAL',
    'Other Malicious': 'HIGH'
}

# Automated SOC Recommended Playbooks
STAGE_PLAYBOOKS = {
    'Normal': 'Traffic profile conforms to baseline. Normal passive monitoring.',
    'Initial Access': 'Alert: Web exploit / Brute Force attempt detected. Inspect WAF logs and throttle suspect remote IP addresses.',
    'Credential Access': 'Alert: Authentication brute-force surge (SSH/FTP). Enforce MFA, reset session tokens, and lock affected accounts.',
    'Lateral Movement': 'High Alert: Internal network pivoting / infiltration pattern. Isolate affected VLAN segment and audit internal RPC/SMB flows.',
    'Command and Control': 'Critical Alert: Botnet beaconing / periodic heartbeat detected. Block C2 IP/domain at perimeter firewall and capture PCAP.',
    'Impact': 'Emergency Alert: High-velocity Denial of Service / Resource Exhaustion. Engage scrubbing centers and apply volumetric rate-limiting.',
    'Other Malicious': 'Alert: Anomaly detected outside standard baseline. Escalate to Tier-2 SOC Analyst for packet inspection.'
}
