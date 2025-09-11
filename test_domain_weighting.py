import sys
import os

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from ml_internship_matcher import MLInternshipMatcher

def test_domain_weighting():
    # Initialize matcher with dataset paths
    matcher = MLInternshipMatcher(
        user_dataset_path='dataset/Candidates_cleaned.csv',
        internship_dataset_path='dataset/Jobs_cleaned.csv'
    )
    
    # Train the model
    matcher.train_model()
    
    # Test case: User with Web Development domain preference
    user_profile = {
        'name': 'Test User',
        'skills': 'Python, React, JavaScript',
        'preferred_domain': 'Web Development',
        'preferred_location': 'remote',
        'education': 'BCA'
    }
    
    print("Testing Web Development domain preference weighting:")
    print("=" * 60)
    
    recommendations = matcher.get_recommendations_for_profile(user_profile, 5)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\nRECOMMENDATION #{i}")
        print(f"Company: {rec['company']}")
        print(f"Role: {rec['role']}")
        print(f"Domain: {rec['domain']}")
        print(f"Location: {rec['location']}")
        print(f"Stipend: {rec['stipend']}")
        print(f"Similarity Score: {rec['similarity_score']:.2f}")
        print(f"Why Recommended: {rec['reason']}")
        print("-" * 40)

if __name__ == "__main__":
    test_domain_weighting()