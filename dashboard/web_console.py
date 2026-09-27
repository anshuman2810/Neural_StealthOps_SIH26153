import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import SEQ_LEN, WINDOW_SECONDS, STAGE_PLAYBOOKS, STAGE_SEVERITY
from src.data.scenario_loader import ScenarioLoader
from src.models.predictor import NetworkWorldModelPredictor
from src.explainability.gradient_attribution import GradientAttributionExplainer
from src.explainability.attention_explainer import AttentionExplainer
from src.simulation.rollout import AutoregressiveRolloutSimulator

# Initialize engine singletons
print("[*] Initializing AI World Model Predictor & Explainer...")
loader = ScenarioLoader()
predictor = NetworkWorldModelPredictor()
grad_explainer = GradientAttributionExplainer(predictor)
attn_explainer = AttentionExplainer(seq_len=SEQ_LEN, window_seconds=WINDOW_SECONDS)
rollout_sim = AutoregressiveRolloutSimulator(predictor)
print("[+] AI Engine ready.")

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predictive Network World Model — SOC Console</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-dark: #0b1120;
            --card-bg: #1e293b;
            --border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --green: #10b981;
            --amber: #f59e0b;
            --red: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); padding: 20px; }
        
        .header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid var(--border); border-radius: 10px; padding: 18px 24px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; color: #fff; }
        .header p { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }
        
        .badge { padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.9rem; letter-spacing: 0.5px; text-transform: uppercase; }
        .badge-NORMAL { background: rgba(16, 185, 129, 0.2); border: 1px solid var(--green); color: var(--green); }
        .badge-ELEVATED { background: rgba(245, 158, 11, 0.2); border: 1px solid var(--amber); color: var(--amber); }
        .badge-HIGH { background: rgba(249, 115, 22, 0.2); border: 1px solid #f97316; color: #f97316; }
        .badge-CRITICAL { background: rgba(239, 68, 68, 0.2); border: 1px solid var(--red); color: var(--red); }
        
        .controls { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; gap: 15px; align-items: center; flex-wrap: wrap; }
        select, button { background: #0f172a; border: 1px solid var(--border); color: #fff; padding: 8px 14px; border-radius: 6px; font-size: 0.9rem; cursor: pointer; }
        button:hover { background: #1e293b; border-color: var(--accent); }
        input[type="range"] { flex: 1; min-width: 200px; accent-color: var(--accent); }
        
        .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 14px; text-align: center; }
        .card-title { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 700; }
        .card-value { font-size: 1.6rem; font-weight: 800; margin: 8px 0; }
        .card-sub { font-size: 0.75rem; color: #64748b; }
        
        .mitre-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 20px; }
        .mitre-card { background: #0f172a; border: 1px solid var(--border); border-radius: 6px; padding: 10px; text-align: center; transition: all 0.3s; }
        .mitre-card.active { border: 2px solid var(--red); box-shadow: 0 0 10px rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.1); }
        .mitre-name { font-weight: 800; font-size: 0.85rem; color: #cbd5e1; margin: 4px 0; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
        .chart-box { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
        .chart-title { font-size: 0.9rem; font-weight: 700; color: #e2e8f0; margin-bottom: 10px; }
        
        .alert-box { background: rgba(239, 68, 68, 0.1); border-left: 4px solid var(--red); border-radius: 6px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🛡️ Predictive Network World Model — SOC Threat Console</h1>
            <p>Direct Multi-Horizon ATT&CK Trajectory Forecasting (+10s, +30s, +60s Lead Time)</p>
        </div>
        <div>
            <span id="threatBadge" class="badge badge-NORMAL">NORMAL</span>
        </div>
    </div>

    <div class="controls">
        <label style="font-weight:600; font-size:0.85rem;">Scenario:</label>
        <select id="scenarioSelect"></select>
        
        <button id="btnPlay">▶️ Play Replay</button>
        <button id="btnPause">⏸️ Pause</button>
        <button id="btnPrev">⏮️ Prev</button>
        <button id="btnNext">⏭️ Next</button>
        
        <input type="range" id="timeSlider" min="12" max="100" value="12">
        <span id="stepLabel" style="font-family:monospace; color:var(--accent);">Window 12</span>
    </div>

    <div class="grid-5">
        <div class="card">
            <div class="card-title">Threat Level</div>
            <div id="valThreat" class="card-value" style="color:var(--green)">NORMAL</div>
            <div class="card-sub">State Trajectory</div>
        </div>
        <div class="card">
            <div class="card-title">Risk at +10s</div>
            <div id="valRisk10" class="card-value" style="color:var(--green)">0.0%</div>
            <div class="card-sub">Next 10s Window</div>
        </div>
        <div class="card" style="border-color:var(--accent); box-shadow:0 0 10px rgba(56,189,248,0.15)">
            <div class="card-title" style="color:var(--accent)">Risk at +30s (Primary)</div>
            <div id="valRisk30" class="card-value" style="color:var(--green)">0.0%</div>
            <div class="card-sub">Advance Lead Warning</div>
        </div>
        <div class="card">
            <div class="card-title">Risk at +60s</div>
            <div id="valRisk60" class="card-value" style="color:var(--green)">0.0%</div>
            <div class="card-sub">1-Minute Forecast</div>
        </div>
        <div class="card">
            <div class="card-title">Forecasted Stage</div>
            <div id="valStage" class="card-value" style="font-size:1.15rem; color:#f43f5e;">Normal</div>
            <div id="valConf" class="card-sub">Confidence: 95.0%</div>
        </div>
    </div>

    <div class="mitre-grid" id="mitreContainer"></div>

    <div class="grid-2">
        <div class="chart-box">
            <div class="chart-title">🔮 60-Second Autoregressive Rollout Simulation</div>
            <div style="height: 240px;"><canvas id="rolloutChart"></canvas></div>
        </div>
        <div class="chart-box">
            <div class="chart-title">📊 Live Network Traffic & Packet Velocity</div>
            <div style="height: 240px;"><canvas id="telemetryChart"></canvas></div>
        </div>
    </div>

    <div class="grid-2">
        <div class="chart-box">
            <div class="chart-title">⏳ Temporal Attention Weights (Preceding 12 Windows)</div>
            <div style="height: 220px;"><canvas id="attnChart"></canvas></div>
        </div>
        <div class="chart-box">
            <div class="chart-title">🔍 Gradient × Input Feature Importance (Top Risk Drivers)</div>
            <div style="height: 220px;"><canvas id="xaiChart"></canvas></div>
        </div>
    </div>

    <div class="alert-box" id="alertContainer">
        <div>
            <div id="alertTitle" style="font-weight:800; font-size:1.05rem; color:#fff;">✅ All Systems Operational — Baseline Conformance</div>
            <div id="alertDesc" style="color:#cbd5e1; font-size:0.85rem; margin-top:4px;">No malicious state transitions observed. Telemetry metrics within normal limits.</div>
        </div>
        <button id="btnMitigate" style="background:#ef4444; border:none; padding:8px 16px; font-weight:700;">🛡️ Deploy Quarantine</button>
    </div>

    <script>
        const MITRE_STAGES = ['Normal', 'Initial Access', 'Credential Access', 'Lateral Movement', 'Command and Control', 'Impact'];
        let activeScenario = '';
        let timer = null;
        let chartRollout, chartTelemetry, chartAttn, chartXai;

        async function init() {
            // Build MITRE stage cards
            const mContainer = document.getElementById('mitreContainer');
            MITRE_STAGES.forEach(s => {
                mContainer.innerHTML += `
                    <div class="mitre-card" id="stage-${s.replace(/\\s+/g, '')}">
                        <div style="font-size:0.7rem; color:#64748b; font-weight:700;">PHASE</div>
                        <div class="mitre-name">${s}</div>
                        <div style="font-size:0.7rem; color:#94a3b8;" id="prob-${s.replace(/\\s+/g, '')}">0.0%</div>
                    </div>
                `;
            });

            // Initialize Chart.js
            initCharts();

            // Fetch scenarios
            const res = await fetch('/api/scenarios');
            const data = await res.json();
            const sel = document.getElementById('scenarioSelect');
            sel.innerHTML = data.scenarios.map(s => `<option value="${s}">${s}</option>`).join('');
            activeScenario = data.scenarios[0];

            sel.onchange = (e) => {
                activeScenario = e.target.value;
                document.getElementById('timeSlider').value = 12;
                updateStep();
            };

            const slider = document.getElementById('timeSlider');
            slider.oninput = (e) => {
                document.getElementById('stepLabel').innerText = 'Window ' + e.target.value;
                updateStep();
            };

            document.getElementById('btnPlay').onclick = () => {
                if (timer) clearInterval(timer);
                timer = setInterval(() => {
                    let v = parseInt(slider.value);
                    if (v < parseInt(slider.max)) {
                        slider.value = v + 1;
                        slider.oninput({target: slider});
                    } else {
                        clearInterval(timer);
                    }
                }, 1000);
            };
            document.getElementById('btnPause').onclick = () => clearInterval(timer);
            document.getElementById('btnPrev').onclick = () => {
                slider.value = Math.max(12, parseInt(slider.value) - 1);
                slider.oninput({target: slider});
            };
            document.getElementById('btnNext').onclick = () => {
                slider.value = Math.min(parseInt(slider.max), parseInt(slider.value) + 1);
                slider.oninput({target: slider});
            };

            updateStep();
        }

        function initCharts() {
            const chartCfg = { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94a3b8' } } }, scales: { x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }, y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } } } };

            chartRollout = new Chart(document.getElementById('rolloutChart'), {
                type: 'line',
                data: { labels: ['+10s', '+20s', '+30s', '+40s', '+50s', '+60s'], datasets: [{ label: 'Forecasted Threat Risk (%)', data: [0,0,0,0,0,0], borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.15)', fill: true, tension: 0.3 }] },
                options: { ...chartCfg, scales: { ...chartCfg.scales, y: { ...chartCfg.scales.y, min: 0, max: 100 } } }
            });

            chartTelemetry = new Chart(document.getElementById('telemetryChart'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Flow Count', data: [], borderColor: '#38bdf8', tension: 0.2 }, { label: 'Packet Volume', data: [], borderColor: '#818cf8', tension: 0.2 }] },
                options: chartCfg
            });

            chartAttn = new Chart(document.getElementById('attnChart'), {
                type: 'bar',
                data: { labels: [], datasets: [{ label: 'Attention Weight (%)', data: [], backgroundColor: '#38bdf8' }] },
                options: chartCfg
            });

            chartXai = new Chart(document.getElementById('xaiChart'), {
                type: 'bar',
                data: { labels: [], datasets: [{ label: 'Feature Importance (%)', data: [], backgroundColor: '#f97316' }] },
                options: { ...chartCfg, indexAxis: 'y' }
            });
        }

        async function updateStep() {
            const step = document.getElementById('timeSlider').value;
            const res = await fetch(`/api/step?scenario=${encodeURIComponent(activeScenario)}&step=${step}`);
            const data = await res.json();

            // Update Executive Metrics
            const badge = document.getElementById('threatBadge');
            badge.className = 'badge badge-' + data.threat_level;
            badge.innerText = data.threat_level;

            document.getElementById('valThreat').innerText = data.threat_level;
            document.getElementById('valThreat').style.color = (data.threat_level === 'CRITICAL' ? 'var(--red)' : (data.threat_level === 'NORMAL' ? 'var(--green)' : 'var(--amber)'));
            
            document.getElementById('valRisk10').innerText = (data.risk_10s * 100).toFixed(1) + '%';
            document.getElementById('valRisk30').innerText = (data.risk_30s * 100).toFixed(1) + '%';
            document.getElementById('valRisk60').innerText = (data.risk_60s * 100).toFixed(1) + '%';
            
            document.getElementById('valStage').innerText = data.predicted_stage;
            document.getElementById('valConf').innerText = 'Confidence: ' + (data.stage_confidence * 100).toFixed(1) + '%';

            // Update MITRE Stages
            MITRE_STAGES.forEach(s => {
                const el = document.getElementById('stage-' + s.replace(/\\s+/g, ''));
                const probEl = document.getElementById('prob-' + s.replace(/\\s+/g, ''));
                if (el) {
                    if (s === data.predicted_stage) el.classList.add('active');
                    else el.classList.remove('active');
                }
                if (probEl) {
                    const prob = (data.stage_probabilities[s] || 0) * 100;
                    probEl.innerText = prob.toFixed(1) + '%';
                }
            });

            // Update Charts
            chartRollout.data.datasets[0].data = data.rollout.map(r => r.risk_pct);
            chartRollout.update();

            chartTelemetry.data.labels = data.telemetry.labels;
            chartTelemetry.data.datasets[0].data = data.telemetry.flow_counts;
            chartTelemetry.data.datasets[1].data = data.telemetry.packet_counts;
            chartTelemetry.update();

            chartAttn.data.labels = data.attention.map(a => a.time_offset);
            chartAttn.data.datasets[0].data = data.attention.map(a => a.percentage);
            chartAttn.update();

            chartXai.data.labels = data.attribution.map(a => a.feature);
            chartXai.data.datasets[0].data = data.attribution.map(a => a.relative_pct);
            chartXai.update();

            // Update Alert Box
            if (data.threat_level === 'CRITICAL' || data.threat_level === 'HIGH') {
                document.getElementById('alertTitle').innerText = '🚨 ' + data.predicted_stage + ' Trajectory Detected (Risk: ' + (data.risk_30s * 100).toFixed(1) + '%)';
                document.getElementById('alertDesc').innerText = 'Recommended Mitigation: ' + data.playbook;
                document.getElementById('alertContainer').style.borderLeftColor = 'var(--red)';
                document.getElementById('alertContainer').style.background = 'rgba(239, 68, 68, 0.15)';
            } else {
                document.getElementById('alertTitle').innerText = '✅ All Systems Operational — Baseline Conformance';
                document.getElementById('alertDesc').innerText = 'No malicious state transitions observed. Telemetry metrics within normal limits.';
                document.getElementById('alertContainer').style.borderLeftColor = 'var(--green)';
                document.getElementById('alertContainer').style.background = 'rgba(16, 185, 129, 0.1)';
            }
        }

        window.onload = init;
    </script>
</body>
</html>
"""

class SOCHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))

        elif path == "/api/scenarios":
            scenarios = loader.get_scenario_names()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"scenarios": scenarios}).encode("utf-8"))

        elif path == "/api/step":
            scenario_name = params.get("scenario", [loader.get_scenario_names()[0]])[0]
            step_idx = int(params.get("step", [SEQ_LEN])[0])

            df = loader.load_scenario(scenario_name)
            step_idx = max(SEQ_LEN, min(step_idx, len(df)))

            seq, current_row, gt = loader.get_sliding_window(df, step_idx)
            pred = predictor.predict(seq)
            attr_df = grad_explainer.explain(seq, horizon_idx=1, top_k=7)
            attn_df = attn_explainer.explain(pred['attention_weights'])
            roll_df = rollout_sim.simulate(seq, k_steps=6)

            history_df = df.iloc[step_idx - SEQ_LEN:step_idx]

            payload = {
                "threat_level": pred['threat_level'],
                "max_risk": pred['max_risk'],
                "risk_10s": pred['risk_10s'],
                "risk_30s": pred['risk_30s'],
                "risk_60s": pred['risk_60s'],
                "predicted_stage": pred['predicted_stage'],
                "stage_confidence": pred['stage_confidence'],
                "stage_probabilities": pred['stage_probabilities'],
                "playbook": STAGE_PLAYBOOKS.get(pred['predicted_stage'], 'Standard passive monitoring.'),
                "rollout": roll_df.to_dict(orient="records"),
                "attention": attn_df.to_dict(orient="records"),
                "attribution": attr_df.to_dict(orient="records"),
                "telemetry": {
                    "labels": [f"t-{10*(SEQ_LEN-1-i)}s" for i in range(SEQ_LEN)],
                    "flow_counts": history_df['flow_count'].tolist(),
                    "packet_counts": history_df['total_packets'].tolist()
                }
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port: int = 8080):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    server = HTTPServer(("0.0.0.0", port), SOCHandler)
    print("\n" + "=" * 55)
    print(f"[+] SOC Threat Console Server LIVE at http://localhost:{port}")
    print("=" * 55 + "\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)
