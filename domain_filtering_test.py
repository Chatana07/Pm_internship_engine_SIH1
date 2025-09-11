import sys
import os

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from job_recommender import JobRecommender

def test_domain_filtering():
    print("TESTING DOMAIN FILTERING IMPROVEMENTS")
    print("=" * 50)
    
    # Initialize recommender
    recommender = JobRecommender(
        jobs_dataset_path='dataset/Jobs_cleaned.csv',
        model_path='ml_models/jobs_matcher_model.joblib'
    )
    
    # Test case: Web Development skills should prioritize Web Development jobs
    print("\n1. Testing Web Development Skills")
    print("-" * 30)
    
    recommendations = recommender.get_recommendations(
        skills="Python, Html, Css, Sql, Angular, Communication",
        location="remote",
        experience="0-2 years"
    )
    
    # Count how many Web Development jobs are in top recommendations
    web_dev_count = 0
    for rec in recommendations:
        if rec['domain'] == 'Web Development':
            web_dev_count += 1
    
    print(f"Web Development jobs in top {len(recommendations)} recommendations: {web_dev_count}")
    
    # Display all recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['company_name']} - {rec['job_title']}")
        print(f"   Domain: {rec['domain']}")
        print(f"   Score: {rec['similarity_score']:.2f}")
        print(f"   Why Recommended: {rec['reason']}")
    
    # Test case: Data Science skills should prioritize Data Science jobs
    print("\n\n2. Testing Data Science Skills")
    print("-" * 30)
    
    recommendations = recommender.get_recommendations(
        skills="Python, Machine Learning, Data Analysis, Statistics",
        location="bangalore",
        experience="0-2 years"
    )
    
    # Count how many Data Science jobs are in top recommendations
    data_sci_count = 0
    for rec in recommendations:
        if rec['domain'] == 'Data Science':
            data_sci_count += 1
    
    print(f"Data Science jobs in top {len(recommendations)} recommendations: {data_sci_count}")
    
    # Display all recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['company_name']} - {rec['job_title']}")
        print(f"   Domain: {rec['domain']}")
        print(f"   Score: {rec['similarity_score']:.2f}")
        print(f"   Why Recommended: {rec['reason']}")

if __name__ == "__main__":
    test_domain_filtering()