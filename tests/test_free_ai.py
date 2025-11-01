#!/usr/bin/env python3
"""
Test Free AI Models
Test Hugging Face models that work without authentication.
"""

import requests
import json

def test_free_models():
    """Test free Hugging Face models."""
    print("🤖 Testing FREE AI Models (No Token Required)")
    print("=" * 50)
    
    # Models that work without authentication
    free_models = [
        "microsoft/DialoGPT-medium",
        "distilgpt2", 
        "gpt2",
        "facebook/blenderbot-400M-distill"
    ]
    
    test_message = "Hello! How can I help with studying?"
    
    for model in free_models:
        print(f"\n🧪 Testing model: {model}")
        print("-" * 30)
        
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            
            # Prepare input based on model type
            if "DialoGPT" in model:
                inputs = f"Human: {test_message}\nBot:"
            elif "blenderbot" in model:
                inputs = test_message
            else:
                inputs = f"Question: {test_message}\nAnswer:"
            
            payload = {
                "inputs": inputs,
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            # No authorization header - using free tier
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                if isinstance(result, list) and len(result) > 0:
                    generated = result[0].get("generated_text", "").strip()
                    print(f"Response: {generated}")
                else:
                    print(f"Raw result: {result}")
                    
            elif response.status_code == 503:
                print("⏳ Model is loading...")
                
            elif response.status_code == 429:
                print("⚠️ Rate limited - too many requests")
                
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_simple_model():
    """Test the simplest model that should work."""
    print("\n\n🚀 Testing Simplest Model")
    print("=" * 30)
    
    try:
        url = "https://api-inference.huggingface.co/models/gpt2"
        
        payload = {
            "inputs": "The Student Tracking System helps students by",
            "parameters": {
                "max_length": 100,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ GPT-2 is working!")
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get("generated_text", "")
                print(f"Generated text: {generated}")
            
        else:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_free_models()
    test_simple_model()
    
    print("\n\n💡 Summary:")
    print("- Free models work without API tokens")
    print("- Some models may be loading (503 error)")  
    print("- Rate limits may apply (429 error)")
    print("- GPT-2 is usually the most reliable free model")
