import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import uuid

from google.adk.sessions.in_memory_session_service import Session as ADKSession
from google.adk.events.event import Event as ADKEvent


class FileBasedSessionService:
    """A session service that persists sessions to a JSON file."""

    def __init__(self, file_path: str = "sessions.json"):
        self.file_path = file_path
        self._sessions: Dict[str, ADKSession] = {}
        self._load_sessions()

    def _load_sessions(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                try:
                    data = json.load(f)
                    for session_data in data:
                        # Reconstruct ADKSession objects
                        session = ADKSession(
                            app_name=session_data["app_name"],
                            user_id=session_data["user_id"],
                            id=session_data["id"],
                            events=[ADKEvent(**e) for e in session_data["events"]]
                        )
                        self._sessions[session.id] = session
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {self.file_path}. Starting with empty sessions.")
        print(f"Loaded {len(self._sessions)} sessions from {self.file_path}")

    def _save_sessions(self):
        with open(self.file_path, "w") as f:
            # Convert ADKSession objects to dictionaries for JSON serialization
            serializable_sessions = []
            for session in self._sessions.values():
                serializable_events = [e.model_dump() for e in session.events] # Assuming ADKEvent has model_dump
                serializable_sessions.append({
                    "app_name": session.app_name,
                    "user_id": session.user_id,
                    "id": session.id,
                    "events": serializable_events
                })
            json.dump(serializable_sessions, f, indent=2)
        print(f"Saved {len(self._sessions)} sessions to {self.file_path}")

    async def create_session(self, app_name: str, user_id: str) -> ADKSession:
        session_id = str(uuid.uuid4())
        session = ADKSession(app_name=app_name, user_id=user_id, id=session_id, events=[])
        self._sessions[session_id] = session
        self._save_sessions()
        return session

    async def delete_session(self, app_name: str, user_id: str, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save_sessions()
            return True
        return False

    async def list_sessions(self, app_name: str, user_id: str) -> List[ADKSession]:
        return [s for s in self._sessions.values() if s.app_name == app_name and s.user_id == user_id]

    async def get_session(self, app_name: str, user_id: str, session_id: str) -> Optional[ADKSession]:
        session = self._sessions.get(session_id)
        if session and session.app_name == app_name and session.user_id == user_id:
            return session
        return None

    async def append_event(self, session: ADKSession, event: ADKEvent):
        if session.id in self._sessions:
            self._sessions[session.id].events.append(event)
            self._save_sessions()
        else:
            print(f"Warning: Session {session.id} not found when trying to append event.")
