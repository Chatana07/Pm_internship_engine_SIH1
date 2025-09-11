"""
ML-based job matching system that works with your jobs dataset
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import re
import os
from typing import List, Dict

class JobsMatcher:
    """ML-based job matching engine for your jobs dataset."""
    
    def __init__(self, jobs_dataset_path: str, model_path: str = None):
        """
        Initialize the jobs matcher.
        
        Args:
            jobs_dataset_path: Path to your jobs dataset CSV file
            model_path: Path to pre-trained model joblib file (optional)
        """
        self.jobs_dataset_path = os.path.abspath(jobs_dataset_path)
        self.jobs_df = None
        self.model = None
        self.vectorizers = {}
        
        # Regularization parameters
        self.max_features = 100
        self.min_df = 2
        self.max_df = 0.8
        self.regularization_strength = 0.05
        self.ngram_range = (1, 2)
        
        # Load jobs dataset
        self.load_jobs_dataset()
        
        # Load model if provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_jobs_dataset(self):
        """Load the jobs dataset from CSV file."""
        try:
            print(f"Loading jobs dataset from: {self.jobs_dataset_path}")
            self.jobs_df = pd.read_csv(self.jobs_dataset_path)
            print(f"Loaded {len(self.jobs_df)} jobs")
            
            # Display column information
            print("Dataset columns:", self.jobs_df.columns.tolist())
        except Exception as e:
            print(f"Error loading jobs dataset: {e}")
            raise
    
    def _preprocess_data(self):
        """Preprocess jobs data for ML training."""
        # Create features for jobs
        job_features = self.jobs_df.copy()
        
        # Add numerical salary values
        job_features['salary_value'] = job_features['salary'].apply(self._parse_salary)
        
        return job_features
    
    def _parse_salary(self, salary: str) -> float:
        """Parse salary string to numerical value."""
        if pd.isna(salary):
            return 0.0
        try:
            # Extract numbers from salary string (e.g., "₹ 2 - 2.5 lpa" -> average of 2 and 2.5)
            numbers = re.findall(r'\d+\.?\d*', str(salary))
            if numbers:
                # Return average if range, otherwise the single value
                nums = [float(n) for n in numbers]
                return sum(nums) / len(nums)
        except:
            pass
        return 0.0
    
    def _create_features(self, job_features):
        """Create feature vectors for jobs."""
        # Combine text features for vectorization
        job_texts = (
            job_features['Type_of_job'].fillna('') + ' ' +
            job_features['company_name'].fillna('') + ' ' +
            job_features['location'].fillna('')
        )
        
        # Vectorize text features with regularization parameters
        tfidf = TfidfVectorizer(
            max_features=self.max_features,
            min_df=self.min_df,
            max_df=self.max_df,
            stop_words='english',
            ngram_range=self.ngram_range,
            norm='l2'
        )
        
        # Fit and transform job texts
        tfidf.fit(job_texts)
        job_vectors = tfidf.transform(job_texts)
        
        self.vectorizers['tfidf'] = tfidf
        
        return job_vectors
    
    def train_model(self):
        """Train the ML model for job recommendations."""
        print("Preprocessing jobs data...")
        job_features = self._preprocess_data()
        
        print("Creating features...")
        job_vectors = self._create_features(job_features)
        
        # Store model components
        self.model = {
            'job_vectors': job_vectors,
            'job_features': job_features
        }
        
        print("Model training completed.")
    
    def get_recommendations(self, user_profile: dict, top_k: int = 5) -> List[Dict]:
        """
        Get job recommendations based on user profile.
        
        Args:
            user_profile: Dictionary with user information
                Required keys: 'skills', 'preferred_location', 'experience_level'
                Optional keys: 'preferred_domain', 'salary_expectation'
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended jobs
        """
        if not self.model:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        # Create user text for vectorization
        user_text = (
            str(user_profile.get('skills', '')) + ' ' +
            str(user_profile.get('preferred_location', '')) + ' ' +
            str(user_profile.get('experience_level', ''))
        )
        
        # Transform user text using the existing vectorizer
        user_vector = self.vectorizers['tfidf'].transform([user_text])
        
        # Get all jobs for matching
        all_jobs = self.model['job_features'].copy()
        
        # Filter by location if specified
        preferred_location = user_profile.get('preferred_location', '').lower()
        if preferred_location and preferred_location != 'any':
            # Check if there are jobs in the preferred location
            location_filtered = all_jobs[
                (all_jobs['location'].str.lower() == preferred_location) |
                (all_jobs['location'].str.lower() == 'remote')
            ]
            
            # If jobs available in preferred location or remote, use them
            if len(location_filtered) > 0:
                all_jobs = location_filtered
        
        # Re-vectorize filtered jobs
        job_texts = (
            all_jobs['Type_of_job'].fillna('') + ' ' +
            all_jobs['company_name'].fillna('') + ' ' +
            all_jobs['location'].fillna('')
        )
        filtered_job_vectors = self.vectorizers['tfidf'].transform(job_texts)
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector, filtered_job_vectors).flatten()
        
        # Apply regularization
        similarities = similarities * (1 - self.regularization_strength)
        
        # Create a dataframe with similarities for sorting
        similarity_df = all_jobs.copy()
        similarity_df['similarity_score'] = similarities
        
        # Sort by similarity score (descending)
        similarity_df = similarity_df.sort_values('similarity_score', ascending=False)
        
        # Get top recommendations
        recommendations = []
        top_jobs = similarity_df.head(top_k)
        
        for _, job_row in top_jobs.iterrows():
            recommendation = {
                'job_id': job_row.name,  # Use row index as job ID
                'company_name': job_row['company_name'],
                'job_title': job_row['Type_of_job'],
                'location': job_row['location'],
                'salary': job_row['salary'],
                'experience_required': job_row['experience'],
                'actively_hiring': job_row['actively_hiring'],
                'similarity_score': float(job_row['similarity_score'])
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def save_model(self, filepath: str):
        """Save the trained model using joblib."""
        if not self.model:
            raise ValueError("No model to save. Train the model first.")
        
        model_data = {
            'model': self.model,
            'vectorizers': self.vectorizers,
            'config': {
                'max_features': self.max_features,
                'min_df': self.min_df,
                'max_df': self.max_df,
                'regularization_strength': self.regularization_strength,
                'ngram_range': self.ngram_range
            }
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model using joblib."""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.vectorizers = model_data['vectorizers']
        
        # Load configuration if available
        if 'config' in model_data:
            config = model_data['config']
            self.max_features = config.get('max_features', 100)
            self.min_df = config.get('min_df', 2)
            self.max_df = config.get('max_df', 0.8)
            self.regularization_strength = config.get('regularization_strength', 0.05)
            self.ngram_range = config.get('ngram_range', (1, 2))
        
        print(f"Model loaded from {filepath}")

