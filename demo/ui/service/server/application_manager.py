from abc import ABC, abstractmethod

from a2a.types import AgentCard, Message, Task

from demo.ui.service.types import Conversation, Event


class ApplicationManager(ABC):
    @abstractmethod
    def create_conversation(self) -> Conversation:
        pass

    @abstractmethod
    def delete_conversation(self, conversation_id: str) -> bool:
        pass

    @abstractmethod
    def sanitize_message(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def process_message(self, message: Message):
        pass

    @abstractmethod
    def register_agent(self, url: str):
        pass

    @abstractmethod
    def get_pending_messages(self) -> list[tuple[str, str]]:
        pass

    @abstractmethod
    def get_conversation(
        self, conversation_id: str | None
    ) -> Conversation | None:
        pass

    @property
    @abstractmethod
    def conversations(self) -> list[Conversation]:
        pass

    @property
    @abstractmethod
    def tasks(self) -> list[Task]:
        pass

    @property
    @abstractmethod
    def agents(self) -> list[AgentCard]:
        pass

    @property
    @abstractmethod
    def events(self) -> list[Event]:
        pass
