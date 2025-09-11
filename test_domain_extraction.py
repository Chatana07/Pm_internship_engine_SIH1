import sys
import os

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from job_recommender import JobRecommender

def test_domain_extraction():
    # Test cases for domain extraction
    test_cases = [
        "full stack developer",
        "react developer",
        "web developer",
        "data scientist",
        "data analyst",
        "quality assurance tester",
        "application tester",
        "business development executive",
        "growth catalyst",
        "insurance consultant"
    ]
    
    # Initialize recommender
    recommender = JobRecommender(
        jobs_dataset_path='dataset/Jobs_cleaned.csv',
        model_path='ml_models/jobs_matcher_model.joblib'
    )
    
    print("Testing domain extraction:")
    print("=" * 50)
    
    for job_title in test_cases:
        domain = recommender._extract_domain_from_role(job_title)
        print(f"Job Title: {job_title:<30} -> Domain: {domain}")

if __name__ == "__main__":
    test_domain_extraction()