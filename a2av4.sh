#!/bin/bash

# Enhanced A2A startup script with intelligent agent routing
# This version includes automatic agent registration and improved error handling

# Change to the project root directory
PROJECT_ROOT="$(dirname "$0")"
cd "$PROJECT_ROOT"

echo "🚀 Starting A2A v4 with Intelligent Agent Routing..."

# --- VERIFICATION STEP FOR VEO AGENT ---
if [ -z "$GOOGLE_GENAI_USE_VERTEXAI" ] || [ "$GOOGLE_GENAI_USE_VERTEXAI" != "TRUE" ]; then
    echo "⚠️  WARNING: VEO agent requires GOOGLE_GENAI_USE_VERTEXAI=TRUE"
    echo "   The VEO video generation agent will not be available."
    echo "   Set the required environment variables to enable video generation."
    SKIP_VEO=true
else
    if [ -z "$GOOGLE_CLOUD_PROJECT" ] || [ -z "$GOOGLE_CLOUD_LOCATION" ] || [ -z "$VIDEO_GEN_GCS_BUCKET" ]; then
        echo "⚠️  WARNING: VEO agent requires additional environment variables:"
        echo "   - GOOGLE_CLOUD_PROJECT"
        echo "   - GOOGLE_CLOUD_LOCATION" 
        echo "   - VIDEO_GEN_GCS_BUCKET"
        echo "   The VEO video generation agent will not be available."
        SKIP_VEO=true
    else
        SKIP_VEO=false
    fi
fi

# Define agents and their properties
if [ "$SKIP_VEO" = true ]; then
    echo "📝 Starting with Coder Agent only (VEO disabled)"
    declare -a AGENT_PORTS=(8000 12111)
    declare -a AGENT_COMMANDS=(
        ".venv/bin/python -m uvicorn demo.ui.main:app --host 0.0.0.0 --port 8000 --log-level debug"
        ".venv/bin/python -m uvicorn samples.python.agents.coder.__main__:app --host 0.0.0.0 --port 12111 --log-level debug"
    )
    declare -a AGENT_NAMES=("UI Server" "Coder Agent")
else
    echo "📝 Starting with all agents (Coder + VEO)"
    declare -a AGENT_PORTS=(8000 12111 12200)
    declare -a AGENT_COMMANDS=(
        ".venv/bin/python -m uvicorn demo.ui.main:app --host 0.0.0.0 --port 8000 --log-level debug"
        ".venv/bin/python -m uvicorn samples.python.agents.coder.__main__:app --host 0.0.0.0 --port 12111 --log-level debug"
        ".venv/bin/python -m samples.python.agents.veo_video_gen --host 0.0.0.0 --port 12200"
    )
    declare -a AGENT_NAMES=("UI Server" "Coder Agent" "VEO Video Agent")
fi

# Kill any existing processes on the ports we're about to use
echo "🧹 Cleaning up existing processes..."
for port in "${AGENT_PORTS[@]}"; do
    pids=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "   Stopping processes on port $port: $pids"
        kill $pids 2>/dev/null
        sleep 2
        pids_after_term=$(lsof -t -i:$port 2>/dev/null)
        if [ -n "$pids_after_term" ]; then
            echo "   Force killing processes on port $port: $pids_after_term"
            kill -9 $pids_after_term 2>/dev/null
        fi
    fi
done

# Set up environment
export A2A_HOST=ADK
source .venv/bin/activate

# Create logs directory
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# Start all agents
echo "🎯 Starting agents with intelligent routing..."
for i in "${!AGENT_COMMANDS[@]}"; do
    cmd="${AGENT_COMMANDS[$i]}"
    port="${AGENT_PORTS[$i]}"
    name="${AGENT_NAMES[$i]}"
    log_file="$LOG_DIR/agent_${port}.log"

    echo "   Starting $name on port $port..."
    nohup bash -c "source .venv/bin/activate && export PYTHONPATH=\"$PROJECT_ROOT:$PYTHONPATH\" && export A2A_HOST=ADK && $cmd > $log_file 2>&1" &
    
    # Give each agent a moment to start
    sleep 1
done

echo "⏳ Waiting for agents to initialize..."
sleep 5

# Register agents automatically
echo "🔗 Registering agents with intelligent router..."
if python register_agents.py; then
    echo "✅ Agent registration completed successfully"
else
    echo "⚠️  Agent registration had some issues, but continuing..."
fi

echo ""
echo "🎉 A2A v4 with Intelligent Agent Routing is now running!"
echo ""
echo "📊 System Status:"
echo "   • UI Server: http://localhost:8000"
echo "   • Coder Agent: http://localhost:12111"
if [ "$SKIP_VEO" = false ]; then
    echo "   • VEO Video Agent: http://localhost:12200"
fi
echo ""
echo "🧠 Intelligent Routing Features:"
echo "   • Automatic agent selection based on request content"
echo "   • Fast pattern matching for optimal performance"
echo "   • Fallback routing for unmatched requests"
echo "   • Real-time agent capability analysis"
echo ""
echo "📝 Logs are available in the 'logs' directory"
echo "🔍 Check logs with: tail -f logs/agent_*.log"
echo ""
echo "To stop all agents, run: pkill -f 'uvicorn.*agent'"
