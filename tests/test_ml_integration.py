"""
Test script to verify ML model integration with the internship matching system
"""

import sys
import os
import json

# Add the project root and ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_models'))

def test_ml_internship_matcher():
    """Test the MLInternshipMatcher class."""
    try:
        from ml_models.ml_internship_matcher import MLInternshipMatcher
        
        # Get the root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Construct paths to dataset files
        user_dataset_path = os.path.join(root_dir, 'dataset', 'Candidates_cleaned.csv')
        internship_dataset_path = os.path.join(root_dir, 'dataset', 'Jobs_cleaned.csv')
        
        # Check if dataset files exist
        if not os.path.exists(user_dataset_path):
            print(f"User dataset not found at: {user_dataset_path}")
            return False
            
        if not os.path.exists(internship_dataset_path):
            print(f"Internship dataset not found at: {internship_dataset_path}")
            return False
        
        # Initialize the ML matcher
        print("Initializing MLInternshipMatcher...")
        ml_matcher = MLInternshipMatcher(
            user_dataset_path=user_dataset_path,
            internship_dataset_path=internship_dataset_path
        )
        
        # Train the model
        print("Training model...")
        ml_matcher.train_model()
        
        # Test getting recommendations for a user
        print("Testing recommendations for user ID 1...")
        recommendations = ml_matcher.get_recommendations(user_id=1, top_k=3)
        
        print(f"Found {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['role']} at {rec['company']} ({rec['location']}) - Score: {rec['similarity_score']:.2f}")
        
        # Test with a user profile
        print("\nTesting recommendations for a sample user profile...")
        user_profile = {
            'skills': 'Python, Machine Learning, Data Analysis',
            'preferred_domain': 'Data Science',
            'preferred_location': 'Bangalore',
            'education': 'B.Tech',
            'experience': '0-2 years'
        }
        
        profile_recommendations = ml_matcher.get_recommendations_for_profile(user_profile, top_k=3)
        
        print(f"Found {len(profile_recommendations)} recommendations for profile:")
        for i, rec in enumerate(profile_recommendations, 1):
            print(f"  {i}. {rec['role']} at {rec['company']} ({rec['location']}) - Score: {rec['similarity_score']:.2f}")
        
        # Save the model
        model_path = os.path.join(root_dir, 'ml_models', 'internship_matcher_model.joblib')
        print(f"Saving model to {model_path}...")
        ml_matcher.save_model(model_path)
        
        # Test loading the model
        print("Testing model loading...")
        ml_matcher.load_model(model_path)
        
        print("✅ MLInternshipMatcher test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing MLInternshipMatcher: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_job_recommender():
    """Test the JobRecommender class."""
    try:
        from ml_models.job_recommender import JobRecommender
        
        # Get the root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Construct paths to dataset and model files
        jobs_dataset_path = os.path.join(root_dir, 'dataset', 'Jobs_cleaned.csv')
        model_path = os.path.join(root_dir, 'ml_models', 'jobs_matcher_model.joblib')
        
        # Check if files exist
        if not os.path.exists(jobs_dataset_path):
            print(f"Jobs dataset not found at: {jobs_dataset_path}")
            return False
            
        if not os.path.exists(model_path):
            print(f"Model file not found at: {model_path}")
            print("Please run the jobs_matcher.py script to train and save the model first.")
            return False
        
        # Initialize the job recommender
        print("Initializing JobRecommender...")
        recommender = JobRecommender(
            jobs_dataset_path=jobs_dataset_path,
            model_path=model_path
        )
        
        # Test getting recommendations
        print("Testing job recommendations...")
        recommendations = recommender.get_recommendations(
            skills="Python, Machine Learning, Data Analysis",
            location="Bangalore",
            experience="0-2 years",
            top_k=3
        )
        
        print(f"Found {len(recommendations)} job recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['job_title']} at {rec['company_name']} ({rec['location']}) - Score: {rec['similarity_score']:.2f}")
        
        print("✅ JobRecommender test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing JobRecommender: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running ML Model Integration Tests...\n")
    
    # Test MLInternshipMatcher
    print("=" * 50)
    print("Testing MLInternshipMatcher...")
    print("=" * 50)
    ml_test_result = test_ml_internship_matcher()
    
    print("\n")
    
    # Test JobRecommender
    print("=" * 50)
    print("Testing JobRecommender...")
    print("=" * 50)
    job_test_result = test_job_recommender()
    
    print("\n")
    print("=" * 50)
    print("Test Summary:")
    print("=" * 50)
    print(f"MLInternshipMatcher: {'✅ PASS' if ml_test_result else '❌ FAIL'}")
    print(f"JobRecommender: {'✅ PASS' if job_test_result else '❌ FAIL'}")
    
    if ml_test_result and job_test_result:
        print("\n🎉 All tests passed! ML models are successfully integrated.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")