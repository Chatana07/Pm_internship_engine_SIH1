#!/usr/bin/env python3
"""
Test script for the ML-based internship matcher
"""

from ml_models.ml_internship_matcher import MLInternshipMatcher

def test_ml_model():
    """Test the ML model functionality."""
    print("Testing ML-based Internship Matcher...")
    
    # Initialize matcher
    matcher = MLInternshipMatcher(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    print(f"Loaded {len(matcher.users_df)} users and {len(matcher.internships_df)} internships")
    
    # Train model with small sample
    print("Training model...")
    matcher.train_model(100)
    print("Model trained successfully")
    
    # Test getting recommendations
    print("Testing recommendations...")
    try:
        recommendations = matcher.get_recommendations(1, 3)
        print(f"Found {len(recommendations)} recommendations")
        
        if recommendations:
            print("First few recommendations:")
            for i, rec in enumerate(recommendations[:3]):
                print(f"  {i+1}. {rec.get('role', 'N/A')} at {rec.get('company', 'N/A')}")
                print(f"     Domain: {rec.get('domain', 'N/A')}, Location: {rec.get('location', 'N/A')}")
                print(f"     Score: {rec.get('similarity_score', 0):.3f}")
                print(f"     Reason: {rec.get('reason', 'N/A')}")
                print()
        else:
            print("No recommendations found")
            
    except Exception as e:
        print(f"Error getting recommendations: {e}")
    
    # Test with another user
    try:
        print("Testing with user ID 5...")
        recommendations2 = matcher.get_recommendations(5, 3)
        print(f"Found {len(recommendations2)} recommendations for user 5")
    except Exception as e:
        print(f"Error with user 5: {e}")

if __name__ == "__main__":
    test_ml_model()
