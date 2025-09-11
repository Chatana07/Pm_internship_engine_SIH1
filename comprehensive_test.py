import sys
import os
import json

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml_models'))

from job_recommender import JobRecommender

def comprehensive_test():
    print("COMPREHENSIVE TEST OF IMPROVED ML MODEL")
    print("=" * 60)
    
    # Initialize recommender
    recommender = JobRecommender(
        jobs_dataset_path='dataset/Jobs_cleaned.csv',
        model_path='ml_models/jobs_matcher_model.joblib'
    )
    
    # Test case 1: Web Development domain
    print("\n1. TESTING WEB DEVELOPMENT DOMAIN")
    print("-" * 40)
    
    recommendations = recommender.get_recommendations(
        skills="Python, React, JavaScript, HTML, CSS",
        location="remote",
        experience="0-2 years"
    )
    
    # Check if we get Web Development jobs
    web_dev_jobs = [rec for rec in recommendations if rec['domain'] == 'Web Development']
    print(f"Found {len(web_dev_jobs)} Web Development jobs in top recommendations")
    
    # Display top 3 recommendations
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\n{i}. {rec['company_name']} - {rec['job_title']}")
        print(f"   Domain: {rec['domain']}")
        print(f"   Location: {rec['location']}")
        print(f"   Salary: {rec['salary']}")
        print(f"   Score: {rec['similarity_score']:.2f}")
        print(f"   Why Recommended: {rec['reason']}")
    
    # Test case 2: Verify domain extraction is working
    print("\n\n2. TESTING DOMAIN EXTRACTION")
    print("-" * 40)
    
    test_jobs = [
        ("full stack developer", "Web Development"),
        ("react developer", "Web Development"),
        ("data scientist", "Data Science"),
        ("quality assurance tester", "Quality Assurance"),
        ("business development executive", "Business Development"),
        ("growth catalyst", "Business Development"),
        ("insurance consultant", "Finance")
    ]
    
    all_correct = True
    for job_title, expected_domain in test_jobs:
        extracted_domain = recommender._extract_domain_from_role(job_title)
        status = "✓" if extracted_domain == expected_domain else "✗"
        print(f"{status} {job_title:<30} -> {extracted_domain} (expected: {expected_domain})")
        if extracted_domain != expected_domain:
            all_correct = False
    
    print(f"\nDomain extraction accuracy: {'100%' if all_correct else 'Needs improvement'}")
    
    # Test case 3: Verify recommendation reasons are meaningful
    print("\n\n3. TESTING RECOMMENDATION REASONS")
    print("-" * 40)
    
    # Get a recommendation with domain match
    web_dev_rec = None
    for rec in recommendations:
        if rec['domain'] == 'Web Development':
            web_dev_rec = rec
            break
    
    if web_dev_rec:
        print(f"Sample recommendation with domain match:")
        print(f"Job: {web_dev_rec['company_name']} - {web_dev_rec['job_title']}")
        print(f"Reason: {web_dev_rec['reason']}")
        
        # Check if reason includes domain expertise
        if "domain expertise" in web_dev_rec['reason']:
            print("✓ Recommendation reason includes domain expertise")
        else:
            print("✗ Recommendation reason missing domain expertise")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    comprehensive_test()