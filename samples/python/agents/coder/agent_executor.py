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
        query_lower = query.lower()
        if query_lower.startswith("write"):
            # Handle requests to write code
            if "hello world" in query_lower:
                if "python" in query_lower and "rust" in query_lower:
                    return """🐍 **Python Hello World:**
```python
print("Hello, World!")
```

🦀 **Rust Hello World:**
```rust
fn main() {
    println!("Hello, World!");
}
```

📊 **Key Differences:**

1. **Syntax**: Python uses `print()` function, Rust uses `println!()` macro
2. **Structure**: Rust requires a `main()` function as entry point, Python executes top-level code
3. **Compilation**: Python is interpreted, Rust is compiled
4. **Type System**: Python is dynamically typed, Rust is statically typed
5. **Memory Management**: Python has garbage collection, Rust uses ownership system
6. **Performance**: Rust typically runs faster due to compilation and zero-cost abstractions
7. **Semicolons**: Rust requires semicolons, Python doesn't
8. **Macros**: Rust `println!` is a macro (note the `!`), Python `print` is a function"""
                elif "python" in query_lower:
                    return "🐍 **Python Hello World:**\n```python\nprint('Hello, World!')\n```"
                elif "rust" in query_lower:
                    return "🦀 **Rust Hello World:**\n```rust\nfn main() {\n    println!(\"Hello, World!\");\n}\n```"
            return "💻 **Code Example:**\n```python\nprint('Hello from the Coder Agent!')\n```"
        elif query_lower.startswith("execute"):
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

            return f"⚡ **Code Execution Result:**\n{output}"
        except subprocess.TimeoutExpired:
            return "⏱️ **Execution Timeout:** Code execution timed out (5 second limit)."
        except Exception as e:
            return f"❌ **Execution Error:** {e}"


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
