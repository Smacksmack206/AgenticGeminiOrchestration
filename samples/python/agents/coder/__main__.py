import uvicorn

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
    url='http://localhost:12111/',
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

server = A2AStarletteApplication(
    agent_card=public_agent_card,
    http_handler=request_handler,
)

app = server.build()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=12111)
