#!/bin/bash
set -e

echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Starting Ollama in background..."
ollama serve &

echo "Waiting for Ollama to start..."
sleep 10

echo "Pulling Phi-3 model..."
ollama pull phi3

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build complete!"
