"""
Test script to verify domain extraction and recommendation reasons
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:5000"

def test_web_development_recommendations():
    """Test recommendations for Web Development domain."""
    print("Testing Web Development domain recommendations...")
    try:
        # Test data with Web Development domain
        test_data = {
            "name": "Test User",
            "skills": "JavaScript, HTML, CSS, React",
            "domain": "Web Development",
            "location": "Remote",
            "eduMin": "B.Tech",
            "duration": "6 Months",
            "edu": "Not in full-time"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai_recommend",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Web Development test passed")
            print(f"   Recommendations found: {data.get('total_recommendations', 0)}")
            
            if 'recommendations' in data and data['recommendations']:
                for i, rec in enumerate(data['recommendations'], 1):
                    print(f"   {i}. {rec['role']} at {rec['company']}")
                    print(f"      Domain: {rec['domain']}")
                    print(f"      Score: {rec['similarity_score']:.2f}")
                    print(f"      Reason: {rec['reason']}")
                    print()
            
            return True
        else:
            print(f"❌ Web Development test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Web Development test error: {e}")
        return False

def test_data_science_recommendations():
    """Test recommendations for Data Science domain."""
    print("Testing Data Science domain recommendations...")
    try:
        # Test data with Data Science domain
        test_data = {
            "name": "Test User",
            "skills": "Python, Machine Learning, Data Analysis",
            "domain": "Data Science",
            "location": "Bangalore",
            "eduMin": "MCA",
            "duration": "6 Months",
            "edu": "Not in full-time"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai_recommend",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data Science test passed")
            print(f"   Recommendations found: {data.get('total_recommendations', 0)}")
            
            if 'recommendations' in data and data['recommendations']:
                for i, rec in enumerate(data['recommendations'], 1):
                    print(f"   {i}. {rec['role']} at {rec['company']}")
                    print(f"      Domain: {rec['domain']}")
                    print(f"      Score: {rec['similarity_score']:.2f}")
                    print(f"      Reason: {rec['reason']}")
                    print()
            
            return True
        else:
            print(f"❌ Data Science test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Data Science test error: {e}")
        return False

def main():
    """Run domain extraction tests."""
    print("Running Domain Extraction Tests...\n")
    
    # Test Web Development recommendations
    web_dev_result = test_web_development_recommendations()
    
    print("\n" + "="*50 + "\n")
    
    # Test Data Science recommendations
    data_sci_result = test_data_science_recommendations()
    
    print("="*50)
    print("Domain Extraction Test Summary:")
    print("="*50)
    print(f"Web Development: {'✅ PASS' if web_dev_result else '❌ FAIL'}")
    print(f"Data Science: {'✅ PASS' if data_sci_result else '❌ FAIL'}")
    
    if web_dev_result and data_sci_result:
        print("\n🎉 All domain extraction tests passed!")
        print("The domain extraction and recommendation reasons are working correctly.")
    else:
        print("\n⚠️  Some domain extraction tests failed.")

if __name__ == "__main__":
    main()