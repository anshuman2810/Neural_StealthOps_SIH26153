# Predictive Network World Model for Threat Forecasting
**SIH 26153 — Neural StealthOps**

An enterprise-grade **Deep Learning World Model** for real-time proactive cyber defense. Operating over 10-second discrete network telemetry windows, the system predicts latent state transitions, forecasts attack hazard risk across multi-step horizons (**+10s, +30s, +60s**), aligns transitions to 7 coarse MITRE ATT&CK stages, models port-to-port attack state transitions, and simulates 6-step autoregressive future trajectories with SHAP explainability.

---

## Key Highlights

- **Predictive World Model Architecture:** 2-layer Attention-LSTM ($H=64$) with multi-task prediction heads: next network state $\hat{s}_{t+1}$, multi-horizon threat risk ($P_{+10\text{s}}, P_{+30\text{s}}, P_{+60\text{s}}$), attack volume intensity, and MITRE ATT&CK progression.
- **Superior Multi-Horizon Durability:** Outperforms non-temporal baselines across all horizons:
  - **+10s:** F1 = **0.991**, Recall = **0.995**, Precision = **0.987**, ROC-AUC = **0.998**
  - **+30s (Primary):** F1 = **0.988**, Recall = **0.992**, Precision = **0.984**, ROC-AUC = **0.998**
  - **+60s (Durability):** F1 = **0.952**, Recall = **0.968** (+17.7% recall retention over Logistic Regression)
- **High-Efficiency CPU Inference:** Operates at **0.19 ms** per forecast slice and **0.56 ms** for the complete multi-task forward pass on an 8-core CPU (>17,000x faster than the 10-second telemetry window, consuming only 0.0056% of CPU budget).
- **Streamlit SOC Live Console:** Clean enterprise light theme dashboard with port state transitions, probability distributions, live MITRE matrix, counterfactual rollout simulator, and SHAP explainability.

---

## Dataset & Benchmark Telemetry

### Training Data Source: CSE-CIC-IDS2018
The Attention-LSTM World Model was trained and evaluated on flow records from the official **CSE-CIC-IDS2018** benchmark dataset (Communications Security Establishment & Canadian Institute for Cybersecurity).

The raw processed traffic dataset is publicly hosted on AWS S3 and can be queried or summarized directly without AWS credentials:
```bash
aws s3 ls --no-sign-request --summarize --human-readable --recursive "s3://cse-cic-ids2018/Processed Traffic Data for ML Algorithms/"
```

To download all or individual CSV capture files into the `dataset/` directory:
```bash
aws s3 cp --no-sign-request "s3://cse-cic-ids2018/Processed Traffic Data for ML Algorithms/" dataset/ --recursive
```

### Dataset Files Used for Training & State Modeling
The following 10 chronological capture files are processed by the chunked 10-second state builder:
1. `Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv` *(FTP-BruteForce, SSH-Bruteforce)*
2. `Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv` *(DoS-GoldenEye, DoS-Slowloris)*
3. `Friday-16-02-2018_TrafficForML_CICFlowMeter.csv` *(DoS-SlowHTTPTest, DoS-Hulk)*
4. `Thuesday-20-02-2018_TrafficForML_CICFlowMeter.csv` *(DDoS-LOIC-HTTP, DDoS-HOIC)*
5. `Wednesday-21-02-2018_TrafficForML_CICFlowMeter.csv` *(DDOS-LOIC-UDP)*
6. `Thursday-22-02-2018_TrafficForML_CICFlowMeter.csv` *(Brute Force -Web, Brute Force -XSS, SQL Injection)*
7. `Friday-23-02-2018_TrafficForML_CICFlowMeter.csv` *(Brute Force -Web, Brute Force -XSS, SQL Injection)*
8. `Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv` *(Infiltration)*
9. `Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv` *(Infiltration)*
10. `Friday-02-03-2018_TrafficForML_CICFlowMeter.csv` *(Botnet C2)*

> **Note:** Downloading the multi-gigabyte raw dataset is **optional**. The repository includes lightweight precomputed scenarios in `demo_data/` and pre-trained model weights in `artifacts_v2/` so the dashboard and evaluation scripts run out-of-the-box immediately after cloning.

---

## Repository Structure

