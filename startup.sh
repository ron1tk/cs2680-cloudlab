#!/usr/bin/env bash
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive

mkdir -p /local/logs
exec > >(tee -a /local/logs/startup.log) 2>&1

echo "== System info =="
uname -a || true
lsb_release -a || true

echo "== Install base packages =="
apt-get update -y
apt-get install -y \
  tmux git curl ca-certificates \
  python3 python3-venv python3-pip python3-dev \
  build-essential cmake pkg-config \
  libopenblas-dev

echo "== GPU check (ok if missing, but Teal speedups won't match) =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi || true
else
  echo "WARNING: nvidia-smi not found. Either:"
  echo "  (a) this node has no GPU, or"
  echo "  (b) the image lacks NVIDIA drivers."
fi

echo "== Python venv =="
cd /local/teal
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip wheel setuptools

echo "== Install Python deps =="
# If the repo has requirements.txt, this is fine:
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

echo "== Sanity import check =="
python -c "import sys; print(sys.version)"
python -c "import torch; print('torch', torch.__version__, 'cuda?', torch.cuda.is_available())" || true

echo "Startup complete."