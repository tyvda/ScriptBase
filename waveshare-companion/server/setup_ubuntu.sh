#!/usr/bin/env bash
# Ubuntu 22.04/24.04 LTS: install the local speech toolchain.
# Run this ON YOUR OWN Ubuntu LLM computer. It does not modify Ollama.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Ubuntu system packages (sudo may ask for a password)..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip ffmpeg ca-certificates

echo "Creating isolated Python environment..."
python3 -m venv "$script_dir/.venv"
"$script_dir/.venv/bin/python" -m pip install --upgrade pip
"$script_dir/.venv/bin/python" -m pip install -r "$script_dir/requirements.txt" piper-tts

echo "Downloading the German Piper voice (model and config)..."
mkdir -p "$script_dir/models"
"$script_dir/.venv/bin/python" -m piper.download_voices \
  --data-dir "$script_dir/models" de_DE-thorsten-medium

echo "Preparing the local Whisper small model (first download may take several minutes)..."
"$script_dir/.venv/bin/python" -c \
  'from faster_whisper import WhisperModel; WhisperModel("small", device="cpu", compute_type="int8"); print("Whisper small ready")'

echo "Done. Configure OLLAMA_MODEL; see README.md."
echo "Piper model: $script_dir/models/de_DE-thorsten-medium.onnx"

