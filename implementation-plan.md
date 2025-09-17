# Implementation Plan: Fixing Host Agent Routing

## Current Goal

Our current goal is to ensure the Host Agent is consistently responsive and routes prompts correctly to the appropriate specialized agents (Coder, Veo Video Gen, etc.) every time.

## Problem Diagnosis

Despite previous attempts, the Host Agent is still not reliably routing prompts. The primary issues identified are:

1.  **Agent Card Discovery (Resolved):** The agents were initially not serving their `agent-card.json` files correctly, preventing the Host Agent from discovering their capabilities. This was addressed by explicitly adding FastAPI routes for `/.well-known/agent-card.json` in `samples/python/agents/coder/__main__.py` and `samples/python/agents/veo_video_gen/__main__.py`.
2.  **Host Agent's Routing Logic (Ongoing):** The Host Agent's internal logic for determining the target agent and instructing the LLM to use the `send_message` tool is still problematic. This manifests as:
    *   `ModuleNotFoundError` for `adk_host_manager` when the UI starts, indicating an import path issue.
    *   The LLM not consistently calling the `send_message` tool with the pre-determined `remote_agent_url`.
    *   The `replace` tool failing due to exact string matching issues, hindering iterative development.

## Next Steps

To address the ongoing routing logic issues and ensure a robust solution, we will proceed with the following steps:

### Phase 1: Fix `adk_host_manager.py` `process_message` Method

The `process_message` method in `demo/ui/service/server/adk_host_manager.py` is currently duplicated and incorrectly structured, leading to the `ModuleNotFoundError` and preventing the programmatic routing logic from executing correctly.

1.  **Read `demo/ui/service/server/adk_host_manager.py`:** Get the exact current content of the `process_message` method.
2.  **Construct Precise `old_string` and `new_string`:** Based on the actual content, we will construct a precise `old_string` representing the duplicated and incorrect `process_message` method. The `new_string` will contain the corrected and streamlined `process_message` method, ensuring the programmatic routing logic (`_determine_target_agent`) is called correctly and its output is used to guide the LLM's tool call.
3.  **Overwrite `demo/ui/service/server/adk_host_manager.py`:** Use `write_file` to overwrite the entire file with the corrected content.

### Phase 2: Verify and Test

Once `adk_host_manager.py` is corrected, we will perform a full verification and testing cycle.

1.  **Restart All Agents:** Stop all currently running agents and restart them using `bash a2av3.sh`. This ensures all code changes are loaded.
2.  **Verify Agent Startup and Accessibility:**
    *   Read `logs/agent_8000.log` (UI Agent).
    *   Read `logs/agent_12111.log` (Coder Agent).
    *   Read `logs/agent_12200.log` (Veo Video Gen Agent).
    *   Look for "Application startup complete" and the absence of `ModuleNotFoundError` or `ConnectError`.
3.  **Run Automated Routing Test:** Execute the `test_routing.py` script. This script will:
    *   Send predefined test prompts to the UI.
    *   Analyze the agent logs for `DEBUG` prints indicating correct routing decisions (`DEBUG: Determined target_agent_url: ...`) and successful message processing by the target agents (`Processing message: ...`).
    *   Report `SUCCESS` or `FAILURE` for each test case.

This detailed plan will allow us to systematically address the remaining issues and confirm the Host Agent's reliable routing behavior.
