from pathlib import Path
import time
import streamlit as st
import pandas as pd
import numpy as np

def init_system_state():
    """Initializes the infrastructure node state, telemetry, and alerts if not present."""
    if "system_nodes" not in st.session_state:
        st.session_state.system_nodes = {
            "lakehouse_iceberg": {
                "id": "lakehouse_iceberg",
                "name": "Apache Iceberg Catalog",
                "category": "Data Lakehouse",
                "ip": "10.0.15.2",
                "port": 8181,
                "status": "Running",
                "health": "OK",
                "storage_used_gb": 512,
                "storage_total_gb": 12288,  # 12 TB
                "endpoint": "/Status"
            },
            "lakehouse_ceph": {
                "id": "lakehouse_ceph",
                "name": "Ceph Object Storage Engine",
                "category": "Data Lakehouse",
                "ip": "10.0.15.3",
                "port": 7480,
                "status": "Running",
                "health": "OK",
                "storage_used_gb": 1024,
                "storage_total_gb": 49152,  # 48 TB
                "endpoint": "/Status"
            },
            "compute_node_1": {
                "id": "compute_node_1",
                "name": "Compute Node 1 (Filter/Extract)",
                "category": "Packet Processing Pipeline",
                "ip": "10.0.15.5",
                "port": 9092,
                "status": "Running",
                "health": "OK",
                "cpu_pct": 35.0,
                "mem_used_gb": 24.0,
                "mem_total_gb": 32.0,
                "endpoint": ""
            },
            "compute_node_2": {
                "id": "compute_node_2",
                "name": "Compute Node 2 (Filter/Extract)",
                "category": "Packet Processing Pipeline",
                "ip": "10.0.15.6",
                "port": 9092,
                "status": "Running",
                "health": "OK",
                "cpu_pct": 45.0,
                "mem_used_gb": 28.0,
                "mem_total_gb": 32.0,
                "endpoint": ""
            },
            "redis_server": {
                "id": "redis_server",
                "name": "Redis Memory Shared Cache",
                "category": "Redis Server",
                "ip": "10.0.15.15",
                "port": 6379,
                "status": "Running",
                "health": "OK",
                "mem_used_gb": 20.0,
                "mem_total_gb": 64.0,
                "endpoint": "/config"
            },
            "threat_engine": {
                "id": "threat_engine",
                "name": "Threat Detection & Prediction Engine",
                "category": "Threat Detection & Prediction Engine",
                "ip": "10.0.15.10",
                "port": 8501,
                "status": "Running",
                "health": "OK",
                "cpu_pct": 35.0,
                "mem_used_gb": 24.0,
                "mem_total_gb": 32.0,
                "endpoint": "/config"
            }
        }

    if "system_alerts" not in st.session_state:
        st.session_state.system_alerts = [
            {
                "id": "ALT-1092",
                "timestamp": "21:32:15",
                "severity": "WARNING",
                "component": "Compute Node 2",
                "message": "Memory utilization exceeded 85% threshold (28GB/32GB allocated). Automatic GC sweep invoked.",
                "status": "Active"
            },
            {
                "id": "ALT-1091",
                "timestamp": "21:28:40",
                "severity": "INFO",
                "component": "Data Lakehouse",
                "message": "Apache Iceberg snapshot compaction committed successfully. 1,420 parquet manifests merged.",
                "status": "Active"
            },
            {
                "id": "ALT-1090",
                "timestamp": "21:24:12",
                "severity": "INFO",
                "component": "Redis Server",
                "message": "Telemetry cache eviction policy set to volatile-lru. 4.2M flow keys active across cluster.",
                "status": "Active"
            },
            {
                "id": "ALT-1089",
                "timestamp": "21:18:05",
                "severity": "CRITICAL",
                "component": "Threat Detection Engine",
                "message": "Infiltration hazard score spike: 0.942 on Port 445 (SMB lateral movement pattern detected).",
                "status": "Active"
            },
            {
                "id": "ALT-1088",
                "timestamp": "21:10:30",
                "severity": "INFO",
                "component": "Packet Processing Pipeline",
                "message": "Compute Node 1 flow extraction throughput peaked at 134,000 pkts/s (nominal latency).",
                "status": "Active"
            }
        ]

    if "active_console_modal" not in st.session_state:
        st.session_state.active_console_modal = None


