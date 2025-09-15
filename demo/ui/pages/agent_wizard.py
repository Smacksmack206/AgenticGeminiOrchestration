import os
import uuid
from typing import List

import mesop as me
import traceback

from demo.ui.components.header import header
from demo.ui.components.page_scaffold import page_frame, page_scaffold
from demo.ui.state.state import AppState


@me.stateclass
class AgentWizardState:
    """State for the agent configuration wizard"""
    
    # Basic Info
    agent_name: str = ''
    agent_description: str = ''
    agent_port: int = 10004
    
    # Capabilities
    supports_streaming: bool = True
    supports_text_input: bool = True
    supports_image_input: bool = False
    supports_video_input: bool = False
    
    # Output Types
    supports_text_output: bool = True
    supports_image_output: bool = False
    supports_video_output: bool = False
    
    # Skills
    skills: List[dict] = None
    current_skill_name: str = ''
    current_skill_description: str = ''
    current_skill_tags: str = ''
    
    # Advanced
    custom_code: str = ''
    
    # Wizard Steps
    current_step: int = 1
    total_steps: int = 5
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []


def on_agent_name_change(e: me.InputBlurEvent):
    state = me.state(AgentWizardState)
    state.agent_name = e.value


def on_agent_description_change(e: me.InputBlurEvent):
    state = me.state(AgentWizardState)
    state.agent_description = e.value


def on_agent_port_change(e: me.InputBlurEvent):
    state = me.state(AgentWizardState)
    try:
        state.agent_port = int(e.value)
    except ValueError:
        state.agent_port = 10004


def on_streaming_change(e: me.CheckboxChangeEvent):
    state = me.state(AgentWizardState)
    state.supports_streaming = e.checked


def on_text_input_change(e: me.CheckboxChangeEvent):
    state = me.state(AgentWizardState)
    state.supports_text_input = e.checked


def on_image_input_change(e: me.CheckboxChangeEvent):
    state = me.state(AgentWizardState)
    state.supports_image_input = e.checked


def on_video_input_change(e: me.CheckboxChangeEvent):
    state = me.state(AgentWizardState)
    state.supports_video_input = e.checked


def on_text_output_change(e: me.CheckboxChangeEvent):
    state = me.state(AgentWizardState)
    state.supports_text_output = e.checked


def on_image_output_change(e: me.CheckboxChangeEvent):
    state = me.state(AgentWizardState)
    state.supports_image_output = e.checked


def on_video_output_change(e: me.CheckboxChangeEvent):
    state = me.state(AgentWizardState)
    state.supports_video_output = e.checked


def on_skill_name_change(e: me.InputBlurEvent):
    state = me.state(AgentWizardState)
    state.current_skill_name = e.value


def on_skill_description_change(e: me.InputBlurEvent):
    state = me.state(AgentWizardState)
    state.current_skill_description = e.value


def on_skill_tags_change(e: me.InputBlurEvent):
    state = me.state(AgentWizardState)
    state.current_skill_tags = e.value


def on_custom_code_change(e: me.InputBlurEvent):
    state = me.state(AgentWizardState)
    state.custom_code = e.value


def add_skill(e: me.ClickEvent):  # pylint: disable=unused-argument
    state = me.state(AgentWizardState)
    if state.current_skill_name and state.current_skill_description:
        skill = {
            'name': state.current_skill_name,
            'description': state.current_skill_description,
            'tags': [tag.strip() for tag in state.current_skill_tags.split(',') if tag.strip()],
        }
        state.skills.append(skill)
        # Clear current skill inputs
        state.current_skill_name = ''
        state.current_skill_description = ''
        state.current_skill_tags = ''
    yield


def remove_skill(e: me.ClickEvent, skill_index: int):  # pylint: disable=unused-argument
    state = me.state(AgentWizardState)
    if 0 <= skill_index < len(state.skills):
        state.skills.pop(skill_index)
    yield


def next_step(e: me.ClickEvent):  # pylint: disable=unused-argument
    state = me.state(AgentWizardState)
    if state.current_step < state.total_steps:
        state.current_step += 1
    yield


def prev_step(e: me.ClickEvent):  # pylint: disable=unused-argument
    state = me.state(AgentWizardState)
    if state.current_step > 1:
        state.current_step -= 1
    yield


