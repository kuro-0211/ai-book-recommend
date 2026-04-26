#!/bin/sh
set -e

MODEL="${OLLAMA_MODEL:-gemma3:4b}"

echo "[ollama-entrypoint] starting ollama serve..."
# 백그라운드로 ollama 데몬 기동 (PID 1을 ollama가 잡도록 마지막에 wait)
ollama serve &
OLLAMA_PID=$!

# 데몬이 살아날 때까지 대기
echo "[ollama-entrypoint] waiting for ollama API..."
i=0
until ollama list >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -gt 60 ]; then
    echo "[ollama-entrypoint] ollama did not become ready in time" >&2
    exit 1
  fi
  sleep 1
done
echo "[ollama-entrypoint] ollama is up."

# 모델 자동 pull (이미 있으면 빠르게 종료됨)
if ollama list | awk '{print $1}' | grep -qx "$MODEL"; then
  echo "[ollama-entrypoint] model '$MODEL' already present, skipping pull."
else
  echo "[ollama-entrypoint] pulling model '$MODEL' (one-time download)..."
  ollama pull "$MODEL" || {
    echo "[ollama-entrypoint] failed to pull $MODEL" >&2
    exit 1
  }
fi

# GPU 활성화 여부 안내 (Ollama는 가용 GPU가 있으면 자동 사용, 없으면 CPU 폴백)
if [ -e /dev/nvidia0 ] || command -v nvidia-smi >/dev/null 2>&1; then
  echo "[ollama-entrypoint] NVIDIA GPU detected — Ollama will use CUDA."
else
  echo "[ollama-entrypoint] no GPU detected — falling back to CPU inference."
fi

echo "[ollama-entrypoint] ready. attaching to ollama serve (PID $OLLAMA_PID)."
wait "$OLLAMA_PID"
