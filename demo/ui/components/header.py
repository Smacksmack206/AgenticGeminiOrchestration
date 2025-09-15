import mesop as me

from demo.ui.components.poller import polling_buttons


@me.content_component
def header(title: str, icon: str):
    """Modern header component with beautiful styling"""
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='space-between',
            align_items='center',
            padding=me.Padding(top=20, bottom=20, left=24, right=24),
            background='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color='white',
            box_shadow='0 4px 20px rgba(102, 126, 234, 0.3)',
        )
    ):
        with me.box(
            style=me.Style(
                display='flex', 
                align_items='center', 
                gap=12
            )
        ):
            # Icon with background
            with me.box(
                style=me.Style(
                    background='rgba(255, 255, 255, 0.2)',
                    border_radius=12,
                    padding=me.Padding(top=8, bottom=8, left=8, right=8),
                    display='flex',
                    align_items='center',
                    justify_content='center',
                )
            ):
                me.icon(
                    icon=icon,
                    style=me.Style(
                        font_size='24px',
                        color='white',
                    )
                )
            
            me.text(
                title,
                style=me.Style(
                    font_family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    font_size='28px',
                    font_weight='600',
                    color='white',
                ),
            )
        
        with me.box(
            style=me.Style(
                display='flex',
                align_items='center',
                gap=12,
            )
        ):
            me.slot()
            polling_buttons()
