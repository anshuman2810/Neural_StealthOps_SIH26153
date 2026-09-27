import os
import sys
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent.parent
    gnn_launcher = root_dir / "GNN" / "run_dashboard.py"
    cmd = [sys.executable, str(gnn_launcher)] + sys.argv[1:]
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
