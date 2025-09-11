import sys
import os

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from job_recommender import JobRecommender

def test_job_recommendations():
    # Initialize recommender
    recommender = JobRecommender(
        jobs_dataset_path='dataset/Jobs_cleaned.csv',
        model_path='ml_models/jobs_matcher_model.joblib'
    )
    
    # Test case 1: Web Development domain
    print("Testing Web Development domain recommendations:")
    print("=" * 60)
    
    recommendations = recommender.get_recommendations(
        skills="Python, React, JavaScript",
        location="remote",
        experience="0-2 years"
    )
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\nRECOMMENDATION #{i}")
        print(f"Company: {rec['company_name']}")
        print(f"Job Title: {rec['job_title']}")
        print(f"Domain: {rec['domain']}")
        print(f"Location: {rec['location']}")
        print(f"Salary: {rec['salary']}")
        print(f"Experience Required: {rec['experience_required']}")
        print(f"Similarity Score: {rec['similarity_score']:.2f}")
        print(f"Why Recommended: {rec['reason']}")
        print("-" * 40)
    
    # Test case 2: Data Science domain
    print("\n\nTesting Data Science domain recommendations:")
    print("=" * 60)
    
    recommendations = recommender.get_recommendations(
        skills="Python, Machine Learning, Data Analysis",
        location="bangalore",
        experience="0-2 years"
    )
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\nRECOMMENDATION #{i}")
        print(f"Company: {rec['company_name']}")
        print(f"Job Title: {rec['job_title']}")
        print(f"Domain: {rec['domain']}")
        print(f"Location: {rec['location']}")
        print(f"Salary: {rec['salary']}")
        print(f"Experience Required: {rec['experience_required']}")
        print(f"Similarity Score: {rec['similarity_score']:.2f}")
        print(f"Why Recommended: {rec['reason']}")
        print("-" * 40)

if __name__ == "__main__":
    test_job_recommendations()