import mesop as me

from demo.ui.state.host_agent_service import DeleteRemoteAgent


@me.stateclass
class AgentState:
    """Agents List State"""

    agent_dialog_open: bool = False
    agent_address: str = ''
    agent_name: str = ''
    agent_description: str = ''
    input_modes: list[str]
    output_modes: list[str]
    extensions: list[str]
    stream_supported: bool = False
    push_notifications_supported: bool = False
    error: str = ''
    agent_framework_type: str = ''

    async def delete_agent(self, agent_address: str):
        success = await DeleteRemoteAgent(agent_address)
        if not success:
            self.error = f"Failed to delete agent: {agent_address}"
        self.error = ''
