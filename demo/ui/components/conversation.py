import uuid

import mesop as me

from a2a.types import Message, Part, Role, TextPart
from demo.ui.state.host_agent_service import (
    ListConversations,
    SendMessage,
    convert_message_to_state,
)
from demo.ui.state.state import AppState, StateMessage

from demo.ui.components.chat_bubble import chat_bubble
from demo.ui.components.form_render import form_sent, is_form, render_form


@me.stateclass
class PageState:
    """Local Page State"""

    conversation_id: str = ''
    message_content: str = ''


def on_blur(e: me.InputBlurEvent):
    """Input handler"""
    state = me.state(PageState)
    state.message_content = e.value


async def send_message(message: str, message_id: str = ''):
    state = me.state(PageState)
    app_state = me.state(AppState)
    c = next(
        (
            x
            for x in await ListConversations()
            if x.conversation_id == state.conversation_id
        ),
        None,
    )
    if not c:
        print('Conversation id ', state.conversation_id, ' not found')
    request = Message(
        message_id=message_id,
        context_id=state.conversation_id,
        role=Role.user,
        parts=[Part(root=TextPart(text=message))],
    )
    # Add message to state until refresh replaces it.
    state_message = convert_message_to_state(request)
    if not app_state.messages:
        app_state.messages = []
    app_state.messages.append(state_message)
    conversation = next(
        filter(
            lambda x: c and x.conversation_id == c.conversation_id,
            app_state.conversations,
        ),
        None,
    )
    if conversation:
        conversation.message_ids.append(state_message.message_id)
    await SendMessage(request)


async def send_message_enter(e: me.InputEnterEvent):  # pylint: disable=unused-argument
    """Send message handler"""
    yield
    state = me.state(PageState)
    state.message_content = e.value
    app_state = me.state(AppState)
    message_id = str(uuid.uuid4())
    app_state.background_tasks[message_id] = ''
    yield
    await send_message(state.message_content, message_id)
    yield


async def send_message_button(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Send message button handler"""
    yield
    state = me.state(PageState)
    app_state = me.state(AppState)
    message_id = str(uuid.uuid4())
    app_state.background_tasks[message_id] = ''
    await send_message(state.message_content, message_id)
    yield


@me.component
def conversation():
    """Conversation component"""
    page_state = me.state(PageState)
    app_state = me.state(AppState)
    if 'conversation_id' in me.query_params:
        page_state.conversation_id = me.query_params['conversation_id']
        app_state.current_conversation_id = page_state.conversation_id
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='space-between',
            flex_direction='column',
        )
    ):
        for message in app_state.messages:
            if is_form(message):
                render_form(message, app_state)
            elif form_sent(message, app_state):
                chat_bubble(
                    StateMessage(
                        message_id=message.message_id,
                        role=message.role,
                        content=[('Form submitted', 'text/plain')],
                    ),
                    message.message_id,
                )
            else:
                chat_bubble(message, message.message_id)

        # Modern input area with beautiful styling
        with me.box(
            style=me.Style(
                position='sticky',
                bottom=0,
                background='white',
                padding=me.Padding(top=20, bottom=20, left=20, right=20),
                box_shadow='0 -4px 20px rgba(0, 0, 0, 0.1)',
                # border_top not supported in Mesop Style
            )
        ):
            with me.box(
                style=me.Style(
                    display='flex',
                    align_items='center',
                    gap=12,
                    max_width='800px',
                    # margin='0 auto' not supported in Mesop
                )
            ):
                me.input(
                    label='Type your message...',
                    on_blur=on_blur,
                    on_enter=send_message_enter,
                    style=me.Style(
                        flex_grow=1,
                        border_radius=25,
                        padding=me.Padding(top=12, bottom=12, left=20, right=20),
                        # border not supported in Mesop Style
                        font_size='16px',
                        background='#f9fafb',
                    ),
                )
                
                # Modern send button
                with me.content_button(
                    type='raised',
                    on_click=send_message_button,
                    style=me.Style(
                        background='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color='white',
                        border_radius=25,
                        padding=me.Padding(top=12, bottom=12, left=12, right=12),
                        box_shadow='0 4px 12px rgba(102, 126, 234, 0.4)',
                        min_width=50,
                        height=50,
                    ),
                ):
                    me.icon(
                        icon='send',
                        style=me.Style(
                            font_size='20px',
                        )
                    )
