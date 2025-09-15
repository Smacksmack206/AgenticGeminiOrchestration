#!/bin/bash

# Change to the project root directory
PROJECT_ROOT="$(dirname "$0")"
cd "$PROJECT_ROOT"

# --- VERIFICATION STEP FOR VEO AGENT ---
# The veo_video_gen agent requires specific environment variables.
# This script will now check for them before trying to run.
if [ -z "$GOOGLE_GENAI_USE_VERTEXAI" ] || [ "$GOOGLE_GENAI_USE_VERTEXAI" != "TRUE" ]; then
    echo "ERROR: The 'veo_video_gen' agent requires GOOGLE_GENAI_USE_VERTEXAI=TRUE."
    echo "Please set the required environment variables before running this script."
    exit 1
fi

if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "ERROR: The 'veo_video_gen' agent requires GOOGLE_CLOUD_PROJECT to be set."
    echo "Please set the required environment variables before running this script."
    exit 1
fi

if [ -z "$GOOGLE_CLOUD_LOCATION" ]; then
    echo "ERROR: The 'veo_video_gen' agent requires GOOGLE_CLOUD_LOCATION to be set."
    echo "Please set the required environment variables before running this script."
    exit 1
fi

if [ -z "$VIDEO_GEN_GCS_BUCKET" ]; then
    echo "ERROR: The 'veo_video_gen' agent requires VIDEO_GEN_GCS_BUCKET to be set for video storage."
    echo "Please set the required environment variables before running this script."
    exit 1
fi
# --- END VERIFICATION ---


# Define agents and their properties
declare -a AGENT_PORTS=(8000 12111 12200)
declare -a AGENT_COMMANDS=(
  "python -m uvicorn demo.ui.main:app --host 0.0.0.0 --port 8000"
  "python -m uvicorn samples.python.agents.coder.__main__:app --host 0.0.0.0 --port 12111"
  "python -m samples.python.agents.veo_video_gen --host 0.0.0.0 --port 12200"
)

# Kill any existing processes on the ports we're about to use
for port in "${AGENT_PORTS[@]}"; do
  pids=$(lsof -t -i:$port)
  if [ -n "$pids" ]; then
    echo "Killing processes $pids on port $port"
    kill $pids
  fi
done

# Activate the virtual environment
source .venv/bin/activate

# Start all agents and redirect output to log files
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

for i in "${!AGENT_COMMANDS[@]}"; do
  cmd="${AGENT_COMMANDS[$i]}"
  port="${AGENT_PORTS[$i]}"
  log_file="$LOG_DIR/agent_${port}.log"

  echo "Starting agent: $cmd (logging to $log_file)"
  $cmd > "$log_file" 2>&1 &
done

echo "All agents started in the background. Check logs in the 'logs' directory for details."
