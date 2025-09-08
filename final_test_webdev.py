import requests
import json

# Test the AI recommendation endpoint with a Web Development user
test_data = {
    "name": "John Developer",
    "citizenship": "Indian",
    "age": 25,
    "eduMin": "BCA",
    "skills": "Python, JavaScript, HTML",
    "domain": "Web Development",
    "location": "Bangalore",
    "duration": "6 Months",
    "edu": "Not in full-time",
    "income": "Up to ₹8,00,000",
    "aadhaarLink": "yes",
    "govtJob": "no"
}

try:
    print("Testing AI recommendation endpoint with Web Development user...")
    print(f"Sending data: {json.dumps(test_data, indent=2)}")
    
    # Send POST request to AI recommendation endpoint
    response = requests.post(
        'http://localhost:5000/ai_recommend',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(test_data)
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nSuccess! Found {result['total_recommendations']} recommendations")
        print(f"Message: {result['message']}")
        
        print("\nTop Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"\n{i}. {rec['company']} - {rec['role']}")
            print(f"   Domain: {rec['domain']}")
            print(f"   Location: {rec['location']}")
            print(f"   Duration: {rec['duration']}")
            print(f"   Score: {rec['similarity_score']:.3f}")
            print(f"   Reason: {rec['reason']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Exception occurred: {e}")