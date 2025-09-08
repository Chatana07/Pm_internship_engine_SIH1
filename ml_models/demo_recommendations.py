"""
Demo script for the PM Internship Recommendation Engine
"""

from recommendation_engine import InternshipRecommendationEngine

def main():
    # Initialize the recommendation engine
    print("Initializing Recommendation Engine...")
    engine = InternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    # Show some candidate examples
    print("\n" + "="*60)
    print("PM Internship Recommendation System Demo")
    print("="*60)
    
    # Display a few candidates
    print("\nSample Candidates:")
    for i in range(3):
        candidate = engine.candidates_df.iloc[i]
        print(f"\nCandidate {i+1}:")
        print(f"  Skills: {candidate['skills']}")
        print(f"  Qualification: {candidate['qualification']}")
        print(f"  Experience: {candidate['experience_level']}")
        print(f"  Preferred Role: {candidate['job_role']}")
    
    # Get recommendations for multiple candidates
    print("\n" + "="*60)
    print("Generating Recommendations...")
    print("="*60)
    
    # Recommend for first 3 candidates
    for i in range(3):
        engine.display_recommendations(i, top_k=3)
    
    print("\n" + "="*60)
    print("Training Model for Better Recommendations...")
    print("="*60)
    
    # Train the model for better recommendations
    engine.train_model(sample_size=500)
    
    print("\n" + "="*60)
    print("Recommendations with Trained Model:")
    print("="*60)
    
    # Show improved recommendations with trained model
    for i in range(2):
        candidate = engine.candidates_df.iloc[i]
        print(f"\nRecommendations for Candidate {i+1} (with trained model):")
        print(f"Skills: {candidate['skills']}")
        print("-" * 50)
        
        # Get recommendations using the trained model
        recommendations = engine.recommend(i, top_k=3, use_model=True)
        
        for j, (job_idx, score) in enumerate(recommendations):
            job_details = engine.get_job_details(job_idx)
            print(f"{j+1}. {job_details['job_title']}")
            print(f"   Company: {job_details['company']}")
            print(f"   Location: {job_details['location']}")
            print(f"   Salary: {job_details['salary']}")
            print(f"   Match Score: {score:.4f}")
            print()

if __name__ == "__main__":
    main()