def render_blinking_indicator(is_ok: bool, text: str = "OK"):
    """Returns HTML for animated pulsing dot indicator."""
    dot_class = "blink-dot-green" if is_ok else "blink-dot-red"
    color = "#16a34a" if is_ok else "#dc2626"
    return f"""<span class="{dot_class}"></span><span style="font-weight:700; color:{color}; font-size:0.95rem;">{text}</span>"""


def render_simulated_console_modal():
    """Renders the in-dashboard interactive simulated admin console modal for the active target."""
    modal_target = st.session_state.active_console_modal
    if not modal_target:
        return

    node = st.session_state.system_nodes.get(modal_target)
    if not node:
        return

    target_url = f"http://{node['ip']}{node['endpoint']}"

    st.markdown(
        f"""
        <div style="background: #0f172a; border: 2px solid #38bdf8; border-radius: 10px; padding: 22px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); color: #f8fafc;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
                <div>
                    <span style="background: #0284c7; color: white; padding: 3px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Simulated Admin Console</span>
                    <h3 style="color: #f8fafc !important; margin: 6px 0 0 0; font-size: 1.25rem;">🖥️ {node['name']} — <code>{target_url}</code></h3>
                </div>
                <div>
                    <span style="color: #10b981; font-weight: 700; font-size: 0.9rem;">● CONNECTED (HTTP 200 OK)</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown(f"**Target Host Endpoint:** `{target_url}` | **Node Status:** `{node['status']}`")

        # Mock console output based on component
        if "lakehouse" in modal_target:
            st.code(
                f"""[HTTP/1.1 200 OK]
Server: Apache Iceberg REST Catalog v1.4.2 / Ceph RGW S3
Host: {node['ip']}:{node['port']}
Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}

{'{'}
  "catalog_name": "neural_stealthops_telemetry_lake",
  "storage_backend": "ceph-rgw-s3",
  "endpoint": "http://{node['ip']}:{node['port']}/v1",
  "tables": [
    "network_telemetry.discrete_10s_states",
    "threat_detection.mitre_attack_logs",
    "threat_detection.world_model_checkpoints"
  ],
  "cluster_status": "{'HEALTH_OK' if node['status'] == 'Running' else 'STOPPED'}",
  "active_snapshots": 1420,
  "committed_bytes": 549755813888,
  "total_capacity_bytes": 13194139533312
{'}'}""",
                language="json"
            )
        elif "compute" in modal_target:
            st.code(
                f"""[Compute Node Diagnostics Console]
Node ID: {node['id']} ({node['name']})
Interface IP: {node['ip']} | Listening Port: {node['port']}
Operating State: {node['status']}

[Worker Processes]
├── thread-0: packet_capture_stream (libpcap AF_PACKET ring buffer: OK)
├── thread-1: flow_dissector (TCP/UDP/ICMP parser: OK)
├── thread-2: 21_feature_extractor (10s sliding window builder: OK)
└── thread-3: redis_telemetry_publisher (Socket connected to 10.0.15.15:6379)

[Pipeline Performance Metrics]
- Ingestion Packet Rate: {'128,450 pkts/sec' if node['status'] == 'Running' else '0 pkts/sec'}
- Flow Record Generation: {'2,180 flows/sec' if node['status'] == 'Running' else '0 flows/sec'}
- Buffer Drops: 0 packets (0.000%)
- Hardware Acceleration: DPDK / AVX-512 enabled""",
                language="text"
            )
        elif "redis" in modal_target:
            st.code(
                f"""# Redis Configuration & Telemetry Status
# Redis Version: 7.2.4 Enterprise High-Speed Cache
# Endpoint: {node['ip']}:{node['port']}

# Server
redis_version:7.2.4
os:Linux 6.1.0-amd64
uptime_in_seconds:384210
status:{'RUNNING' if node['status'] == 'Running' else 'STOPPED'}

