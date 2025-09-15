# Agent2Agent (A2A) Samples

<a href="https://studio.firebase.google.com/new?template=https%3A%2F%2Fgithub.com%2Fa2aproject%2Fa2a-samples%2Ftree%2Fmain%2F.firebase-studio">
  <picture>
    <source
      media="(prefers-color-scheme: dark)"
      srcset="https://cdn.firebasestudio.dev/btn/try_light_20.svg">
    <source
      media="(prefers-color-scheme: light)"
      srcset="https://cdn.firebasestudio.dev/btn/try_dark_20.svg">
    <img
      height="20"
      alt="Try in Firebase Studio"
      src="https://cdn.firebasestudio.dev/btn/try_blue_20.svg">
  </picture>
</a>

<div style="text-align: right;">
  <details>
    <summary>🌐 Language</summary>
    <div style="text-align: center;">
      <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=en">English</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=zh-CN">简体中文</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=zh-TW">繁體中文</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=ja">日本語</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=ko">한국어</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=hi">हिन्दी</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=th">ไทย</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=fr">Français</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=de">Deutsch</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=es">Español</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=it">Italiano</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=ru">Русский</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=pt">Português</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=nl">Nederlands</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=pl">Polski</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=ar">العربية</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=fa">فارسی</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=tr">Türkçe</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=vi">Tiếng Việt</a>
      | <a href="https://openaitx.github.io/view.html?user=a2aproject&project=a2a-samples&lang=id">Bahasa Indonesia</a>
    </div>
  </details>
</div>

This repository contains code samples and demos which use the [Agent2Agent (A2A) Protocol](https://goo.gle/a2a).

## Related Repositories

- [A2A](https://github.com/a2aproject/A2A) - A2A Specification and documentation.
- [a2a-python](https://github.com/a2aproject/a2a-python) - A2A Python SDK.
- [a2a-inspector](https://github.com/a2aproject/a2a-inspector) - UI tool for inspecting A2A enabled agents.

## Project Customizations and Adding New Agents

This section outlines recent changes made to improve the user experience (UX) and provides instructions on how to add new agents to this project.

### UX Improvements and Script Refactoring

To streamline the process of starting and managing multiple agents, the `a2a_demo.sh` script has been refactored. Key improvements include:

-   **Centralized Agent Management**: Agent ports and their respective startup commands are now defined in arrays (`AGENT_PORTS` and `AGENT_COMMANDS`) at the top of the `a2a_demo.sh` script. This makes it easier to see and modify which agents are started.
-   **Clean Start**: The script now automatically identifies and kills any processes running on the defined agent ports before starting new ones. This ensures a clean environment and avoids port conflicts.
-   **Simplified Execution**: The script now ensures it always runs from the project root, resolving issues with relative paths and virtual environment activation.

### How to Add a New Agent

Follow these steps to add a new Python agent to the project:

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

6.  **Update `a2a_demo.sh`**: Open `a2a_demo.sh` in the project root and add your new agent to the `AGENT_PORTS` and `AGENT_COMMANDS` arrays. Choose a unique port for your agent.

    ```bash
    # ... existing agents
    declare -a AGENT_PORTS=(8000 10002 12111 12200)
    declare -a AGENT_COMMANDS=(
      # ... existing commands
      "python -m uvicorn samples.python.agents.my_new_agent.__main__:app --host 0.0.0.0 --port <YOUR_NEW_AGENT_PORT>"
    )
    ```

7.  **Test Your Agent**: Run the `a2a` alias from your terminal to start all agents, including your new one. You can then use the `a2a-cli` or the UI to interact with it.

    ```bash
    a2a
    ```

## Contributing

Contributions welcome! See the [Contributing Guide](CONTRIBUTING.md).

## Getting help

Please use the [issues page](https://github.com/a2aproject/a2a-samples/issues) to provide suggestions, feedback or submit a bug report.

## Disclaimer

This repository itself is not an officially supported Google product. The code in this repository is for demonstrative purposes only.

Important: The sample code provided is for demonstration purposes and illustrates the mechanics of the Agent-to-Agent (A2A) protocol. When building production applications, it is critical to treat any agent operating outside of your direct control as a potentially untrusted entity.

All data received from an external agent—including but not limited to its AgentCard, messages, artifacts, and task statuses—should be handled as untrusted input. For example, a malicious agent could provide an AgentCard containing crafted data in its fields (e.g., description, name, skills.description). If this data is used without sanitization to construct prompts for a Large Language Model (LLM), it could expose your application to prompt injection attacks.  Failure to properly validate and sanitize this data before use can introduce security vulnerabilities into your application.

Developers are responsible for implementing appropriate security measures, such as input validation and secure handling of credentials to protect their systems and users.
