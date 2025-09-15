#AgenticGeminiOrchestration

### New Agents and Functionality
I've have added new agents and extended existing ones with specific functionality:
* **VEO Video Generation Agent:** A new agent was created to generate videos from text prompts using Google's VEO model. It is configured to stream progress updates and provide a GCS URL for the final video. It requires specific Google Cloud environment variables to be set for it to function correctly.
* **A2A Coder Agent:** The codebase includes a Coder agent (`samples/python/agents/coder/`) that is likely used for code generation or analysis.

***

### Custom User Interface and Hosts
The most significant changes are in the user interface and host services, as I've updated the UI to be beautiful support video output have quality of life improvements like actually being able to delete a conversations.
* **Mesop UI (`demo/ui`):** I've built a web-based user interface using the Mesop framework, which includes pages for viewing conversations, a list of tasks, and a list of agents.
* **Custom Startup Script (`a2av3.sh`):** A shell script was created to manage the startup and shutdown of multiple agents and the UI server simultaneously on different ports so no need to open multi tabs to run new agents they all can instead be started via a2av3.sh to run the project.
* **Custom Hosts:** Several custom host services were implemented, such as `multiagent`, which acts as a central orchestrator for other agents running on separate ports.

***

### Configuration and Dependency Management
My project has its own unique configuration and dependency setup.
* **Environment Variables:** I've added new environment variables like `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, and `VIDEO_GEN_GCS_BUCKET` to support the new VEO agent and other Google Cloud services.
* **Project and Dependency Files:** The `pyproject.toml` and `uv.lock` files show that I've managed project dependencies and a virtual environment separately from the core framework.
* **Linting and Formatting:** I've included `.ruff.toml` and `.prettierrc` files, suggesting a focus on code quality and formatting.

# Agent2Agent (A2A) Samples

This repository contains code samples and demos which use the [Agent2Agent (A2A) Protocol](https://goo.gle/a2a).

## How to Install and Run

To get started with this project, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone git@github.com:Smacksmack206/AgenticGeminiOrchestration.git
    cd AgenticGeminiOrchestration
    ```

2.  **Set up Python Virtual Environment and Install Dependencies:**
    It's recommended to use `uv` for dependency management.
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    uv sync
    ```
    *Note: If `uv` is not installed, you can install it via `pip install uv` or use `pip install -r requirements.txt` if a `requirements.txt` is available.*

3.  **Configure Environment Variables (for VEO Video Generation Agent):**
    The `veo_video_gen` agent requires specific Google Cloud environment variables. Set these in your environment before running the `a2av3.sh` script:
    ```bash
    export GOOGLE_GENAI_USE_VERTEXAI="TRUE"
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-region" # e.g., us-central1
    export VIDEO_GEN_GCS_BUCKET="your-gcs-bucket-for-videos"
    ```
    Replace `"your-gcp-project-id"`, `"your-gcp-region"`, and `"your-gcs-bucket-for-videos"` with your actual Google Cloud project details.

4.  **Run the A2A Demo Environment:**
    The `a2av3.sh` script will start the main UI (dashboard) and any pre-configured agents.
    ```bash
    ./a2av3.sh
    ```
    Access the dashboard, usually at `http://localhost:8000`.

## How to Add a New Agent

This section provides instructions for adding new agents to the project, covering both automated and manual methods.

#### Automated Method (Recommended)

This method leverages the `a2av3.sh` script and the dashboard's agent wizard for a streamlined agent creation and configuration process.

1.  **Using the Dashboard Agent Wizard:**
    *   Start the A2A demo environment by running `./a2av3.sh`. This script will launch the main UI (dashboard) and any pre-configured agents.
    *   Access the dashboard (usually at `http://localhost:8000` or as configured).
    *   Navigate to the "Agent Wizard" section within the dashboard. This new feature allows you to add and configure new agents interactively.
    *   Follow the on-screen prompts to define your new agent's properties, such as name, description, and initial configuration. The wizard will handle the underlying file creation and configuration updates automatically, simplifying the agent creation process.

2.  **Using the `a2av3.sh` script for agent management:**
    *   The `a2av3.sh` script is designed to simplify the startup and management of agents. It automatically handles port assignments and ensures a clean start by killing existing processes on designated ports.
    *   While the dashboard wizard automates much of the setup, `a2av3.sh` is the primary script for launching your A2A environment. It ensures that the dashboard and any agents (including those configured via the wizard) are started correctly. You can review the `AGENT_COMMANDS` array within `a2av3.sh` to see how agents are launched, but for new agent creation, the dashboard wizard is the recommended starting point.

#### Manual Method

If you prefer to manually configure your agent or need to perform advanced customizations, follow these steps:

1.  **Create a New Agent Directory**: Navigate to `samples/python/agents/` and create a new directory for your agent (e.g., `my_new_agent`).

    ```bash
    mkdir -p samples/python/agents/my_new_agent
    ```

2.  **Copy Template Files**: Copy the contents of an existing simple agent (e.g., `helloworld` or `coder`) into your new agent's directory.

    ```bash
    cp samples/python/agents/helloworld/* samples/python/agents/my_new_agent/
    ```

3.  **Update `pyproject.toml`**: Open `samples/python/agents/my_new_agent/pyproject.toml` and update the `name` and `description` fields to reflect your new agent.

    ```toml
    [project]
    name = "my_new_agent"
    description = "A description of what your new agent does"
    # ... other fields
    ```

4.  **Modify Agent Logic (`__main__.py`, `agent_executor.py`)**: Implement your agent's specific logic in `samples/python/agents/my_new_agent/__main__.py` and `samples/python/agents/my_new_agent/agent_executor.py`. Remember to:

    -   Update the `AgentCard` details (name, description, skills, URL) in `__main__.py`.
    -   Ensure the `uvicorn.run` call in `__main__.py` is correctly configured to expose your agent as an ASGI application (e.g., `app = server.build()` and `uvicorn.run(app, ...)`).
    -   Implement the `execute` method in `agent_executor.py` to define your agent's behavior.

    **Important Security Note**: If your agent executes code or interacts with external systems, ensure you implement robust security measures, including proper sandboxing and input validation. The `coder` agent's `_execute_code` method is for demonstration purposes only and is **not secure for production environments**.

5.  **Install Agent Dependencies**: From the project root, install your new agent's dependencies:

    ```bash
    pip install -e samples/python/agents/my_new_agent
    ```

6.  **Update `a2av3.sh`**: Open `a2av3.sh` in the project root and add your new agent to the `AGENT_PORTS` and `AGENT_COMMANDS` arrays. Choose a unique port for your agent.

    ```bash
    # ... existing agents
    declare -a AGENT_PORTS=(8000 10002 12111 12200)
    declare -a AGENT_COMMANDS=(
      # ... existing commands
      "python -m uvicorn samples/python/agents/my_new_agent.__main__:app --host 0.0.0.0 --port <YOUR_NEW_AGENT_PORT>"
    )
    ```

7.  **Test Your Agent**: Run the `a2av3.sh` script from your terminal to start all agents, including your new one. You can then use the `a2a-cli` or the UI to interact with it.

    ```bash
    ./a2av3.sh
    ```
