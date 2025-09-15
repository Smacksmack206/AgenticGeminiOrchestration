import io
import contextlib
import subprocess
import sys

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message, get_text_parts

class CoderAgent:
    """Coder Agent."""

    async def invoke(self, query: str) -> str:
        if query.startswith("write"):
            return "```python\nprint('Hello from the Coder Agent!')\n```"
        elif query.startswith("execute"):
            code_to_execute = query.replace("execute", "").strip()
            if not code_to_execute:
                return "Please provide code to execute after 'execute'."
            return self._execute_code(code_to_execute)
        else:
            return "I can write and execute code. What would you like me to do?"

    def _execute_code(self, code: str) -> str:
        # This is a very basic and INSECURE way to execute code.
        # DO NOT use this in a production environment without proper sandboxing.
        try:
            # Use subprocess to run the code in a separate Python interpreter
            # This provides some isolation but is not a full sandbox.
            process = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=5  # Add a timeout to prevent infinite loops
            )
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            output = ""
            if stdout:
                output += f"Stdout:\n{stdout}\n"
            if stderr:
                output += f"Stderr:\n{stderr}\n"
            if process.returncode != 0:
                output += f"Exited with code: {process.returncode}\n"
            
            if not output:
                output = "Execution completed with no output."

            return f"Code executed.\n{output}"
        except subprocess.TimeoutExpired:
            return "Code execution timed out."
        except Exception as e:
            return f"An error occurred during code execution: {e}"


class CoderAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = CoderAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = get_text_parts(context.message.parts)[0] if context.message.parts else ""
        result = await self.agent.invoke(query)
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')