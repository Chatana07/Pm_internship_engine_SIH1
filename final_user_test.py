import sys
import os

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from ml_internship_matcher import MLInternshipMatcher

def final_user_test():
    print("FINAL USER TEST - Sanchita Das Scenario")
    print("=" * 50)
    
    # Initialize matcher with dataset paths
    matcher = MLInternshipMatcher(
        user_dataset_path='dataset/Candidates_cleaned.csv',
        internship_dataset_path='dataset/Jobs_cleaned.csv'
    )
    
    # Train the model
    matcher.train_model()
    
    # User profile matching Sanchita Das
    user_profile = {
        'name': 'Sanchita Das',
        'education': 'BCA',
        'skills': 'Python, Html, Css, Sql, Angular, Communication',
        'preferred_domain': 'Web Development',
        'preferred_location': 'Remote'
    }
    
    print(f"User Profile:")
    print(f"Name: {user_profile['name']}")
    print(f"Education: {user_profile['education']}")
    print(f"Skills: {user_profile['skills']}")
    print(f"Preferred Domain: {user_profile['preferred_domain']}")
    print(f"Preferred Location: {user_profile['preferred_location']}")
    print(f"\nFinding best 3 internships...")
    print("-" * 50)
    
    recommendations = matcher.get_recommendations_for_profile(user_profile, 3)
    
    print(f"Found {len(recommendations)} internships matching your criteria.\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['company']} - {rec['role']}")
        print(f"   Score: {rec['similarity_score']:.1f}%")
        print(f"   Domain: {rec['domain']}")
        print(f"   Location: {rec['location']}")
        print(f"   Type: {rec['type']}")
        print(f"   Duration: {rec['duration']}")
        print(f"   Stipend: {rec['stipend']}")
        print(f"   Why Recommended: {rec['reason']}")
        print()

if __name__ == "__main__":
    final_user_test()