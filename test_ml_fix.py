#!/usr/bin/env python3
"""
Test script for the fixed ML-based internship matcher
"""

import sys
import os

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from ml_models.ml_internship_matcher import MLInternshipMatcher

def test_ml_model():
    """Test the ML model functionality with the fixed implementation."""
    print("Testing Fixed ML-based Internship Matcher...")
    
    # Initialize matcher
    matcher = MLInternshipMatcher(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    print(f"Loaded {len(matcher.users_df)} users and {len(matcher.internships_df)} internships")
    
    # Test with a Data Science user profile
    print("\n" + "="*60)
    print("TESTING DATA SCIENCE USER PROFILE")
    print("="*60)
    
    user_profile = {
        'name': 'Ankit Mondal',
        'education': 'B.Sc',
        'skills': 'SQL, Python',
        'preferred_domain': 'Data Science',
        'preferred_location': 'Remote',
        'internship_duration': '12 Months',
        'enrollment_status': 'Remote/Online'
    }
    
    print(f"User Profile: {user_profile}")
    
    # Get recommendations
    print("\n🔍 Finding the best internships for you...")
    try:
        recommendations = matcher.get_recommendations_for_profile(user_profile, 3)
        print(f"Found {len(recommendations)} recommendations")
        
        if recommendations:
            print("\nTop Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec.get('company', 'N/A')} - {rec.get('role', 'N/A')}")
                print(f"   Domain: {rec.get('domain', 'N/A')}")
                print(f"   Location: {rec.get('location', 'N/A')}")
                print(f"   Duration: {rec.get('duration', 'N/A')}")
                print(f"   Score: {rec.get('similarity_score', 0):.3f}")
                print(f"   Reason: {rec.get('reason', 'N/A')}")
        else:
            print("No recommendations found")
            
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        import traceback
        traceback.print_exc()

    # Test with a Web Development user profile
    print("\n" + "="*60)
    print("TESTING WEB DEVELOPMENT USER PROFILE")
    print("="*60)
    
    user_profile_web = {
        'name': 'John Developer',
        'education': 'BCA',
        'skills': 'Python, JavaScript, HTML',
        'preferred_domain': 'Web Development',
        'preferred_location': 'Bangalore',
        'internship_duration': '6 Months',
        'enrollment_status': 'Remote/Online'
    }
    
    print(f"User Profile: {user_profile_web}")
    
    # Get recommendations
    print("\n🔍 Finding the best internships for you...")
    try:
        recommendations = matcher.get_recommendations_for_profile(user_profile_web, 3)
        print(f"Found {len(recommendations)} recommendations")
        
        if recommendations:
            print("\nTop Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec.get('company', 'N/A')} - {rec.get('role', 'N/A')}")
                print(f"   Domain: {rec.get('domain', 'N/A')}")
                print(f"   Location: {rec.get('location', 'N/A')}")
                print(f"   Duration: {rec.get('duration', 'N/A')}")
                print(f"   Score: {rec.get('similarity_score', 0):.3f}")
                print(f"   Reason: {rec.get('reason', 'N/A')}")
        else:
            print("No recommendations found")
            
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ml_model()