def generate_agent(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Generate the agent files based on the configuration"""
    state = me.state(AgentWizardState)
    
    try:
        # Create agent directory
        agent_dir = f"samples/python/agents/{state.agent_name.lower().replace(' ', '_')}"
        os.makedirs(agent_dir, exist_ok=True)
        
        # Generate agent files
        generate_agent_files(state, agent_dir)
        
        # Show success message (in a real implementation, you'd show a proper dialog)
        me.navigate('/agents')
    except Exception as ex:
        print(f"Error generating agent: {ex}")
        traceback.print_exc()
        # Optionally, set an error message in the state to display in the UI
        # app_state = me.state(AppState)
        # app_state.error = f"Error generating agent: {ex}"
    yield


def generate_agent_files(state: AgentWizardState, agent_dir: str):
    """Generate the actual agent files"""
    
    files_to_generate = {
        "__main__.py": generate_main_py(state),
        "agent.py": generate_agent_py(state),
        "agent_executor.py": generate_agent_executor_py(state),
        "pyproject.toml": generate_pyproject_toml(state),
        "README.md": generate_readme_md(state),
    }

    for filename, content in files_to_generate.items():
        file_path = os.path.join(agent_dir, filename)
        try:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Successfully generated {file_path}")
        except IOError as e:
            print(f"Error writing file {file_path}: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"An unexpected error occurred while generating {file_path}: {e}")
            traceback.print_exc()


def generate_main_py(state: AgentWizardState) -> str:
    """Generate the __main__.py file content"""
    input_types = []
    if state.supports_text_input:
        input_types.append("'text/plain'")
    if state.supports_image_input:
        input_types.append("'image/*'")
    if state.supports_video_input:
        input_types.append("'video/*'")
    
    output_types = []
    if state.supports_text_output:
        output_types.append("'text/plain'")
    if state.supports_image_output:
        output_types.append("'image/*'")
    if state.supports_video_output:
        output_types.append("'video/*'")
    
    skills_code_items = []
    for skill in state.skills:
        skills_code_items.append(f"""
            AgentSkill(
                id='{skill['name'].lower().replace(' ', '_')}',
                name='{skill['name']}',
                description='{skill['description']}',
                tags={skill['tags']},
            )""")
    
    skills_code = ",\n        ".join(skills_code_items)
    if skills_code:
        skills_code = f"\n        {skills_code},\n        "
    else:
        skills_code = ""
    
    return f'''import logging
import os

import click

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from .agent import {state.agent_name.replace(' ', '')}Agent
from .agent_executor import {state.agent_name.replace(' ', '')}AgentExecutor
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '--host', default='localhost', help='Hostname to bind the server to.'
)
@click.option(
    '--port', default={state.agent_port}, help='Port to bind the server to.'
)
def main(host: str, port: int):
    try:
        # Agent Card Configuration
        capabilities = AgentCapabilities(
            streaming={str(state.supports_streaming).lower()}
        )

        skills = [{skills_code}
        ]

        agent_card = AgentCard(
            name='{state.agent_name}',
            description='{state.agent_description}',
            url=f'http://{{host}}:{{port}}/',
            version='1.0.0',
            default_input_modes=[{', '.join(input_types) if input_types else "''"}],
            default_output_modes=[{', '.join(output_types) if output_types else "''"}],
            capabilities=capabilities,
            skills=skills,
        )

        request_handler = DefaultRequestHandler(
            agent_executor={state.agent_name.replace(' ', '')}AgentExecutor(),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        logger.info(
            f'Starting {state.agent_name} server on http://{{host}}:{{port}}'
        )

        import uvicorn

        uvicorn.run(server.build(), host=host, port=port)

    except Exception as e:
        logger.error(
            f'An unexpected error occurred during server startup: {{e}}',
            exc_info=True,
        )
        exit(1)


if __name__ == '__main__':
    main()
'''


def generate_agent_py(state: AgentWizardState) -> str:
    """Generate the agent.py file content"""
    return f'''import logging
from typing import Any, AsyncIterable

logger = logging.getLogger(__name__)


class {state.agent_name.replace(' ', '')}Agent:
    """
    {state.agent_description}
    """

    SUPPORTED_INPUT_CONTENT_TYPES = [{'text/plain' if state.supports_text_input else ''}]
    SUPPORTED_OUTPUT_CONTENT_TYPES = [{'text/plain' if state.supports_text_output else ''}]

    def __init__(self):
        logger.info('Initializing {state.agent_name}Agent...')
        # Add any initialization logic here
        logger.info('{state.agent_name}Agent initialized.')

    async def process_request(self, prompt: str, session_id: str) -> AsyncIterable[dict[str, Any]]:
        """
        Process a request and yield responses
        """
        logger.info(f"Processing request for session {{session_id}}: {{prompt}}")
        
        # Yield initial response
        yield {{
            'is_task_complete': False,
            'updates': f"Processing request: '{{prompt}}'",
            'progress_percent': 10,
        }}
        
        # Add your custom logic here
        {state.custom_code if state.custom_code else '# Add your custom processing logic here'}
        
        # Yield final response
        yield {{
            'is_task_complete': True,
            'content': f"Hello! I'm {state.agent_name}. You said: {{prompt}}",
            'final_message_text': 'Request processed successfully.',
            'progress_percent': 100,
        }}
'''


def generate_agent_executor_py(state: AgentWizardState) -> str:
    """Generate the agent_executor.py file content"""
    return f'''import asyncio
import logging
from typing import Any, AsyncIterable

from a2a.server.request_handlers import AgentExecutor
from a2a.types import Message, Part, TextPart

from .agent import {state.agent_name.replace(' ', '')}Agent

logger = logging.getLogger(__name__)


class {state.agent_name.replace(' ', '')}AgentExecutor(AgentExecutor):
    """Agent executor for {state.agent_name}"""

    def __init__(self):
        self.agent = {state.agent_name.replace(' ', '')}Agent()

    async def execute(self, message: Message) -> AsyncIterable[dict[str, Any]]:
        """Execute the agent with the given message"""
        
        # Extract text from message
        text_content = ""
        for part in message.parts:
            if part.root.kind == 'text':
                text_content += part.root.text + " "
        
        text_content = text_content.strip()
        session_id = message.context_id or "default"
        
        # Process with the agent
        async for response in self.agent.process_request(text_content, session_id):
            yield response
'''


def generate_pyproject_toml(state: AgentWizardState) -> str:
    """Generate the pyproject.toml file content"""
    return f'''[project]
name = "{state.agent_name.lower().replace(' ', '-')}"
version = "0.1.0"
description = "{state.agent_description}"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "a2a-sdk>=0.3.0",
    "click>=8.1.8",
    "python-dotenv>=1.1.0",
]

[tool.hatch.build.targets.wheel]
packages = ["."]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''


def generate_readme_md(state: AgentWizardState) -> str:
    """Generate the README.md file content"""
    skills_list = ""
    for skill in state.skills:
        skills_list += f"- **{skill['name']}**: {skill['description']}\n"
    
    return f'''# {state.agent_name}

{state.agent_description}

## Features

{skills_list if skills_list else "- Basic text processing capabilities"}

## Configuration

- **Port**: {state.agent_port}
- **Streaming**: {"Enabled" if state.supports_streaming else "Disabled"}
- **Input Types**: {", ".join([
    "Text" if state.supports_text_input else "",
    "Images" if state.supports_image_input else "",
    "Videos" if state.supports_video_input else ""
]).strip(", ")}
- **Output Types**: {", ".join([
    "Text" if state.supports_text_output else "",
    "Images" if state.supports_image_output else "",
    "Videos" if state.supports_video_output else ""
]).strip(", ")}

## Running the Agent

```bash
# Install dependencies
pip install -e .

# Run the agent
python -m {state.agent_name.lower().replace(' ', '_')}.__main__ --host 0.0.0.0 --port {state.agent_port}
```

## Usage

Connect to the agent at `http://localhost:{state.agent_port}` using the A2A protocol.

Generated by A2A Agent Wizard.
'''


def agent_wizard_page():
    """Agent Configuration Wizard Page"""
    state = me.state(AgentWizardState)
    
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Agent Configuration Wizard', 'auto_fix_high'):
                pass
            
            # Progress indicator
            with me.box(
                style=me.Style(
                    display='flex',
                    align_items='center',
                    margin=me.Margin(bottom=30),
                    gap=10,
                )
            ):
                me.text(
                    f"Step {state.current_step} of {state.total_steps}",
                    style=me.Style(font_weight='bold', font_size='18px')
                )
                me.progress_bar(
                    value=state.current_step / state.total_steps
                )
                    
            
            # Step content
            if state.current_step == 1:
                render_basic_info_step(state)
            elif state.current_step == 2:
                render_capabilities_step(state)
            elif state.current_step == 3:
                render_output_types_step(state)
            elif state.current_step == 4:
                render_skills_step(state)
            elif state.current_step == 5:
                render_review_step(state)
            
            # Navigation buttons
            with me.box(
                style=me.Style(
                    display='flex',
                    justify_content='space-between',
                    margin=me.Margin(top=40),
                )
            ):
                if state.current_step > 1:
                    me.button(
                        'Previous',
                        on_click=prev_step,
                        type='outlined',
                    )
                else:
                    me.box()  # Empty box for spacing
                
                if state.current_step < state.total_steps:
                    me.button(
                        'Next',
                        on_click=next_step,
                        type='raised',
                    )
                else:
                    me.button(
                        'Generate Agent',
                        on_click=generate_agent,
                        type='raised',
                        style=me.Style(background=me.theme_var('primary')),
                    )


def render_basic_info_step(state: AgentWizardState):
    """Render the basic information step"""
    me.text(
        'Basic Information',
        type='headline-5',
        style=me.Style(margin=me.Margin(bottom=20))
    )
    
    me.input(
        label='Agent Name',
        value=state.agent_name,
        on_blur=on_agent_name_change,
        style=me.Style(width='100%', margin=me.Margin(bottom=20)),
    )
    
    me.textarea(
        label='Agent Description',
        value=state.agent_description,
        on_blur=on_agent_description_change,
        rows=3,
        style=me.Style(width='100%', margin=me.Margin(bottom=20)),
    )
    
    me.input(
        label='Port Number',
        value=str(state.agent_port),
        on_blur=on_agent_port_change,
        type='number',
        style=me.Style(width='200px'),
    )


def render_capabilities_step(state: AgentWizardState):
    """Render the capabilities step"""
    me.text(
        'Agent Capabilities',
        type='headline-5',
        style=me.Style(margin=me.Margin(bottom=20))
    )
    
    me.checkbox(
        'Supports Streaming',
        checked=state.supports_streaming,
        on_change=on_streaming_change,
        style=me.Style(margin=me.Margin(bottom=15)),
    )
    
    me.text(
        'Input Types',
        type='headline-6',
        style=me.Style(margin=me.Margin(top=20, bottom=10))
    )
    
    me.checkbox(
        'Text Input',
        checked=state.supports_text_input,
        on_change=on_text_input_change,
        style=me.Style(margin=me.Margin(bottom=10)),
    )
    
    me.checkbox(
        'Image Input',
        checked=state.supports_image_input,
        on_change=on_image_input_change,
        style=me.Style(margin=me.Margin(bottom=10)),
    )
    
    me.checkbox(
        'Video Input',
        checked=state.supports_video_input,
        on_change=on_video_input_change,
        style=me.Style(margin=me.Margin(bottom=10)),
    )


def render_output_types_step(state: AgentWizardState):
    """Render the output types step"""
    me.text(
        'Output Types',
        type='headline-5',
        style=me.Style(margin=me.Margin(bottom=20))
    )
    
    me.checkbox(
        'Text Output',
        checked=state.supports_text_output,
        on_change=on_text_output_change,
        style=me.Style(margin=me.Margin(bottom=10)),
    )
    
    me.checkbox(
        'Image Output',
        checked=state.supports_image_output,
        on_change=on_image_output_change,
        style=me.Style(margin=me.Margin(bottom=10)),
    )
    
    me.checkbox(
        'Video Output',
        checked=state.supports_video_output,
        on_change=on_video_output_change,
        style=me.Style(margin=me.Margin(bottom=10)),
    )


def render_skills_step(state: AgentWizardState):
    """Render the skills configuration step"""
    me.text(
        'Agent Skills',
        type='headline-5',
        style=me.Style(margin=me.Margin(bottom=20))
    )
    
    # Add new skill form
    with me.box(
        style=me.Style(
            background='#f5f5f5',
            padding=me.Padding(top=20, bottom=20, left=20, right=20),
            border_radius=8,
            margin=me.Margin(bottom=20),
        )
    ):
        me.text(
            'Add New Skill',
            type='headline-6',
            style=me.Style(margin=me.Margin(bottom=15))
        )
        
        me.input(
            label='Skill Name',
            value=state.current_skill_name,
            on_blur=on_skill_name_change,
            style=me.Style(width='100%', margin=me.Margin(bottom=10)),
        )
        
        me.textarea(
            label='Skill Description',
            value=state.current_skill_description,
            on_blur=on_skill_description_change,
            rows=2,
            style=me.Style(width='100%', margin=me.Margin(bottom=10)),
        )
        
        me.input(
            label='Tags (comma-separated)',
            value=state.current_skill_tags,
            on_blur=on_skill_tags_change,
            style=me.Style(width='100%', margin=me.Margin(bottom=15)),
        )
        
        me.button(
            'Add Skill',
            on_click=add_skill,
            type='raised',
        )
    
    # Display existing skills
    if state.skills:
        me.text(
            'Configured Skills',
            type='headline-6',
            style=me.Style(margin=me.Margin(bottom=15))
        )
        
        for i, skill in enumerate(state.skills):
            with me.box(
                style=me.Style(
                    # border not supported in Mesop Style
                    padding=me.Padding(top=15, bottom=15, left=15, right=15),
                    border_radius=5,
                    margin=me.Margin(bottom=10),
                    display='flex',
                    justify_content='space-between',
                    align_items='center',
                )
            ):
                with me.box():
                    me.text(
                        skill['name'],
                        style=me.Style(font_weight='bold', margin=me.Margin(bottom=5))
                    )
                    me.text(
                        skill['description'],
                        style=me.Style(color='#666', margin=me.Margin(bottom=5))
                    )
                    if skill['tags']:
                        me.text(
                            f"Tags: {', '.join(skill['tags'])}",
                            style=me.Style(font_size='12px', color='#888')
                        )
                
                with me.content_button(
                    type='icon',
                    on_click=lambda e, idx=i: remove_skill(e, idx),
                    style=me.Style(color='red'),
                ):
                    me.icon(icon='delete')


def render_review_step(state: AgentWizardState):
    """Render the review and generate step"""
    me.text(
        'Review Configuration',
        type='headline-5',
        style=me.Style(margin=me.Margin(bottom=20))
    )
    
    # Basic info
    with me.box(style=me.Style(margin=me.Margin(bottom=20))):
        me.text('Basic Information', type='headline-6', style=me.Style(margin=me.Margin(bottom=10)))
        me.text(f'Name: {state.agent_name}')
        me.text(f'Description: {state.agent_description}')
        me.text(f'Port: {state.agent_port}')
    
    # Capabilities
    with me.box(style=me.Style(margin=me.Margin(bottom=20))):
        me.text('Capabilities', type='headline-6', style=me.Style(margin=me.Margin(bottom=10)))
        me.text(f'Streaming: {"Yes" if state.supports_streaming else "No"}')
        
        input_types = []
        if state.supports_text_input:
            input_types.append('Text')
        if state.supports_image_input:
            input_types.append('Images')
        if state.supports_video_input:
            input_types.append('Videos')
        me.text(f'Input Types: {", ".join(input_types) if input_types else "None"}')
        
        output_types = []
        if state.supports_text_output:
            output_types.append('Text')
        if state.supports_image_output:
            output_types.append('Images')
        if state.supports_video_output:
            output_types.append('Videos')
        me.text(f'Output Types: {", ".join(output_types) if output_types else "None"}')
    
    # Skills
    if state.skills:
        with me.box(style=me.Style(margin=me.Margin(bottom=20))):
            me.text('Skills', type='headline-6', style=me.Style(margin=me.Margin(bottom=10)))
            for skill in state.skills:
                me.text(f'• {skill["name"]}: {skill["description"]}')
