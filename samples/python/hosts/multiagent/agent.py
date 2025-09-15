import httpx
import asyncio
from samples.python.hosts.multiagent.host_agent import HostAgent

async def initialize_root_agent():
    client = httpx.AsyncClient()
    agent = HostAgent(['http://localhost:10000'], client).create_agent()
    return agent

root_agent = asyncio.run(initialize_root_agent())