# Memory
used_memory:21474836480
used_memory_human:20.00G
maxmemory:68719476736
maxmemory_human:64.00G
maxmemory_policy:volatile-lru
mem_fragmentation_ratio:1.04

# Keyspace
db0:keys=4290120,expires=4290120,avg_ttl=60000 (10s window discrete state queue)""",
                language="properties"
            )
        else:  # threat_engine
            st.code(
                f"""[Neural StealthOps AI Threat Detection Engine Runtime]
Host: {node['ip']}:{node['port']}
Inference Engine: PyTorch AttentionWorldModel (Multi-Task)
Service Status: {node['status']}

[Model Configuration]
- Context Window (SEQ_LEN): 6 steps (60.0s telemetry history)
- Latent Hidden Dim: 64
- Forecasting Heads:
    ├── next_state_head: Dim 21 (L2 regression)
    ├── threat_hazard_heads: +10s (BCELoss), +30s (BCELoss), +60s (BCELoss)
    ├── attack_volume_head: Log1p MSELoss
    └── mitre_progression_head: 7 Classes Softmax (CrossEntropyLoss)
- Hardware Profiling: Host CPU (Single Core: 0.19ms / Multi-task Forward: 0.56ms)
- Connected Redis Ingestion Queue: 10.0.15.15:6379""",
                language="text"
            )

        col_close, col_dummy = st.columns([1, 4])
        with col_close:
            if st.button("Close Console Screen ✕", key="btn_close_modal", use_container_width=True):
                st.session_state.active_console_modal = None
                st.rerun()

    st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 20px 0;'>", unsafe_allow_html=True)


def render_system_management():
    """
    Renders the System Monitoring & Management Dashboard with:
    1. Health (blinking green LED dots, live component status)
    2. Resource Usage (gauges, progress bars, sparkline telemetry trends)
    3. Alerts (interactive SOC alert table with severity badges and triage actions)
    4. System Configuration (start/stop toggles, dynamic IP configuration, simulated consoles)
    """
    init_system_state()

    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1.5px solid #334155; border-radius: 10px; padding: 18px 24px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="font-size: 1.55rem; color: #ffffff; margin: 0; font-weight: 800; letter-spacing: -0.3px;">
                    🖥️ System Monitoring & Management Console
                </h1>
                <p style="font-size: 0.88rem; color: #94a3b8; margin-top: 4px; margin-bottom: 0;">
                    Infrastructure Health, Compute Pipeline Telemetry, Resource Allocations & Enclave Management
                </p>
            </div>
            <div>
                <span style="background: rgba(16, 185, 129, 0.15); border: 1.5px solid #10b981; color: #10b981; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; letter-spacing: 0.5px;">
                    ● CLUSTER HEALTH: OK
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render simulated modal if one was opened
    render_simulated_console_modal()

    # Tabs for the System Management Dashboard
    tabs = st.tabs([
        "System Health",
        "Resource Usage",
        "Alert Management",
        "System Configuration"
    ])

    # =========================================================================
    # TAB 1: HEALTH (Blinking Green LEDs)
    # =========================================================================
    with tabs[0]:
        st.markdown("### Real-Time Infrastructure Health & Telemetry")
        st.markdown("Components are actively monitored via ICMP heartbeat, REST health endpoints, and Redis ping probes.")

        nodes = st.session_state.system_nodes

        # Grid of cards grouped by subsystem
        col_g1, col_g2 = st.columns(2, gap="medium")

        with col_g1:
            # 1. Data Lakehouse Card
            st.markdown(
                """
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04); margin-bottom: 18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 14px;">
                        <h4 style="margin:0; font-size:1.15rem; color:#0f172a;">💾 Data Lakehouse</h4>
                        <span style="font-size:0.8rem; background:#eff6ff; color:#1d4ed8; padding:3px 8px; border-radius:4px; font-weight:700;">TIER 1 STORAGE</span>
                    </div>
                """,
                unsafe_allow_html=True
            )

            is_iceberg_ok = nodes["lakehouse_iceberg"]["status"] == "Running"
            is_ceph_ok = nodes["lakehouse_ceph"]["status"] == "Running"

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Apache Iceberg** (`{nodes['lakehouse_iceberg']['ip']}`)")
                st.markdown(render_blinking_indicator(is_iceberg_ok, "OK" if is_iceberg_ok else "STOPPED"), unsafe_allow_html=True)
                st.caption(f"Catalog Service: {'Active' if is_iceberg_ok else 'Inactive'} (Port {nodes['lakehouse_iceberg']['port']})")

            with c2:
                st.markdown(f"**Ceph Object Storage Engine** (`{nodes['lakehouse_ceph']['ip']}`)")
                st.markdown(render_blinking_indicator(is_ceph_ok, "OK" if is_ceph_ok else "STOPPED"), unsafe_allow_html=True)
                st.caption(f"Cluster: {'HEALTH_OK' if is_ceph_ok else 'HEALTH_DOWN'} (RGW S3 Pool)")

            st.markdown("</div>", unsafe_allow_html=True)

            # 2. Redis Shared Cache Card
            st.markdown(
                """
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 14px;">
                        <h4 style="margin:0; font-size:1.15rem; color:#0f172a;">⚡ Redis Shared Cache</h4>
                        <span style="font-size:0.8rem; background:#fef2f2; color:#b91c1c; padding:3px 8px; border-radius:4px; font-weight:700;">IN-MEMORY BUS</span>
                    </div>
                """,
                unsafe_allow_html=True
            )

            is_redis_ok = nodes["redis_server"]["status"] == "Running"
            st.markdown(f"**Redis Server** (connected at `{nodes['redis_server']['ip']}`)")
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:16px; margin: 8px 0;">
                    <div>Server Health: {render_blinking_indicator(is_redis_ok, 'OK' if is_redis_ok else 'STOPPED')}</div>
                    <div>Port: <code>{nodes['redis_server']['port']}</code></div>
                    <div>Latency: <code>0.12 ms</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption("Telemetry stream buffer for discrete 10s feature sequences.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_g2:
            # 3. Packet Processing Pipeline Card
            st.markdown(
                """
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04); margin-bottom: 18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 14px;">
                        <h4 style="margin:0; font-size:1.15rem; color:#0f172a;">⚙️ Packet Processing Pipeline</h4>
                        <span style="font-size:0.8rem; background:#f0fdf4; color:#15803d; padding:3px 8px; border-radius:4px; font-weight:700;">DISTRIBUTED COMPUTE</span>
                    </div>
                """,
                unsafe_allow_html=True
            )

            is_node1_ok = nodes["compute_node_1"]["status"] == "Running"
            is_node2_ok = nodes["compute_node_2"]["status"] == "Running"

            cn1, cn2 = st.columns(2)
            with cn1:
                st.markdown(f"**Compute Node 1** (`{nodes['compute_node_1']['ip']}`)")
                st.markdown(render_blinking_indicator(is_node1_ok, "OK" if is_node1_ok else "STOPPED"), unsafe_allow_html=True)
                st.caption(f"Task: Multi-Protocol Filtering ({'Active' if is_node1_ok else 'Halted'})")

            with cn2:
                st.markdown(f"**Compute Node 2** (`{nodes['compute_node_2']['ip']}`)")
                st.markdown(render_blinking_indicator(is_node2_ok, "OK" if is_node2_ok else "STOPPED"), unsafe_allow_html=True)
                st.caption(f"Task: Flow Feature Extraction ({'Active' if is_node2_ok else 'Halted'})")

            st.markdown("</div>", unsafe_allow_html=True)

            # 4. Threat Detection & Prediction Engine Card
            st.markdown(
                """
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 14px;">
                        <h4 style="margin:0; font-size:1.15rem; color:#0f172a;">🧠 Threat Detection & Prediction Engine</h4>
                        <span style="font-size:0.8rem; background:#faf5ff; color:#7e22ce; padding:3px 8px; border-radius:4px; font-weight:700;">WORLD MODEL CORE</span>
                    </div>
                """,
                unsafe_allow_html=True
            )

            is_threat_ok = nodes["threat_engine"]["status"] == "Running"
            st.markdown(f"**AI Inference Node** (`{nodes['threat_engine']['ip']}`)")
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:20px; margin: 8px 0;">
                    <div>Service Status: <strong>{'Running' if is_threat_ok else 'Stopped'}</strong></div>
                    <div>Health: {render_blinking_indicator(is_threat_ok, 'OK' if is_threat_ok else 'STOPPED')}</div>
                    <div>Port: <code>{nodes['threat_engine']['port']}</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption("Temporal PyTorch Attention-LSTM World Model with +10s, +30s, +60s forecast heads.")
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: RESOURCE USAGE
    # =========================================================================
    with tabs[1]:
        st.markdown("### Infrastructure Resource Allocations & Telemetry")
        st.markdown("Real-time utilization percentages, capacity thresholds, and 60-second telemetry sparkline trends.")

        nodes = st.session_state.system_nodes

        # Grid of resource progress bars
        r_col1, r_col2 = st.columns(2, gap="medium")

        with r_col1:
            # Apache Iceberg Storage
            iceberg_used = nodes["lakehouse_iceberg"]["storage_used_gb"]
            iceberg_total = nodes["lakehouse_iceberg"]["storage_total_gb"]
            iceberg_pct = (iceberg_used / iceberg_total) * 100

            st.markdown("#### 💾 Data Lakehouse: Apache Iceberg")
            st.write(f"**Storage Usage:** `{iceberg_used} GB / 12 TB` ({iceberg_pct:.1f}%)")
            st.progress(float(iceberg_pct / 100))

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Compute Node 1
            cn1_cpu = nodes["compute_node_1"]["cpu_pct"] if nodes["compute_node_1"]["status"] == "Running" else 0.0
            cn1_mem_used = nodes["compute_node_1"]["mem_used_gb"] if nodes["compute_node_1"]["status"] == "Running" else 0.0
            cn1_mem_total = nodes["compute_node_1"]["mem_total_gb"]
            cn1_mem_pct = (cn1_mem_used / cn1_mem_total) * 100

            st.markdown("#### ⚙️ Packet Processing: Compute Node 1")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.write(f"**CPU:** `{cn1_cpu:.0f}%`")
                st.progress(float(cn1_cpu / 100))
            with col_m2:
                st.write(f"**Memory:** `{cn1_mem_used:.0f} GB / {cn1_mem_total:.0f} GB` ({cn1_mem_pct:.1f}%)")
                st.progress(float(cn1_mem_pct / 100))

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Compute Node 2
            cn2_cpu = nodes["compute_node_2"]["cpu_pct"] if nodes["compute_node_2"]["status"] == "Running" else 0.0
            cn2_mem_used = nodes["compute_node_2"]["mem_used_gb"] if nodes["compute_node_2"]["status"] == "Running" else 0.0
            cn2_mem_total = nodes["compute_node_2"]["mem_total_gb"]
            cn2_mem_pct = (cn2_mem_used / cn2_mem_total) * 100

            st.markdown("#### ⚙️ Packet Processing: Compute Node 2")
            col_m3, col_m4 = st.columns(2)
            with col_m3:
                st.write(f"**CPU:** `{cn2_cpu:.0f}%`")
                st.progress(float(cn2_cpu / 100))
            with col_m4:
                st.write(f"**Memory:** `{cn2_mem_used:.0f} GB / {cn2_mem_total:.0f} GB` ({cn2_mem_pct:.1f}%)")
                st.progress(float(cn2_mem_pct / 100))

        with r_col2:
            # Redis Server Memory Load
            redis_mem_used = nodes["redis_server"]["mem_used_gb"] if nodes["redis_server"]["status"] == "Running" else 0.0
            redis_mem_total = nodes["redis_server"]["mem_total_gb"]
            redis_mem_pct = (redis_mem_used / redis_mem_total) * 100

            st.markdown("#### ⚡ Redis Shared Cache")
            st.write(f"**Memory Load:** `{redis_mem_used:.0f} GB / {redis_mem_total:.0f} GB` ({redis_mem_pct:.1f}%)")
            st.progress(float(redis_mem_pct / 100))

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Threat Detection Engine
            ai_cpu = nodes["threat_engine"]["cpu_pct"] if nodes["threat_engine"]["status"] == "Running" else 0.0
            ai_mem_used = nodes["threat_engine"]["mem_used_gb"] if nodes["threat_engine"]["status"] == "Running" else 0.0
            ai_mem_total = nodes["threat_engine"]["mem_total_gb"]
            ai_mem_pct = (ai_mem_used / ai_mem_total) * 100

            st.markdown("#### 🧠 Threat Detection & Prediction Engine")
            col_m5, col_m6 = st.columns(2)
            with col_m5:
                st.write(f"**CPU:** `{ai_cpu:.0f}%`")
                st.progress(float(ai_cpu / 100))
            with col_m6:
                st.write(f"**Memory:** `{ai_mem_used:.0f} GB / {ai_mem_total:.0f} GB` ({ai_mem_pct:.1f}%)")
                st.progress(float(ai_mem_pct / 100))

        st.markdown("---")
        st.markdown("#### 📈 Real-Time 60-Second Telemetry Sparkline Trends")

        # Generate realistic simulated sparkline historical telemetry (60 steps)
        np.random.seed(42)
        timeline = [f"-{i*1}s" for i in reversed(range(30))]

        df_telemetry_trends = pd.DataFrame({
            "Time": timeline,
            "Compute Node 1 CPU (%)": np.clip(35 + np.random.normal(0, 3, 30), 20, 50),
            "Compute Node 2 CPU (%)": np.clip(45 + np.random.normal(0, 4, 30), 30, 65),
            "AI Threat Engine CPU (%)": np.clip(35 + np.random.normal(0, 2.5, 30), 25, 45),
            "Redis Memory (GB)": np.clip(20 + np.random.normal(0, 0.4, 30), 18, 22)
        }).set_index("Time")

        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            st.markdown("**CPU Load History (Last 30s Window)**")
            st.line_chart(df_telemetry_trends[["Compute Node 1 CPU (%)", "Compute Node 2 CPU (%)", "AI Threat Engine CPU (%)"]])

        with ch_col2:
            st.markdown("**Redis In-Memory Buffer Load (GB)**")
            st.line_chart(df_telemetry_trends["Redis Memory (GB)"], color="#ef4444")

    # =========================================================================
    # TAB 3: ALERTS (Interactive SOC Alert Triage)
    # =========================================================================
    with tabs[2]:
        st.markdown("### Active Infrastructure & Security Alerts")
        st.markdown("Centralized alert triage feed with component-based filtering and acknowledgment actions.")

        col_filter, col_actions = st.columns([2, 1])
        with col_filter:
            components = ["All", "Compute Node 1", "Compute Node 2", "Data Lakehouse", "Redis Server", "Threat Detection Engine"]
            selected_comp = st.selectbox("Filter by Subsystem:", components, index=0)

        with col_actions:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Clear Acknowledged Alerts", use_container_width=True):
                st.session_state.system_alerts = [
                    a for a in st.session_state.system_alerts if a["status"] == "Active"
                ]
                st.success("Cleared dismissed alerts.")
                st.rerun()

        filtered_alerts = st.session_state.system_alerts
        if selected_comp != "All":
            filtered_alerts = [a for a in filtered_alerts if selected_comp in a["component"]]

        if not filtered_alerts:
            st.info("No active alerts matching the selected filter.")
        else:
            for idx, alert in enumerate(filtered_alerts):
                sev_color = {
                    "CRITICAL": "#ef4444",
                    "WARNING": "#f59e0b",
                    "INFO": "#3b82f6"
                }.get(alert["severity"], "#64748b")

                is_acknowledged = alert["status"] == "Acknowledged"

                card_border = "#e2e8f0" if is_acknowledged else sev_color
                opacity = "0.6" if is_acknowledged else "1.0"

                st.markdown(
                    f"""
                    <div style="background: #ffffff; border-left: 5px solid {card_border}; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; border-radius: 6px; padding: 14px 18px; margin-bottom: 10px; opacity: {opacity}; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <div>
                                <span style="background: {sev_color}; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">{alert['severity']}</span>
                                <strong style="margin-left: 8px; font-size: 0.95rem; color: #0f172a;">{alert['id']}</strong>
                                <span style="color: #64748b; font-size: 0.85rem; margin-left: 8px;">• Subsystem: <strong>{alert['component']}</strong></span>
                            </div>
                            <div style="font-size: 0.8rem; color: #64748b;">
                                🕒 {alert['timestamp']} | Status: <strong>{alert['status']}</strong>
                            </div>
                        </div>
                        <p style="font-size: 0.9rem; color: #334155; margin: 4px 0 0 0;">
                            {alert['message']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if not is_acknowledged:
                    if st.button(f"Acknowledge {alert['id']}", key=f"btn_ack_{alert['id']}"):
                        alert["status"] = "Acknowledged"
                        st.rerun()

    # =========================================================================
    # TAB 4: SYSTEM CONFIGURATION (Dynamic Control & Simulated Consoles)
    # =========================================================================
    with tabs[3]:
        st.markdown("### Infrastructure Component Configuration & Control Plane")
        st.markdown(
            """
            Start or stop nodes, update IP bindings dynamically, and launch interactive simulated management consoles.
            Changes made here update the **Health Indicators**, **Resource Usage**, and **Alerts** across all tabs in real-time.
            """
        )

        nodes = st.session_state.system_nodes

        # Accordions for each component
        for key, node in nodes.items():
            with st.expander(f"🔧 Configure {node['name']} ({node['category']})", expanded=(key == "threat_engine")):
                c_info, c_action, c_console = st.columns([1.5, 1, 1.2], gap="medium")

                with c_info:
                    st.markdown(f"**Subsystem:** {node['category']}")
                    st.markdown(f"**Current Status:** `{'Running' if node['status'] == 'Running' else 'Stopped'}`")
                    st.markdown(f"**Current Health:** `{node['health']}`")

                    # Dynamic IP change input
                    new_ip = st.text_input(f"Binding IP Address", value=node["ip"], key=f"ip_{node['id']}")
                    if st.button(f"Update IP for {node['id']}", key=f"btn_ip_{node['id']}"):
                        node["ip"] = new_ip.strip()
                        st.success(f"IP updated to {node['ip']}")
                        st.rerun()

                with c_action:
                    st.markdown("**Power / Process Control**")
                    if node["status"] == "Running":
                        if st.button(f"🛑 Stop Component", key=f"btn_stop_{node['id']}", use_container_width=True):
                            node["status"] = "Stopped"
                            node["health"] = "STOPPED"
                            st.session_state.system_alerts.insert(0, {
                                "id": f"ALT-{int(time.time()) % 10000}",
                                "timestamp": time.strftime("%H:%M:%S"),
                                "severity": "CRITICAL",
                                "component": node["name"],
                                "message": f"Operator manually STOPPED service on {node['ip']}.",
                                "status": "Active"
                            })
                            st.rerun()
                    else:
                        if st.button(f"▶️ Start Component", key=f"btn_start_{node['id']}", use_container_width=True):
                            node["status"] = "Running"
                            node["health"] = "OK"
                            st.session_state.system_alerts.insert(0, {
                                "id": f"ALT-{int(time.time()) % 10000}",
                                "timestamp": time.strftime("%H:%M:%S"),
                                "severity": "INFO",
                                "component": node["name"],
                                "message": f"Service successfully resumed and healthy on {node['ip']}.",
                                "status": "Active"
                            })
                            st.rerun()

                with c_console:
                    st.markdown("**Enclave Management Console**")
                    endpoint_label = f"{node['ip']}{node['endpoint']}" if node['endpoint'] else f"{node['ip']}"
                    st.caption(f"Target: `http://{endpoint_label}`")

                    if st.button(f"Launch Console ({endpoint_label})", key=f"btn_console_{node['id']}", use_container_width=True):
                        st.session_state.active_console_modal = node["id"]
                        st.rerun()
