import mesop as me
import pandas as pd

from demo.ui.state.host_agent_service import CreateConversation, DeleteConversation, UpdateAppState
from demo.ui.state.state import AppState, StateConversation


@me.stateclass
class DeleteState:
    """State to track which conversation to delete"""
    conversation_to_delete: str = ''


def mark_for_delete(e: me.ClickEvent, conversation_id: str):  # pylint: disable=unused-argument
    """Mark conversation for deletion"""
    delete_state = me.state(DeleteState)
    delete_state.conversation_to_delete = conversation_id
    yield





def cancel_delete(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Cancel the delete operation"""
    delete_state = me.state(DeleteState)
    delete_state.conversation_to_delete = ''
    yield


async def confirm_delete(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Confirm and execute the delete"""
    delete_state = me.state(DeleteState)
    conversation_id = delete_state.conversation_to_delete
    delete_state.conversation_to_delete = ''  # Clear the dialog
    
    # Perform the actual delete
    success = await DeleteConversation(conversation_id)
    
    if success:
        app_state = me.state(AppState)
        # Re-fetch and update the entire app state to ensure synchronization
        await UpdateAppState(app_state, app_state.current_conversation_id)
        
        if app_state.current_conversation_id == conversation_id:
            app_state.current_conversation_id = ''
            app_state.messages = []
            me.navigate('/')
    
    yield


@me.component
def delete_confirmation_dialog():
    """Confirmation dialog for deleting conversations"""
    delete_state = me.state(DeleteState)
    
    if not delete_state.conversation_to_delete:
        return
    
    # Find the conversation name for display
    app_state = me.state(AppState)
    conversation_name = "this conversation"
    for conv in app_state.conversations:
        if conv.conversation_id == delete_state.conversation_to_delete:
            conversation_name = conv.conversation_name or f"Chat {conv.conversation_id[:8]}"
            break
    
    # Overlay background
    with me.box(
        style=me.Style(
            position='fixed',
            top=0,
            left=0,
            width='100%',
            height='100%',
            background='rgba(0, 0, 0, 0.5)',
            display='flex',
            justify_content='center',
            align_items='center',
            z_index=1000,
        )
    ):
        # Dialog box
        with me.box(
            style=me.Style(
                background='white',
                border_radius=12,
                padding=me.Padding(top=24, bottom=24, left=24, right=24),
                max_width='400px',
                width='90%',
                box_shadow='0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            )
        ):
            # Title
            me.text(
                'Delete Conversation',
                style=me.Style(
                    font_size='20px',
                    font_weight='600',
                    color='#1a1a1a',
                    margin=me.Margin(bottom=12),
                )
            )
            
            # Message
            me.text(
                f'Are you sure you want to delete "{conversation_name}"? This action cannot be undone.',
                style=me.Style(
                    font_size='14px',
                    color='#6b7280',
                    margin=me.Margin(bottom=24),
                )
            )
            
            # Buttons
            with me.box(
                style=me.Style(
                    display='flex',
                    justify_content='flex-end',
                    gap=12,
                )
            ):
                me.button(
                    'Cancel',
                    on_click=cancel_delete,
                    type='flat',
                    style=me.Style(
                        color='#6b7280',
                        padding=me.Padding(top=8, bottom=8, left=16, right=16),
                    )
                )
                
                me.button(
                    'Delete',
                    on_click=confirm_delete,
                    type='raised',
                    style=me.Style(
                        background='#dc2626',
                        color='white',
                        padding=me.Padding(top=8, bottom=8, left=16, right=16),
                    )
                )


@me.component
def conversation_list(conversations: list[StateConversation]):
    """Simple working conversation list with table"""
    
    # Create table data
    df_data = {
        'Name': [],
        'Status': [],
        'Messages': [],
        'ID': [],
    }
    
    for conversation in conversations:
        df_data['Name'].append(conversation.conversation_name or f"Chat {conversation.conversation_id[:8]}")
        df_data['Status'].append('Active' if conversation.is_active else 'Closed')
        df_data['Messages'].append(len(conversation.message_ids))
        df_data['ID'].append(conversation.conversation_id)
    
    df = pd.DataFrame(df_data)
    
    with me.box(
        style=me.Style(
            padding=me.Padding(top=20, bottom=20, left=20, right=20),
        )
    ):
        me.text(
            "Conversations",
            style=me.Style(font_size='24px', font_weight='bold', margin=me.Margin(bottom=20))
        )
        
        # Add conversation button
        me.button(
            'New Conversation',
            on_click=add_conversation,
            type='raised',
            style=me.Style(margin=me.Margin(bottom=20))
        )
        
        # Simple list of conversations with delete buttons
        for i, conversation in enumerate(conversations):
            with me.box(
                style=me.Style(
                    display='flex',
                    justify_content='space-between',
                    align_items='center',
                    padding=me.Padding(top=10, bottom=10, left=10, right=10),
                    margin=me.Margin(bottom=5),
                    background='#f5f5f5',
                    border_radius=5,
                )
            ):
                # Conversation info (clickable)
                with me.box(
                    style=me.Style(flex_grow=1, cursor='pointer'),
                    on_click=lambda e, cid=conversation.conversation_id: navigate_to_conversation(cid)
                ):
                    me.text(
                        conversation.conversation_name or f"Conversation {conversation.conversation_id[:8]}",
                        style=me.Style(font_weight='bold')
                    )
                    me.text(
                        f"Messages: {len(conversation.message_ids)} | Status: {'Active' if conversation.is_active else 'Closed'}",
                        style=me.Style(font_size='14px', color='#666')
                    )
                
                # Delete button
                me.button(
                    'Delete',
                    key=f'delete_btn_{i}',  # Use index as key
                    on_click=lambda e, cid=conversation.conversation_id: mark_for_delete(e, cid),
                    type='flat',
                    style=me.Style(color='red')
                )
        
        # Add confirmation dialog
        delete_confirmation_dialog()





def navigate_to_conversation(conversation_id: str):
    """Navigate to conversation"""
    state = me.state(AppState)
    state.current_conversation_id = conversation_id
    me.navigate('/conversation', query_params={'conversation_id': conversation_id})
    yield


# Removed separate delete_button component - using inline button instead


@me.component
def conversation_card(conversation: StateConversation, index: int):
    """Beautiful conversation card component"""
    app_state = me.state(AppState)
    is_active = app_state.current_conversation_id == conversation.conversation_id
    message_count = len(conversation.message_ids)
    
    # Generate a nice conversation title
    conversation_title = conversation.conversation_name or f"Chat {index + 1}"
    
    # Status styling
    status_color = '#10b981' if conversation.is_active else '#6b7280'
    status_bg = '#ecfdf5' if conversation.is_active else '#483550'
    status_text = 'Active' if conversation.is_active else 'Closed'
    
    with me.box(
        style=me.Style(
            background='white' if not is_active else '#483550',
            border_radius=16,
            padding=me.Padding(top=20, bottom=20, left=24, right=24),
            margin=me.Margin(bottom=12),
            box_shadow='0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.1)' if not is_active else '0 8px 25px rgba(102, 126, 234, 0.15), 0 3px 10px rgba(102, 126, 234, 0.1)',
        ),
    ):
        with me.box(
            style=me.Style(
                display='flex',
                justify_content='space-between',
                align_items='flex-start',
            )
        ):
            # Left side - conversation info (clickable)
            with me.box(
                style=me.Style(
                    flex_grow=1,
                    display='flex',
                    flex_direction='column',
                    gap=8,
                    cursor='pointer',
                ),
                on_click=lambda e: navigate_to_conversation(conversation.conversation_id)
            ):
                # Title and status row
                with me.box(
                    style=me.Style(
                        display='flex',
                        align_items='center',
                        gap=12,
                        margin=me.Margin(bottom=4),
                    )
                ):
                    me.text(
                        conversation_title,
                        style=me.Style(
                            font_size='18px',
                            font_weight='600',
                            color='#1a1a1a',
                            # line_height not supported in Mesop Style
                        )
                    )
                    
                    # Status badge
                    with me.box(
                        style=me.Style(
                            background=status_bg,
                            color=status_color,
                            padding=me.Padding(top=4, bottom=4, left=8, right=8),
                            border_radius=12,
                            font_size='12px',
                            font_weight='500',
                        )
                    ):
                        me.text(status_text)
                
                # Message count and metadata
                with me.box(
                    style=me.Style(
                        display='flex',
                        align_items='center',
                        gap=16,
                    )
                ):
                    with me.box(
                        style=me.Style(
                            display='flex',
                            align_items='center',
                            gap=6,
                        )
                    ):
                        me.icon(
                            icon='chat_bubble_outline',
                            style=me.Style(
                                font_size='16px',
                                color='#6b7280',
                            )
                        )
                        me.text(
                            f"{message_count} message{'s' if message_count != 1 else ''}",
                            style=me.Style(
                                font_size='14px',
                                color='#6b7280',
                                font_weight='400',
                            )
                        )
                    
                    # Conversation ID (shortened)
                    me.text(
                        f"ID: {conversation.conversation_id[:8]}...",
                        style=me.Style(
                            font_size='12px',
                            color='#9ca3af',
                            font_family='monospace',
                        )
                    )
            
            # Right side - actions
            with me.box(
                style=me.Style(
                    display='flex',
                    align_items='center',
                    gap=8,
                )
            ):
                # Delete button - inline without component
                me.button(
                    'DELETE',
                    on_click=lambda e, cid=conversation.conversation_id: mark_for_delete(e, cid),
                    type='raised',
                    style=me.Style(color='red')
                )


async def add_conversation(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Add conversation button handler"""
    response = await CreateConversation()
    me.state(AppState).messages = []
    me.navigate(
        '/conversation',
        query_params={'conversation_id': response.conversation_id},
    )
    yield


# Functions are now defined above where they're used
