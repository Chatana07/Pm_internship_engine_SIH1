"""
Comprehensive Demo of the PM Internship Recommendation System
"""

import pandas as pd
from simple_recommendation_engine import SimpleInternshipRecommendationEngine

def analyze_dataset():
    """Analyze the dataset to understand its characteristics."""
    print("="*60)
    print("DATASET ANALYSIS")
    print("="*60)
    
    # Load datasets
    candidates = pd.read_csv('dataset/Candidates_cleaned.csv')
    jobs = pd.read_csv('dataset/Jobs_cleaned.csv')
    
    print(f"Total Candidates: {len(candidates)}")
    print(f"Total Jobs: {len(jobs)}")
    
    # Sample candidate skills
    print("\nSample Candidate Skills:")
    for i in range(3):
        print(f"  Candidate {i+1}: {candidates.iloc[i]['skills']}")
    
    # Sample job titles
    print("\nSample Job Titles:")
    for i in range(3):
        print(f"  Job {i+1}: {jobs.iloc[i]['Type_of_job']} at {jobs.iloc[i]['company_name']}")

def demonstrate_recommendations():
    """Demonstrate the recommendation system."""
    print("\n" + "="*60)
    print("RECOMMENDATION DEMO")
    print("="*60)
    
    # Initialize the recommendation engine
    engine = SimpleInternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    # Show recommendations for different types of candidates
    candidate_types = [
        (0, "Data Science Candidate"),
        (1, "Frontend Developer"),
        (10, "Business Development")
    ]
    
    for idx, description in candidate_types:
        if idx < len(engine.candidates_df):
            candidate = engine.candidates_df.iloc[idx]
            print(f"\n{description}:")
            print(f"  Skills: {candidate['skills']}")
            print(f"  Qualification: {candidate['qualification']}")
            print(f"  Experience: {candidate['experience_level']}")
            
            # Get recommendations
            recommendations = engine.recommend(idx, top_k=3)
            print("  Top Recommendations:")
            for i, (job_idx, score) in enumerate(recommendations):
                job = engine.get_job_details(job_idx)
                print(f"    {i+1}. {job['job_title']} at {job['company']} ({score:.3f})")

def show_fairness_features():
    """Demonstrate fairness features."""
    print("\n" + "="*60)
    print("FAIRNESS FEATURES")
    print("="*60)
    
    print("""
The recommendation system incorporates several fairness features:

1. SCORE BOOSTING:
   - 5% score boost for candidates from underrepresented groups
   - Helps ensure equitable opportunity distribution

2. DIVERSE RECOMMENDATIONS:
   - System considers location preferences
   - Balances urban/rural candidate needs

3. TRANSPARENCY:
   - Clear match scores for each recommendation
   - Explainable recommendation process
    """)

def show_system_benefits():
    """Show the benefits of the system."""
    print("\n" + "="*60)
    print("SYSTEM BENEFITS")
    print("="*60)
    
    benefits = {
        "Lightweight": "Fast inference with minimal compute requirements",
        "Scalable": "Handles thousands of candidates and jobs efficiently",
        "Mobile-Friendly": "Simple interface suitable for low digital literacy users",
        "Fairness-Aware": "Incorporates affirmative action considerations",
        "Interpretable": "Clear scoring and ranking explanations"
    }
    
    for benefit, description in benefits.items():
        print(f"\n{benefit}:")
        print(f"  {description}")

def main():
    """Main demo function."""
    print("PM Internship Recommendation System")
    print("===================================")
    print("This system helps match candidates with suitable internships")
    print("based on their skills, qualifications, and preferences.")
    
    # Analyze dataset
    analyze_dataset()
    
    # Demonstrate recommendations
    demonstrate_recommendations()
    
    # Show fairness features
    show_fairness_features()
    
    # Show system benefits
    show_system_benefits()
    
    print("\n" + "="*60)
    print("TECHNICAL SPECIFICATIONS")
    print("="*60)
    print("""
Algorithm: TF-IDF + Cosine Similarity
- Converts skills and job descriptions to numerical vectors
- Computes similarity scores between candidates and jobs
- Ranks jobs by relevance to candidate profile

Performance:
- Sub-second inference time per candidate
- Memory efficient implementation
- Handles datasets with thousands of jobs

Requirements:
- Python 3.7+
- scikit-learn
- pandas
- numpy
    """)

if __name__ == "__main__":
    main()