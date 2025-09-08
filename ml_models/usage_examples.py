"""
Usage Examples for the PM Internship Recommendation Engine
"""

from simple_recommendation_engine import SimpleInternshipRecommendationEngine

def example_1_basic_usage():
    """Basic usage example."""
    print("="*50)
    print("EXAMPLE 1: Basic Usage")
    print("="*50)
    
    # Initialize the engine
    engine = SimpleInternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    # Get recommendations for the first candidate
    engine.display_recommendations(0, top_k=3)

def example_2_multiple_candidates():
    """Show recommendations for multiple candidates."""
    print("\n" + "="*50)
    print("EXAMPLE 2: Multiple Candidates")
    print("="*50)
    
    engine = SimpleInternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    # Show recommendations for first 3 candidates
    for i in range(3):
        engine.display_recommendations(i, top_k=2)

def example_3_custom_candidate():
    """Example showing how to work with candidate data."""
    print("\n" + "="*50)
    print("EXAMPLE 3: Working with Candidate Data")
    print("="*50)
    
    engine = SimpleInternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    # Show information about candidates
    print(f"Total candidates in database: {len(engine.candidates_df)}")
    print(f"Total jobs in database: {len(engine.jobs_df)}")
    
    # Show first few candidates
    print("\nFirst 3 candidates:")
    for i in range(3):
        candidate = engine.candidates_df.iloc[i]
        print(f"  Candidate {i+1}: {candidate['skills'][:50]}...")

def example_4_programmatic_access():
    """Example of programmatic access to recommendations."""
    print("\n" + "="*50)
    print("EXAMPLE 4: Programmatic Access")
    print("="*50)
    
    engine = SimpleInternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    # Get recommendations programmatically
    candidate_idx = 0
    recommendations = engine.recommend(candidate_idx, top_k=3)
    
    print(f"Recommendations for candidate {candidate_idx}:")
    for i, (job_idx, score) in enumerate(recommendations):
        job_details = engine.get_job_details(job_idx)
        print(f"  {i+1}. {job_details['job_title']} at {job_details['company']} (score: {score:.3f})")

def example_5_fairness_awareness():
    """Example showing fairness features."""
    print("\n" + "="*50)
    print("EXAMPLE 5: Fairness Awareness")
    print("="*50)
    
    print("""
The recommendation system applies a 5% boost to scores
for candidates from underrepresented groups to ensure
equitable opportunity distribution.

This is implemented as a simple multiplier in the 
recommendation algorithm, but in a production system
it would be based on specific demographic data.
    """)

def main():
    """Run all examples."""
    print("PM Internship Recommendation Engine - Usage Examples")
    print("="*50)
    
    example_1_basic_usage()
    example_2_multiple_candidates()
    example_3_custom_candidate()
    example_4_programmatic_access()
    example_5_fairness_awareness()
    
    print("\n" + "="*50)
    print("END OF EXAMPLES")
    print("="*50)

if __name__ == "__main__":
    main()