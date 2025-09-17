import httpx
import requests
import json

from a2a.types import AgentCard, AgentCapabilities
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


async def get_agent_card(remote_agent_address: str) -> AgentCard:
    """Get the agent card."""
    if not remote_agent_address.startswith(('http://', 'https://')):
        remote_agent_address = 'http://' + remote_agent_address
    try:
        async with httpx.AsyncClient() as client:
            agent_card_response = await client.get(
                f'{remote_agent_address}{AGENT_CARD_WELL_KNOWN_PATH}'
            )
            agent_card_response.raise_for_status() # Raise an exception for bad status codes
            return AgentCard(**agent_card_response.json())
    except (httpx.RequestError, httpx.HTTPStatusError, json.decoder.JSONDecodeError) as e:
        print(f"Error fetching agent card from {remote_agent_address}: {e}")
        # Return a default AgentCard with the URL and default values for required fields
        return AgentCard(
            url=remote_agent_address,
            name="Unknown Agent",
            description="Could not fetch agent card",
            capabilities=AgentCapabilities(), # Provide a default empty capabilities
            default_input_modes=[], # Provide an empty list
            default_output_modes=[], # Provide an empty list
            skills=[], # Provide an empty list
            version="0.0.0" # Provide a default version
        )
