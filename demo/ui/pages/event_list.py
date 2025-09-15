import mesop as me

from demo.ui.components.event_viewer import event_list
from demo.ui.components.header import header
from demo.ui.components.page_scaffold import page_frame, page_scaffold
from demo.ui.state.agent_state import AgentState
from demo.ui.state.state import AppState


def event_list_page(app_state: AppState):
    """Agents List Page"""
    state = me.state(AgentState)
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Event List', 'list'):
                pass
            event_list()
