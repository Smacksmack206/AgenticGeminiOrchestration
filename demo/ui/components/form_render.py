import mesop as me

from a2a.types import DataPart, Message, Part, Role, TextPart
from demo.ui.state.host_agent_service import SendMessage
from demo.ui.state.state import AppState, StateMessage


def is_form(message: StateMessage) -> bool:
    """Returns true if the message is a form."""
    if not message.content:
        return False
    for part in message.content:
        if part[1] == 'form':
            return True
    return False


def form_sent(message: StateMessage, app_state: AppState) -> bool:
    """Returns true if the form has been sent."""
    return message.message_id in app_state.form_responses


@me.component
def render_form(message: StateMessage, app_state: AppState):
    """Render a form from a message."""
    if not message.content:
        return
    for part in message.content:
        if part[1] == 'form':
            form_data = part[0]
            with me.box(style=me.Style(margin=me.Margin(bottom=10))):
                me.text(form_data['instructions'])
            with me.form(on_submit=lambda e: on_submit_form(e, message)):
                for key, value in form_data['form']['properties'].items():
                    with me.box(style=me.Style(margin=me.Margin(bottom=10))):
                        me.input(
                            label=value['title'],
                            name=key,
                            value=form_data['form_data'].get(key, ''),
                        )
                me.button('Submit', type='submit')


async def on_submit_form(e: me.ClickEvent, message: StateMessage):
    """Submit form handler."""
    app_state = me.state(AppState)
    app_state.form_responses[message.message_id] = 'submitted'
    # Update the completed forms
    app_state.completed_forms[message.message_id] = e.json
    # Send the message to the agent
    request = Message(
        message_id=str(uuid.uuid4()),
        context_id=message.context_id,
        role=Role.user,
        parts=[
            Part(
                root=DataPart(
                    data={
                        'type': 'form_response',
                        'form_response': e.json,
                        'original_message_id': message.message_id,
                    }
                )
            )
        ],
    )
    await SendMessage(request)
    yield
