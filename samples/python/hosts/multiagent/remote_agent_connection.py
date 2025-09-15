import traceback

from collections.abc import Callable

from a2a.client import (
    Client,
    ClientFactory,
)
from a2a.types import (
    AgentCard,
    Message,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)


TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]


class RemoteAgentConnection:
    """A class to hold the connections to the remote agents."""

    def __init__(self, url: str, http_client, task_callback: TaskUpdateCallback, agent_card: AgentCard | None = None):
        self.url = url
        self.agent_client: Client = ClientFactory(http_client).create(agent_card if agent_card else url)
        self.card: AgentCard = agent_card if agent_card else self.agent_client.agent_card
        self.pending_tasks = set()
        self.task_callback = task_callback

    def get_agent(self) -> AgentCard:
        return self.card

    async def send_message(self, message: Message) -> Task | Message | None:
        lastTask: Task | None = None
        try:
            async for event in self.agent_client.send_message(message):
                if isinstance(event, Message):
                    return event
                if self.is_terminal_or_interrupted(event[0]):
                    return event[0]
                lastTask = event[0]
        except Exception as e:
            print('Exception found in send_message')
            traceback.print_exc()
            raise e
        return lastTask

    def is_terminal_or_interrupted(self, task: Task) -> bool:
        return task.status.state in [
            TaskState.completed,
            TaskState.canceled,
            TaskState.failed,
            TaskState.input_required,
            TaskState.unknown,
        ]

    async def get_task_status(self, task_id: str, session_id: str) -> str:
        # This is a placeholder. In a real scenario, you'd query the remote agent for task status.
        return f"Status for task {task_id} in session {session_id}: Unknown"

    async def cancel_task(self, task_id: str, session_id: str) -> str:
        # This is a placeholder. In a real scenario, you'd send a cancel request to the remote agent.
        return f"Cancellation for task {task_id} in session {session_id}: Not supported"