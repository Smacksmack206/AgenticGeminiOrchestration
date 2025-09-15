import mesop as me


SIDENAV_MIN_WIDTH = 68
SIDENAV_MAX_WIDTH = 200

DEFAULT_MENU_STYLE = me.Style(align_content='left')

_FANCY_TEXT_GRADIENT = me.Style(
    color='transparent',
    background=(
        'linear-gradient(72.83deg,#4285f4 11.63%,#9b72cb 40.43%,#d96570 68.07%)'
        ' text'
    ),
)

MAIN_COLUMN_STYLE = me.Style(
    display='flex',
    flex_direction='column',
    height='100%',
)

PAGE_BACKGROUND_STYLE = me.Style(
    background='linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
    height='100%',
    overflow_y='scroll',
    margin=me.Margin(bottom=0),
)

PAGE_BACKGROUND_PADDING_STYLE = me.Style(
    background='transparent',
    padding=me.Padding(top=0, left=0, right=0, bottom=0),
    display='flex',
    flex_direction='column',
    min_height='100vh',
)
