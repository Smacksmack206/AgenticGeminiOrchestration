#!/usr/bin/env python3
"""
Script to automatically register default agents with the system
"""
import json
import os
import asyncio
import httpx
from demo.ui.utils.agent_card import get_agent_card

# Default agents to register
DEFAULT_AGENTS = [
    "http://localhost:12111",  # Coder Agent
    "http://localhost:12200",  # VEO Video Generation Agent
]

async def register_agents():
    """Register default agents"""
    agents_file = "agents.json"
    
    # Check if agents file already exists
    if os.path.exists(agents_file):
        print(f"Agents file {agents_file} already exists. Skipping registration.")
        return
    
    agents = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for agent_url in DEFAULT_AGENTS:
            try:
                print(f"Registering agent at {agent_url}...")
                
                # Get agent card
                agent_card = get_agent_card(agent_url)
                if not agent_card.url:
                    agent_card.url = agent_url
                
                agents.append(agent_card.dict())
                print(f"✓ Successfully registered: {agent_card.name}")
                
            except Exception as e:
                print(f"✗ Failed to register agent at {agent_url}: {e}")
                continue
    
    # Save agents to file
    if agents:
        try:
            with open(agents_file, 'w') as f:
                json.dump(agents, f, indent=2)
            print(f"\n✓ Saved {len(agents)} agents to {agents_file}")
        except Exception as e:
            print(f"✗ Failed to save agents file: {e}")
    else:
        print("\n✗ No agents were successfully registered")

if __name__ == "__main__":
    asyncio.run(register_agents())
