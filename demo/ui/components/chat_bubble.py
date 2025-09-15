import mesop as me

from demo.ui.state.state import AppState, StateMessage


@me.component
def chat_bubble(message: StateMessage, key: str):
    """Modern chat bubble component with beautiful design"""
    app_state = me.state(AppState)
    show_progress_bar = (
        message.message_id in app_state.background_tasks
        or message.message_id in app_state.message_aliases.values()
    )
    progress_text = ''
    if show_progress_bar:
        progress_text = app_state.background_tasks[message.message_id]
    if not message.content:
        print('No message content')
    for pair in message.content:
        modern_chat_box(
            pair[0],
            pair[1],
            message.role,
            key,
            progress_bar=show_progress_bar,
            progress_text=progress_text,
        )


def modern_chat_box(
    content: str,
    media_type: str,
    role: str,
    key: str,
    progress_bar: bool,
    progress_text: str,
):
    """Modern chat box with beautiful styling"""
    is_user = role == 'user'
    
    # Color scheme
    user_bg = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    agent_bg = '#f8fafc'
    user_text_color = 'white'
    agent_text_color = '#1a202c'
    
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='flex-end' if is_user else 'flex-start',
            margin=me.Margin(bottom=16),
            padding=me.Padding(left=20, right=20),
        ),
        key=key,
    ):
        with me.box(
            style=me.Style(
                max_width='70%',
                min_width='200px',
            )
        ):
            # Avatar and name row
            with me.box(
                style=me.Style(
                    display='flex',
                    align_items='center',
                    gap=8,
                    margin=me.Margin(bottom=8),
                    justify_content='flex-end' if is_user else 'flex-start',
                )
            ):
                if not is_user:
                    # Agent avatar
                    with me.box(
                        style=me.Style(
                            width=32,
                            height=32,
                            border_radius=16,
                            background='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            display='flex',
                            align_items='center',
                            justify_content='center',
                        )
                    ):
                        me.icon(
                            icon='smart_toy',
                            style=me.Style(
                                color='white',
                                font_size='18px',
                            )
                        )
                
                me.text(
                    'You' if is_user else 'AI Assistant',
                    style=me.Style(
                        font_size='12px',
                        font_weight='500',
                        color='#6b7280',
                    )
                )
                
                if is_user:
                    # User avatar
                    with me.box(
                        style=me.Style(
                            width=32,
                            height=32,
                            border_radius=16,
                            background='#e5e7eb',
                            display='flex',
                            align_items='center',
                            justify_content='center',
                        )
                    ):
                        me.icon(
                            icon='person',
                            style=me.Style(
                                color='#6b7280',
                                font_size='18px',
                            )
                        )
            
            # Message content
            with me.box(
                style=me.Style(
                    background=user_bg if is_user else agent_bg,
                    color=user_text_color if is_user else agent_text_color,
                    padding=me.Padding(top=16, bottom=16, left=20, right=20),
                    border_radius=20,
                    box_shadow='0 2px 8px rgba(0, 0, 0, 0.1)' if not is_user else '0 4px 12px rgba(102, 126, 234, 0.3)',
                    # border not supported in Mesop Style
                )
            ):
                if media_type == 'image/png' or media_type.startswith('image/'):
                    if '/message/file' not in content:
                        content = 'data:image/png;base64,' + content
                    me.image(
                        src=content,
                        style=me.Style(
                            width='100%',
                            max_width='400px',
                            border_radius=12,
                            object_fit='contain',
                        ),
                    )
                elif media_type == 'video/mp4' or media_type.startswith('video/'):
                    # Enhanced video content with modern styling
                    with me.box(
                        style=me.Style(
                            background='linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                            border_radius=12,
                            padding=me.Padding(top=16, bottom=16, left=16, right=16),
                            # border not supported in Mesop Style
                        )
                    ):
                        # Video header
                        with me.box(
                            style=me.Style(
                                display='flex',
                                align_items='center',
                                gap=8,
                                margin=me.Margin(bottom=12),
                            )
                        ):
                            me.icon(
                                icon='movie',
                                style=me.Style(
                                    color='#60a5fa',
                                    font_size='20px',
                                )
                            )
                            me.text(
                                "Generated Video",
                                style=me.Style(
                                    color='white',
                                    font_size='16px',
                                    font_weight='600',
                                )
                            )
                        
                        # Video player or link
                        if content.startswith('http'):
                            # Create a clickable video link
                            with me.box(
                                style=me.Style(
                                    background='rgba(96, 165, 250, 0.1)',
                                    # border not supported in Mesop Style
                                    border_radius=8,
                                    padding=me.Padding(top=12, bottom=12, left=12, right=12),
                                    cursor='pointer',
                                ),
                                on_click=lambda e: me.navigate(content, new_tab=True)
                            ):
                                with me.box(
                                    style=me.Style(
                                        display='flex',
                                        align_items='center',
                                        gap=8,
                                    )
                                ):
                                    me.icon(
                                        icon='play_circle',
                                        style=me.Style(
                                            color='#60a5fa',
                                            font_size='24px',
                                        )
                                    )
                                    with me.box():
                                        me.text(
                                            "Click to view video",
                                            style=me.Style(
                                                color='#60a5fa',
                                                font_size='14px',
                                                font_weight='500',
                                            )
                                        )
                                        me.text(
                                            "Opens in new tab",
                                            style=me.Style(
                                                color='#94a3b8',
                                                font_size='12px',
                                            )
                                        )
                        else:
                            # Fallback for non-URL content
                            me.text(
                                f"Video content: {content[:50]}{'...' if len(content) > 50 else ''}",
                                style=me.Style(
                                    color='#e2e8f0',
                                    font_size='14px',
                                )
                            )
                else:
                    me.markdown(
                        content,
                        style=me.Style(
                            font_family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                            font_size='15px',
                            line_height='1.6',
                        ),
                    )
    
    # Progress bar for ongoing operations
    if progress_bar:
        with me.box(
            style=me.Style(
                display='flex',
                justify_content='flex-start',
                margin=me.Margin(bottom=16),
                padding=me.Padding(left=20, right=20),
            ),
        ):
            with me.box(
                style=me.Style(
                    max_width='70%',
                    min_width='200px',
                )
            ):
                with me.box(
                    style=me.Style(
                        background='#f8fafc',
                        # border not supported in Mesop Style
                        padding=me.Padding(top=16, bottom=16, left=20, right=20),
                        border_radius=20,
                        box_shadow='0 2px 8px rgba(0, 0, 0, 0.05)',
                    )
                ):
                    with me.box(
                        style=me.Style(
                            display='flex',
                            align_items='center',
                            gap=12,
                            margin=me.Margin(bottom=8),
                        )
                    ):
                        # Animated thinking icon
                        me.icon(
                            icon='psychology',
                            style=me.Style(
                                color='#667eea',
                                font_size='20px',
                            )
                        )
                        me.text(
                            progress_text or 'AI is thinking...',
                            style=me.Style(
                                font_size='14px',
                                color='#6b7280',
                                font_weight='500',
                            )
                        )
                    
                    me.progress_bar(
                        color='primary',
                        
                    )
