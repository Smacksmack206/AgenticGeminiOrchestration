import asyncio

import mesop as me
import pandas as pd

from demo.ui.state.host_agent_service import GetEvents, convert_event_to_state


def flatten_content(content: list[tuple[str, str]]) -> str:
    parts = []
    for p in content:
        if p[1] == 'text/plain' or p[1] == 'application/json':
            parts.append(p[0])
        else:
            parts.append(p[1])

    return '\n'.join(parts)


@me.component
def event_list():
    """Events list component"""
    df_data = {
        'Timestamp': [],
        'Conversation ID': [],
        'Actor': [],
        'Role': [],
        'Id': [],
        'Content': [],
    }
    events = asyncio.run(GetEvents())
    
    # Sort events by timestamp (chronological order - newest first)
    events_sorted = sorted(events, key=lambda e: e.timestamp if hasattr(e, 'timestamp') and e.timestamp else 0, reverse=True)
    
    for e in events_sorted:
        event = convert_event_to_state(e)
        # Add timestamp formatting
        if hasattr(e, 'timestamp') and e.timestamp:
            import datetime
            timestamp_str = datetime.datetime.fromtimestamp(e.timestamp).strftime('%H:%M:%S')
        else:
            timestamp_str = 'N/A'
        
        df_data['Timestamp'].append(timestamp_str)
        df_data['Conversation ID'].append(event.context_id)
        df_data['Role'].append(event.role)
        df_data['Id'].append(event.id)
        df_data['Content'].append(flatten_content(event.content))
        df_data['Actor'].append(event.actor)
    if not df_data['Conversation ID']:
        me.text('No events found')
        return
    df = pd.DataFrame(
        pd.DataFrame(df_data),
        columns=['Timestamp', 'Conversation ID', 'Actor', 'Role', 'Id', 'Content'],
    )
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='space-between',
            flex_direction='column',
        )
    ):
        me.table(
            df,
            header=me.TableHeader(sticky=True),
            columns={
                'Conversation ID': me.TableColumn(sticky=True),
                'Actor': me.TableColumn(sticky=True),
                'Role': me.TableColumn(sticky=True),
                'Id': me.TableColumn(sticky=True),
                'Content': me.TableColumn(sticky=True),
            },
        )
