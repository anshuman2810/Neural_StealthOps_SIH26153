import os
import sys
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent.parent
    app_path = root_dir / "dashboard" / "app.py"
    demo_data_dir = root_dir / "demo_data"

    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("=" * 65)
    print("[*] Launching Predictive Network World Model SOC Console")
    print("=" * 65)

    # Check if demo scenarios exist
    scenario_files = list(demo_data_dir.glob("*.csv")) if demo_data_dir.exists() else []
    if not scenario_files:
        print("\n[!] No precomputed scenarios found in demo_data/.")
        print("[*] Running scripts/precompute_scenarios.py first...")
        subprocess.run([sys.executable, str(root_dir / "scripts" / "precompute_scenarios.py")], check=True)

    print(f"\n[*] Starting Streamlit SOC Dashboard ({app_path})...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless", "false",
        "--theme.base", "dark"
    ]
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    main()
