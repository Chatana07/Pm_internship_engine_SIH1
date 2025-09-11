import sys
import os

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from ml_internship_matcher import MLInternshipMatcher

def final_test():
    # Initialize matcher with dataset paths
    matcher = MLInternshipMatcher(
        user_dataset_path='dataset/Candidates_cleaned.csv',
        internship_dataset_path='dataset/Jobs_cleaned.csv'
    )
    
    # Train the model
    matcher.train_model()
    
    # Test case 1: User with Web Development domain preference
    print("TEST CASE 1: Web Development Domain Preference")
    print("=" * 60)
    
    user_profile_web_dev = {
        'name': 'Web Dev User',
        'skills': 'Python, React, JavaScript, HTML, CSS',
        'preferred_domain': 'Web Development',
        'preferred_location': 'remote',
        'education': 'BCA'
    }
    
    recommendations = matcher.get_recommendations_for_profile(user_profile_web_dev, 3)
    
    print(f"User Profile: {user_profile_web_dev['name']}")
    print(f"Preferred Domain: {user_profile_web_dev['preferred_domain']}")
    print(f"Skills: {user_profile_web_dev['skills']}")
    print("\nRecommendations:")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['company']} - {rec['role']}")
        print(f"   Domain: {rec['domain']}")
        print(f"   Location: {rec['location']}")
        print(f"   Stipend: {rec['stipend']}")
        print(f"   Score: {rec['similarity_score']:.2f}")
        print(f"   Why Recommended: {rec['reason']}")
    
    # Test case 2: User with Data Science domain preference
    print("\n\nTEST CASE 2: Data Science Domain Preference")
    print("=" * 60)
    
    user_profile_data_sci = {
        'name': 'Data Science User',
        'skills': 'Python, Machine Learning, Data Analysis, Statistics',
        'preferred_domain': 'Data Science',
        'preferred_location': 'bangalore',
        'education': 'B.Tech'
    }
    
    recommendations = matcher.get_recommendations_for_profile(user_profile_data_sci, 3)
    
    print(f"User Profile: {user_profile_data_sci['name']}")
    print(f"Preferred Domain: {user_profile_data_sci['preferred_domain']}")
    print(f"Skills: {user_profile_data_sci['skills']}")
    print("\nRecommendations:")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['company']} - {rec['role']}")
        print(f"   Domain: {rec['domain']}")
        print(f"   Location: {rec['location']}")
        print(f"   Stipend: {rec['stipend']}")
        print(f"   Score: {rec['similarity_score']:.2f}")
        print(f"   Why Recommended: {rec['reason']}")

if __name__ == "__main__":
    final_test()