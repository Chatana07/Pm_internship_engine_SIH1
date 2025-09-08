import requests
import json

# Test data
test_data = {
    "name": "John Doe",
    "citizenship": "Indian",
    "age": 22,
    "eduMin": "BCA",
    "skills": "Python, SQL, Machine Learning",
    "domain": "Data Science",
    "location": "Remote",
    "duration": "12 Months",
    "edu": "Not in full-time",
    "income": "Up to ₹8,00,000",
    "aadhaarLink": "yes",
    "govtJob": "no"
}

try:
    # Send POST request to AI recommendation endpoint
    response = requests.post(
        'http://localhost:5000/ai_recommend',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(test_data)
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("Success! Here's the response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        
except Exception as e:
    print(f"Exception occurred: {e}")