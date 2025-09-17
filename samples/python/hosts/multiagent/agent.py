import httpx
from .host_agent import HostAgent


root_agent = HostAgent(['http://localhost:10000'], httpx.AsyncClient()).create_agent()
