import mesop as me

from demo.ui.components.conversation import conversation
from demo.ui.components.header import header
from demo.ui.components.page_scaffold import page_scaffold, page_frame
from demo.ui.state.state import AppState


def conversation_page(app_state: AppState):
    """Conversation Page"""
    state = me.state(AppState)
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Conversation', 'chat'):
                pass
            conversation()
