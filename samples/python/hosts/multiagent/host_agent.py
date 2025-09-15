import asyncio
import base64
import datetime
import json
import os
import uuid

import httpx

from a2a.types import (
    AgentCard,
    Artifact,
    DataPart,
    FilePart,
    FileWithBytes,
    FileWithUri,
    Message,
    Part,
    Role,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events.event import Event as ADKEvent
from google.adk.events.event_actions import EventActions as ADKEventActions
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from samples.python.hosts.multiagent.remote_agent_connection import RemoteAgentConnection, TaskCallbackArg
from demo.ui.utils.agent_card import get_agent_card


class HostAgent:
    """Host Agent."""

    def __init__(
        self,
        remote_agent_urls: list[str],
        http_client: httpx.AsyncClient,
        task_callback: TaskCallbackArg,
    ):
        self._remote_agent_urls = remote_agent_urls
        self._remote_agents: list[RemoteAgentConnection] = []
        self._http_client = http_client
        self._task_callback = task_callback
        self._initialize_remote_agents()

    def _initialize_remote_agents(self):
        for url in self._remote_agent_urls:
            self._remote_agents.append(
                RemoteAgentConnection(url, self._http_client, self._task_callback)
            )

    def create_agent(self) -> LlmAgent:
        """Creates the LLM agent for the host agent."""
        LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini/gemini-2.0-flash-001')
        return LlmAgent(
            model=LiteLlm(model=LITELLM_MODEL),
            name='host_agent',
            description='Host agent that can communicate with other agents.',
            instruction="""
    You are a host agent that can communicate with other agents.
    You can use the following tools to communicate with other agents:
    - send_message: Send a message to a remote agent.
    - get_task_status: Get the status of a task from a remote agent.
    - cancel_task: Cancel a task from a remote agent.
    """,
            tools=[
                self.send_message,
                self.get_task_status,
                self.cancel_task,
            ],
        )

    def register_agent_card(self, agent_card: AgentCard):
        self._remote_agents.append(
            RemoteAgentConnection(agent_card.url, self._http_client, self._task_callback, agent_card)
        )

    async def send_message(
        self,
        message: str,
        remote_agent_url: str,
        session_id: str,
        task_id: str | None = None,
    ) -> str:
        """Sends a message to a remote agent.

        Args:
            message: The message to send.
            remote_agent_url: The URL of the remote agent.
            session_id: The session ID.
            task_id: The task ID.

        Returns:
            The response from the remote agent.
        """
        agent = self._get_remote_agent(remote_agent_url)
        if not agent:
            return f'Error: Remote agent {remote_agent_url} not found.'
        response = await agent.send_message(message, session_id, task_id)
        return response

    async def get_task_status(
        self,
        task_id: str,
        remote_agent_url: str,
        session_id: str,
    ) -> str:
        """Gets the status of a task from a remote agent.

        Args:
            task_id: The ID of the task.
            remote_agent_url: The URL of the remote agent.
            session_id: The session ID.

        Returns:
            The status of the task.
        """
        agent = self._get_remote_agent(remote_agent_url)
        if not agent:
            return f'Error: Remote agent {remote_agent_url} not found.'
        response = await agent.get_task_status(task_id, session_id)
        return response

    async def cancel_task(
        self,
        task_id: str,
        remote_agent_url: str,
        session_id: str,
    ) -> str:
        """Cancels a task from a remote agent.

        Args:
            task_id: The ID of the task.
            remote_agent_url: The URL of the remote agent.
            session_id: The session ID.

        Returns:
            The status of the cancellation.
        """
        agent = self._get_remote_agent(remote_agent_url)
        if not agent:
            return f'Error: Remote agent {remote_agent_url} not found.'
        response = await agent.cancel_task(task_id, session_id)
        return response

    def _get_remote_agent(self, url: str) -> RemoteAgentConnection | None:
        return next((agent for agent in self._remote_agents if agent.url == url), None)
