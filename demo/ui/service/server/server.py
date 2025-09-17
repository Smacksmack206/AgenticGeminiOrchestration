import asyncio
import base64
import os
import threading
import uuid

from typing import cast

import httpx

from a2a.types import FilePart, FileWithUri, Message, Part, Role
from fastapi import FastAPI, Request, Response

from ..types import (
    CreateConversationResponse,
    DeleteConversationResponse,
    GetEventResponse,
    ListAgentResponse,
    ListConversationResponse,
    ListMessageResponse,
    ListTaskResponse,
    MessageInfo,
    PendingMessageResponse,
    RegisterAgentResponse,
    SendMessageResponse,
    UnregisterAgentRequest,
    UnregisterAgentResponse,
)

from .adk_host_manager import ADKHostManager, get_message_id
from .application_manager import ApplicationManager
from .in_memory_manager import InMemoryFakeAgentManager


class ConversationServer:
    """ConversationServer is the backend to serve the agent interactions in the UI

    This defines the interface that is used by the Mesop system to interact with
    agents and provide details about the executions.
    """

    def __init__(self, app: FastAPI, http_client: httpx.AsyncClient):
        self._app = app
        self._http_client = http_client
        self._api_key = os.environ.get('GOOGLE_API_KEY', '')
        self._uses_vertex_ai = (
            os.environ.get('GOOGLE_GENAI_USE_VERTEXAI', '').upper() == 'TRUE'
        )

        self.manager: ApplicationManager = None

        self._file_cache = {}  # dict[str, FilePart] maps file id to message data
        self._message_to_cache = {}  # dict[str, str] maps message id to cache id

        app.add_api_route(
            '/conversation/create', self._create_conversation, methods=['POST']
        )
        app.add_api_route(
            '/conversation/delete', self._delete_conversation, methods=['POST']
        )
        app.add_api_route(
            '/conversation/list', self._list_conversation, methods=['POST']
        )
        app.add_api_route('/message/send', self._send_message, methods=['POST'])
        app.add_api_route('/events/get', self._get_events, methods=['POST'])
        app.add_api_route(
            '/message/list', self._list_messages, methods=['POST']
        )
        app.add_api_route(
            '/message/pending', self._pending_messages, methods=['POST']
        )
        app.add_api_route('/task/list', self._list_tasks, methods=['POST'])
        app.add_api_route(
            '/agent/register', self._register_agent, methods=['POST']
        )
        app.add_api_route('/agent/list', self._list_agents, methods=['POST'])
        app.add_api_route(
            '/agent/unregister', self._unregister_agent, methods=['POST']
        )
        app.add_api_route(
            '/message/file/{file_id}', self._files, methods=['GET']
        )
        app.add_api_route(
            '/api_key/update', self._update_api_key, methods=['POST']
        )

    async def initialize_manager(self):
        agent_manager = os.environ.get('A2A_HOST', 'ADK')

        if agent_manager.upper() == 'ADK':
            print(f"🔵 SERVER: Creating ADKHostManager")
            self.manager = ADKHostManager(
                self._http_client,
                api_key=self._api_key,
                uses_vertex_ai=self._uses_vertex_ai,
            )
            print(f"🔵 SERVER: Calling async_init")
            await self.manager.async_init()
            print(f"🔵 SERVER: async_init completed")
        else:
            self.manager = InMemoryFakeAgentManager()
        if isinstance(self.manager, ADKHostManager):
            self.manager.update_api_key(self._api_key)

    async def _create_conversation(self):
        c = await self.manager.create_conversation()
        return CreateConversationResponse(result=c)

    async def _delete_conversation(self, request: Request):
        message_data = await request.json()
        conversation_id = message_data['params']
        success = await self.manager.delete_conversation(conversation_id)
        return DeleteConversationResponse(result=success)

    async def _send_message(self, request: Request):
        message_data = await request.json()
        params = message_data['params']
        if isinstance(params.get("role"), str):
            params["role"] = Role(params["role"])
        message = Message(**params)
        message = self.manager.sanitize_message(message)
        loop = asyncio.get_event_loop()
        if isinstance(self.manager, ADKHostManager):
            t = threading.Thread(
                target=lambda: cast(
                    'ADKHostManager', self.manager
                ).process_message_threadsafe(message, loop)
            )
        else:
            t = threading.Thread(
                target=lambda: asyncio.run(
                    self.manager.process_message(message)
                )
            )
        t.start()
        return SendMessageResponse(
            result=MessageInfo(
                message_id=message.message_id,
                context_id=message.context_id if message.context_id else '',
            )
        )

    async def _list_messages(self, request: Request):
        message_data = await request.json()
        conversation_id = message_data['params']
        conversation = self.manager.get_conversation(conversation_id)
        if conversation:
            return ListMessageResponse(
                result=self.cache_content(conversation.messages)
            )
        return ListMessageResponse(result=[])

    def cache_content(self, messages: list[Message]):
        rval = []
        for m in messages:
            message_id = get_message_id(m)
            if not message_id:
                rval.append(m)
                continue
            new_parts: list[Part] = []
            for i, p in enumerate(m.parts):
                part = p.root
                if part.kind != 'file':
                    new_parts.append(p)
                    continue
                message_part_id = f'{message_id}:{i}'
                if message_part_id in self._message_to_cache:
                    cache_id = self._message_to_cache[message_part_id]
                else:
                    cache_id = str(uuid.uuid4())
                    self._message_to_cache[message_part_id] = cache_id
                # Replace the part data with a url reference
                new_parts.append(
                    Part(
                        root=FilePart(
                            file=FileWithUri(
                                mime_type=part.file.mime_type,
                                uri=f'/message/file/{cache_id}',
                            )
                        )
                    )
                )
                if cache_id not in self._file_cache:
                    self._file_cache[cache_id] = part
            m.parts = new_parts
            rval.append(m)
        return rval

    async def _pending_messages(self):
        return PendingMessageResponse(
            result=self.manager.get_pending_messages()
        )

    def _list_conversation(self):
        return ListConversationResponse(result=self.manager.conversations)

    def _get_events(self):
        return GetEventResponse(result=self.manager.events)

    def _list_tasks(self):
        return ListTaskResponse(result=self.manager.tasks)

    async def _register_agent(self, request: Request):
        message_data = await request.json()
        url = message_data['params']
        await self.manager.register_agent(url)
        return RegisterAgentResponse()

    async def _unregister_agent(self, request: Request):
        message_data = await request.json()
        url = message_data['params']
        success = await self.manager.unregister_agent(url)
        return UnregisterAgentResponse(result=success)

    async def _list_agents(self):
        return ListAgentResponse(result=self.manager.agents)

    def _files(self, file_id):
        if file_id not in self._file_cache:
            raise Exception('file not found')
        part = self._file_cache[file_id]
        if 'image' in part.file.mime_type:
            return Response(
                content=base64.b64decode(part.file.bytes),
                media_type=part.file.mime_type,
            )
        return Response(content=part.file.bytes, media_type=part.file.mime_type)

    async def _update_api_key(self, request: Request):
        """Update the API key"""
        try:
            data = await request.json()
            api_key = data.get('api_key', '')

            if api_key:
                # Update in the manager
                self.update_api_key(api_key)
                return {'status': 'success'}
            return {'status': 'error', 'message': 'No API key provided'}
        except Exception as e:
            print(e)
            return {'status': 'error', 'message': str(e)}
