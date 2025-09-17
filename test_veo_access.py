#!/usr/bin/env python3
import os
from google import genai

# Set environment variables
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'TRUE'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'cedricgpt-380318'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

try:
    client = genai.Client()
    print("✅ GenAI client initialized successfully")
    
    # Try to list models
    try:
        models = client.models.list()
        print(f"📋 Available models: {len(list(models))}")
        
        # Look for VEO models
        veo_models = [m for m in client.models.list() if 'veo' in m.name.lower()]
        if veo_models:
            print(f"🎬 Found VEO models: {[m.name for m in veo_models]}")
        else:
            print("❌ No VEO models found")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        
except Exception as e:
    print(f"❌ Error initializing GenAI client: {e}")
