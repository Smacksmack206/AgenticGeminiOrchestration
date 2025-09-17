import httpx
import asyncio
import json
import time
import os
import uuid

# Configuration
UI_URL = "http://localhost:8000"
HOST_AGENT_LOG_PATH = "/Users/home/HM-labs/A2A/a2a-samples/logs/agent_8000.log"
CODER_AGENT_LOG_PATH = "/Users/home/HM-labs/A2A/a2a-samples/logs/agent_12111.log"
VIDEO_AGENT_LOG_PATH = "/Users/home/HM-labs/A2A/a2a-samples/logs/agent_12200.log"

TEST_PROMPTS = [
    {
        "prompt": "Can you write a Python script to parse a CSV file?",
        "expected_agent_name": "Coder Agent",
        "expected_agent_url": "http://localhost:12111/",
    },
    {
        "prompt": "I need a short video explaining quantum physics for social media.",
        "expected_agent_name": "VEO Video Generation Agent",
        "expected_agent_url": "http://localhost:12200/",
    },
    {
        "prompt": "What's the weather like in London tomorrow?",
        "expected_agent_name": None, # Should trigger clarification
        "expected_agent_url": None,
    },
    {
        "prompt": "Tell me a joke.",
        "expected_agent_name": None, # Should trigger clarification
        "expected_agent_url": None,
    },
]

async def send_message_to_ui(client: httpx.AsyncClient, message_text: str, conversation_id: str):
    message_payload = {
        "message": {
            "parts": [{"root": {"kind": "text", "text": message_text}}],
            "context_id": conversation_id,
            "message_id": str(uuid.uuid4()),
            "role": "user"
        },
        "conversation_id": conversation_id
    }
    print(f"Sending message to UI: {message_text}")
    response = await client.post(f"{UI_URL}/message/send", json=message_payload)
    response.raise_for_status()
    print(f"UI response status: {response.status_code}")

async def get_latest_log_content(log_path: str):
    if not os.path.exists(log_path):
        return ""
    with open(log_path, 'r') as f:
        return f.read()

async def run_test():
    async with httpx.AsyncClient() as client:
        # Create a new conversation
        print("Creating new conversation...")
        create_conv_response = await client.post(f"{UI_URL}/conversation/create")
        create_conv_response.raise_for_status()
        conversation_id = create_conv_response.json()["conversation_id"]
        print(f"Created conversation ID: {conversation_id}")

        # Give agents some time to initialize and for logs to settle
        time.sleep(5) 
        
        initial_host_log = await get_latest_log_content(HOST_AGENT_LOG_PATH)
        initial_coder_log = await get_latest_log_content(CODER_AGENT_LOG_PATH)
        initial_video_log = await get_latest_log_content(VIDEO_AGENT_LOG_PATH)

        for test_case in TEST_PROMPTS:
            prompt = test_case["prompt"]
            expected_agent_name = test_case["expected_agent_name"]
            expected_agent_url = test_case["expected_agent_url"]

            print(f"\n--- Testing Prompt: \"{prompt}\" ---")
            await send_message_to_ui(client, prompt, conversation_id)
            
            # Give time for processing and logging
            time.sleep(10) 

            latest_host_log = await get_latest_log_content(HOST_AGENT_LOG_PATH)
            latest_coder_log = await get_latest_log_content(CODER_AGENT_LOG_PATH)
            latest_video_log = await get_latest_log_content(VIDEO_AGENT_LOG_PATH)

            new_host_log_content = latest_host_log[len(initial_host_log):]
            new_coder_log_content = latest_coder_log[len(initial_coder_log):]
            new_video_log_content = latest_video_log[len(initial_video_log):]

            print("\n--- Host Agent Log Output ---")
            print(new_host_log_content)
            print("-----------------------------")

            if expected_agent_name:
                # Check if Host Agent attempted to route
                if f"DEBUG: Determined target_agent_url: {expected_agent_url}" in new_host_log_content:
                    print(f"SUCCESS: Host Agent correctly determined target URL for {expected_agent_name}.")
                else:
                    print(f"FAILURE: Host Agent DID NOT determine expected target URL for {expected_agent_name}.")
                    print(f"Expected URL: {expected_agent_url}")
                
                # Check if message was sent to the target agent's log
                if expected_agent_name == "Coder Agent":
                    if "Processing message:" in new_coder_log_content and prompt in new_coder_log_content:
                        print(f"SUCCESS: Message received by {expected_agent_name}.")
                    else:
                        print(f"FAILURE: Message NOT received by {expected_agent_name}.")
                elif expected_agent_name == "VEO Video Generation Agent":
                    if "Processing message:" in new_video_log_content and prompt in new_video_log_content:
                        print(f"SUCCESS: Message received by {expected_agent_name}.")
                    else:
                        print(f"FAILURE: Message NOT received by {expected_agent_name}.")
            else:
                # Check for clarification response
                if "DEBUG: No specific agent determined, asking for clarification." in new_host_log_content:
                    print("SUCCESS: Host Agent correctly asked for clarification.")
                else:
                    print("FAILURE: Host Agent DID NOT ask for clarification as expected.")
            
            initial_host_log = latest_host_log # Update for next iteration
            initial_coder_log = latest_coder_log
            initial_video_log = latest_video_log

        print("\n--- Automated Routing Test Complete ---")

if __name__ == "__main__":
    # Ensure the logs directory exists
    os.makedirs(os.path.dirname(HOST_AGENT_LOG_PATH), exist_ok=True)
    # Clear previous logs for a clean test run
    for log_file in [HOST_AGENT_LOG_PATH, CODER_AGENT_LOG_PATH, VIDEO_AGENT_LOG_PATH]:
        if os.path.exists(log_file):
            open(log_file, 'w').close() # Clear content

    asyncio.run(run_test())
