import requests
import json

# Test the translation service directly
def test_direct_translation():
    url = "http://localhost:5001/translate_batch"
    data = {
        "texts": ["Hello, how are you?", "This is a test translation"],
        "target_lang": "hi"
    }
    
    try:
        response = requests.post(url, json=data)
        print("Direct translation service test:")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Success! Translation result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect to translation service: {e}")

# Test the translation service through the main API server (proxy)
def test_proxy_translation():
    url = "http://localhost:5000/translate_batch"
    data = {
        "texts": ["Hello, how are you?", "This is a test translation"],
        "target_lang": "hi"
    }
    
    try:
        response = requests.post(url, json=data)
        print("\nProxy translation service test (through main API server):")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Success! Translation result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect to API server: {e}")

if __name__ == "__main__":
    print("Testing translation services...")
    test_direct_translation()
    test_proxy_translation()