```text
├── .streamlit/
│   └── config.toml                        # Streamlit light theme & contrast UI styling
├── artifacts_v2/
│   ├── attention_world_model.pt           # Trained PyTorch Attention-LSTM World Model
│   ├── scaler.npz                         # StandardScaler 21-feature normalizer
│   ├── latest_forecast.csv                # Rollout simulation export
│   ├── latest_explanation.csv             # Feature attribution export
│   ├── benchmark_hardware_latency.png     # Host CPU inference latency chart
│   ├── benchmark_f1_recall_comparison.png # Performance comparison vs Logistic Regression
│   ├── benchmark_multi_horizon_decay.png  # Multi-horizon durability decay curve
│   └── benchmark_batch_throughput.png     # Batch throughput scaling chart
├── dashboard/
│   ├── app.py                             # Main Streamlit SOC Dashboard
│   ├── web_console.py                     # Standalone API/web runner
│   └── components/
│       ├── header.py                      # Telemetry strip and threat banners
│       ├── metrics.py                     # Multi-horizon risk probability cards
│       ├── charts.py                      # Multi-horizon trajectories & telemetry features
│       ├── mitre_matrix.py                # 7-stage MITRE ATT&CK progression matrix
│       ├── rollout_view.py                # 6-step autoregressive future simulation
│       ├── xai_panel.py                   # SHAP explainability & marginal contributions
│       ├── port_analysis.py               # Port-to-port attack state transitions
│       └── alert_feed.py                  # Live alert queue
├── demo_data/                             # Precomputed scenarios for instant live demo
│   ├── 1_botnet_c2_attack.csv
│   ├── 2_infiltration_lateral_movement.csv
│   ├── 3_credential_brute_force.csv
│   ├── 4_ddos_high_impact.csv
│   └── 5_normal_baseline.csv
├── scripts/
│   ├── run_dashboard.py                   # Production dashboard launcher
│   ├── precompute_scenarios.py            # Scenario generator from raw CSVs
│   └── create_tables_doc.py               # Documentation generator
├── src/
│   ├── config.py                          # 21-feature schema, 10s windows, MITRE taxonomy
│   ├── data/                              # Flow cleaner & 10s state builder
│   ├── models/                            # PyTorch AttentionWorldModel & Predictor
│   ├── explainability/                    # Temporal attention, gradient × input, SHAP
│   └── simulation/                        # 6-step rollout simulator & port engine
├── world_model_forecasting_v2.ipynb       # Model training, benchmarking & CPU profiling notebook
├── requirements.txt                       # Project dependencies
├── .gitignore                             # Git ignore rules (excludes raw dataset & caches)
└── README.md
```

---

## Quickstart: Running on Another PC

### 1. Clone the Repository
```bash
git clone https://github.com/anshuman2810/Neural_StealthOps_SIH26153.git
cd Neural_StealthOps_SIH26153
```

### 2. Create a Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/macOS
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Streamlit SOC Dashboard
The repository includes lightweight precomputed demo scenarios (`demo_data/`) and the pre-trained model checkpoint (`artifacts_v2/attention_world_model.pt`), so the dashboard runs **immediately out of the box with zero external dataset downloads**:
```bash
python scripts/run_dashboard.py
```
*Or directly via Streamlit:*
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501` to access the SOC Console.

### 4. Interactive Model Training & Benchmarking Notebook
To inspect or re-run the multi-horizon benchmarks, honest baseline comparison, and CPU hardware latency profiling:
```bash
jupyter notebook world_model_forecasting_v2.ipynb
```

---

## Telemetry Feature Schema (21 Metrics)

| Category | Telemetry Features |
| :--- | :--- |
| **Traffic Entropy & Diversity** | `port_entropy`, `protocol_diversity` |
| **Temporal & Rate Dynamics** | `mean_Flow Duration`, `mean_Flow Byts/s`, `mean_Flow Pkts/s`, `mean_Flow IAT Mean`, `mean_Flow IAT Std` |
| **Packet Inspection** | `mean_Pkt Len Mean`, `mean_Pkt Len Std` |
| **TCP Control Plane Flags** | `mean_SYN Flag Cnt`, `mean_ACK Flag Cnt`, `mean_RST Flag Cnt`, `mean_FIN Flag Cnt`, `mean_PSH Flag Cnt` |
| **Activity Patterns** | `mean_Active Mean`, `mean_Idle Mean` |
| **Volumetric Scales ($\log(1+x)$)** | `log_flow_count`, `log_total_packets`, `log_total_bytes`, `log_attack_flow_count`, `log_unique_dst_ports` |

---

## License & Attribution
Developed for Smart India Hackathon (SIH) 2026 — Problem Statement SIH 26153. Built on CSE-CIC-IDS2018 benchmark telemetry.
