#!/usr/bin/env python3
"""
Simple Hugging Face Token Test
Test if a Hugging Face token is valid and working.
"""

import requests
import json

def test_hf_token(token):
    """Test if a Hugging Face token is valid."""
    print(f"🧪 Testing Hugging Face token: {token[:8]}...")
    
    # Test with whoami endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # First try the whoami endpoint
        response = requests.get("https://huggingface.co/api/whoami", headers=headers)
        print(f"📡 Whoami response status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token is valid! User: {user_info.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Whoami failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
        # Try a simple model info request
        model_url = "https://huggingface.co/api/models/microsoft/DialoGPT-medium"
        response = requests.get(model_url, headers=headers)
        print(f"📡 Model info response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token can access model information!")
            return True
        else:
            print(f"❌ Model access failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        
    return False

def test_inference_api(token):
    """Test if token works with Inference API."""
    print("\n🤖 Testing Inference API...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple text generation model
    api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    
    payload = {
        "inputs": "Hello, how are you?",
        "parameters": {
            "max_length": 50,
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print(f"📡 Inference API response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Inference API works!")
            result = response.json()
            print(f"Response: {result}")
            return True
        else:
            print(f"❌ Inference API failed: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error testing inference API: {e}")
        
    return False

if __name__ == "__main__":
    print("🔍 Hugging Face Token Validator")
    print("=" * 40)
    
    # Test token (replace with your actual token)
    token = "hf_REPLACE_WITH_YOUR_TOKEN_HERE"
    
    print(f"Testing token: {token[:8]}...")
    
    if test_hf_token(token):
        print("✅ Token validation passed!")
        test_inference_api(token)
    else:
        print("❌ Token validation failed!")
        print("\n💡 Possible solutions:")
        print("1. Check if the token was copied correctly")
        print("2. Make sure the token has 'read' permissions")
        print("3. Verify your Hugging Face account is active")
        print("4. Try generating a new token")
        print("\n🔗 Get a new token at: https://huggingface.co/settings/tokens")
