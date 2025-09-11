"""
Test script to verify API endpoints for ML model integration
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_ml_recommendations():
    """Test the ML-based recommendations endpoint."""
    print("\nTesting ML-based recommendations endpoint...")
    try:
        # Test data
        test_data = {
            "user_id": 1,
            "top_k": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/ml_recommend",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ML recommendations test passed")
            print(f"   User ID: {data['user_id']}")
            print(f"   Recommendations found: {data['total_recommendations']}")
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"   {i}. {rec['role']} at {rec['company']} ({rec['location']}) - Score: {rec.get('similarity_score', 'N/A')}")
            return True
        else:
            print(f"❌ ML recommendations test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ML recommendations test error: {e}")
        return False

def test_job_recommendations():
    """Test the job recommendations endpoint."""
    print("\nTesting job recommendations endpoint...")
    try:
        # Test data
        test_data = {
            "skills": "Python, Machine Learning, Data Analysis",
            "location": "Bangalore",
            "experience": "0-2 years",
            "top_k": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/job_recommend",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job recommendations test passed")
            print(f"   Skills: {data['user_input']['skills']}")
            print(f"   Location: {data['user_input']['location']}")
            print(f"   Experience: {data['user_input']['experience']}")
            print(f"   Recommendations found: {data['total_recommendations']}")
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"   {i}. {rec['job_title']} at {rec['company_name']} ({rec['location']}) - Score: {rec['similarity_score']:.2f}")
            return True
        else:
            print(f"❌ Job recommendations test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Job recommendations test error: {e}")
        return False

def test_ai_recommendations():
    """Test the AI recommendations endpoint."""
    print("\nTesting AI recommendations endpoint...")
    try:
        # Test data similar to what the frontend would send
        test_data = {
            "name": "Test User",
            "skills": "Python, Data Analysis, Machine Learning",
            "domain": "Data Science",
            "location": "Bangalore",
            "eduMin": "B.Tech",
            "duration": "6 Months",
            "edu": "Enrolled full-time"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai_recommend",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI recommendations test passed")
            print(f"   Recommendations found: {data.get('total_recommendations', 0)}")
            if 'recommendations' in data and data['recommendations']:
                for i, rec in enumerate(data['recommendations'], 1):
                    print(f"   {i}. {rec['role']} at {rec['company']} ({rec['location']}) - Score: {rec.get('similarity_score', 'N/A'):.2f}")
            else:
                print("   No recommendations found (this might be expected based on the model)")
            return True
        else:
            print(f"❌ AI recommendations test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI recommendations test error: {e}")
        return False

def main():
    """Run all API tests."""
    print("Running API Endpoint Tests...\n")
    
    # Test health check
    health_result = test_health_check()
    
    if health_result:
        # Test ML recommendations
        ml_result = test_ml_recommendations()
        
        # Test job recommendations
        job_result = test_job_recommendations()
        
        # Test AI recommendations
        ai_result = test_ai_recommendations()
        
        print("\n" + "="*50)
        print("API Test Summary:")
        print("="*50)
        print(f"Health Check: {'✅ PASS' if health_result else '❌ FAIL'}")
        print(f"ML Recommendations: {'✅ PASS' if ml_result else '❌ FAIL'}")
        print(f"Job Recommendations: {'✅ PASS' if job_result else '❌ FAIL'}")
        print(f"AI Recommendations: {'✅ PASS' if ai_result else '❌ FAIL'}")
        
        if all([health_result, ml_result, job_result, ai_result]):
            print("\n🎉 All API tests passed! ML models are successfully integrated with the backend.")
        else:
            print("\n⚠️  Some API tests failed. Please check the errors above.")
    else:
        print("\n❌ Health check failed. API server may not be running properly.")

if __name__ == "__main__":
    main()