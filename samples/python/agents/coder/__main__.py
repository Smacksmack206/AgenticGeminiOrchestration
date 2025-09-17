import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from samples.python.agents.coder.agent_executor import (
    CoderAgentExecutor,  # type: ignore[import-untyped]
)

skill = AgentSkill(
    id='coder',
    name='Writes and executes code',
    description='Can write and execute code in a sandboxed environment.',
    tags=['coding', 'development'],
    examples=['write a python script to print hello world', 'execute the previous script'],
)

public_agent_card = AgentCard(
    name='Coder Agent',
    description='An agent that can write and execute code.',
    url='http://localhost:12111',
    version='1.0.0',
    default_input_modes=['text'],
    default_output_modes=['text'],
    capabilities=AgentCapabilities(streaming=True),
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=CoderAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

# Create the A2AStarletteApplication instance
a2a_app = A2AStarletteApplication(
    agent_card=public_agent_card,
    http_handler=request_handler,
).build() # Build the Starlette app from A2AStarletteApplication

# Create a FastAPI app
app = FastAPI()

# Mount the A2A application at the root path
app.mount("/", a2a_app)

# Add the agent-card.json route to the FastAPI app
@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    return JSONResponse(content=public_agent_card.model_dump_json())

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=12111)