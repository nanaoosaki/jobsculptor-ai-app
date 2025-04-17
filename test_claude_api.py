#!/usr/bin/env python3

import os
import traceback
from dotenv import load_dotenv
from anthropic import Anthropic

def test_claude_api():
    """Test the Claude API connection with a simple request"""
    print("Claude API Test Script")
    print("=====================")
    
    # Load environment variables from .env file
    print("Loading .env file...")
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("ERROR: CLAUDE_API_KEY not found in .env file")
        return False
    
    print(f"API key found (starts with): {api_key[:5]}...")
    
    try:
        # Initialize client
        print("Initializing Anthropic client...")
        client = Anthropic(api_key=api_key)
        
        # Send a simple message
        print("Sending test request to Claude API...")
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            messages=[
                {"role": "user", "content": "Please confirm this API test is working by saying hello."}
            ]
        )
        
        # Check response
        print("\n=== SUCCESS: API is working! ===")
        print(f"Response: {response.content[0].text}")
        print(f"Model: {response.model}")
        print(f"Input tokens: {response.usage.input_tokens}")
        print(f"Output tokens: {response.usage.output_tokens}")
        print(f"Total tokens: {response.usage.input_tokens + response.usage.output_tokens}")
        return True
        
    except Exception as e:
        print("\n=== ERROR: API test failed ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        print("\nThis suggests your API key may be invalid or there's a network issue.")
        return False

if __name__ == "__main__":
    test_claude_api() 