from demo.ui.components.header import header
from demo.ui.components.page_scaffold import page_frame, page_scaffold
from demo.ui.components.task_card import task_card
from demo.ui.state.state import AppState


def task_list_page(app_state: AppState):
    """Task List Page"""
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Task List', 'task'):
                pass
            task_card(app_state.task_list)
