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
  ".venv/bin/python -m uvicorn demo.ui.main:app --host 0.0.0.0 --port 8000 --log-level debug"
  ".venv/bin/python -m uvicorn samples.python.agents.coder.__main__:app --host 0.0.0.0 --port 12111 --log-level debug"
  ".venv/bin/python -m samples.python.agents.veo_video_gen --host 0.0.0.0 --port 12200"
)

# Kill any existing processes on the ports we're about to use
for port in "${AGENT_PORTS[@]}"; do
  pids=$(lsof -t -i:$port)
  if [ -n "$pids" ]; then
    echo "Attempting to gracefully kill processes $pids on port $port"
    kill $pids # Send SIGTERM
    sleep 2 # Give processes time to shut down
    pids_after_term=$(lsof -t -i:$port)
    if [ -n "$pids_after_term" ]; then
      echo "Processes $pids_after_term on port $port are still running. Force killing."
      kill -9 $pids_after_term # Send SIGKILL
    fi
  fi
done
export A2A_HOST=ADK
source .venv/bin/activate

# Start all agents and redirect output to log files
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

for i in "${!AGENT_COMMANDS[@]}"; do
  cmd="${AGENT_COMMANDS[$i]}"
  port="${AGENT_PORTS[$i]}"
  log_file="$LOG_DIR/agent_${port}.log"

  echo "Starting agent: $cmd (logging to $log_file)"
        nohup bash -c 'source .venv/bin/activate && export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH" && '$cmd' > '$log_file' 2>&1' &


done

echo "All agents started in the background. Check logs in the 'logs' directory for details."