def main():
    """Demo function to test the jobs matcher."""
    import os
    # Get the root directory (parent of ml_models directory)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Construct correct paths to dataset files
    jobs_dataset_path = os.path.join(root_dir, 'dataset', 'Jobs_cleaned.csv')
    
    # Initialize matcher
    matcher = JobsMatcher(
        jobs_dataset_path=jobs_dataset_path
    )
    
    # Train model
    matcher.train_model()
    
    # Save model
    model_path = os.path.join(root_dir, 'ml_models', 'jobs_matcher_model.joblib')
    matcher.save_model(model_path)
    
    # Example user profile
    user_profile = {
        'skills': 'Python, Data Analysis, Machine Learning',
        'preferred_location': 'bangalore',
        'experience_level': '0-2 years',
        'preferred_domain': 'Technology',
        'salary_expectation': '3-5 lpa'
    }
    
    # Get recommendations
    print("\n" + "="*80)
    print("JOB RECOMMENDATIONS")
    print("="*80)
    print(f"Skills: {user_profile['skills']}")
    print(f"Preferred Location: {user_profile['preferred_location']}")
    print(f"Experience Level: {user_profile['experience_level']}")
    print("="*80)
    
    recommendations = matcher.get_recommendations(user_profile, top_k=5)
    
    if not recommendations:
        print("No matching jobs found based on your criteria.")
        return
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n🏆 RECOMMENDATION #{i}")
        print(f"Company: {rec['company_name']}")
        print(f"Job Title: {rec['job_title']}")
        print(f"Location: {rec['location']}")
        print(f"Salary: {rec['salary']}")
        print(f"Experience Required: {rec['experience_required']}")
        print(f"Actively Hiring: {'Yes' if rec['actively_hiring'] == 1.0 else 'No'}")
        print(f"Similarity Score: {rec['similarity_score']:.2f}")
        print("-" * 60)

if __name__ == "__main__":
    main()