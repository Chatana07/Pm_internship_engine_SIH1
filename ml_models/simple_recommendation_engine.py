"""
Simple AI-based Recommendation Engine for PM Internship Scheme

This lightweight recommendation engine suggests relevant internships to candidates
based on their profile, skills, education, and location preferences.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class SimpleInternshipRecommendationEngine:
    def __init__(self, candidates_path, jobs_path):
        """
        Initialize the recommendation engine with candidate and job data.
        
        Args:
            candidates_path (str): Path to candidates CSV file
            jobs_path (str): Path to jobs CSV file
        """
        self.candidates_df = pd.read_csv(candidates_path)
        self.jobs_df = pd.read_csv(jobs_path)
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', lowercase=True)
        self._preprocess_data()
        self._create_skill_profiles()
    
    def _preprocess_data(self):
        """Preprocess and clean the data for recommendation."""
        # Clean skills data
        self.candidates_df['skills'] = self.candidates_df['skills'].fillna('').astype(str)
        self.jobs_df['Type_of_job'] = self.jobs_df['Type_of_job'].fillna('').astype(str)
        
        # Clean qualification data
        self.candidates_df['qualification'] = self.candidates_df['qualification'].fillna('')
        self.candidates_df['experience_level'] = self.candidates_df['experience_level'].fillna('')
        
        # Clean location data
        self.candidates_df['job_role'] = self.candidates_df['job_role'].fillna('')
        self.jobs_df['location'] = self.jobs_df['location'].fillna('')
        
        print(f"Loaded {len(self.candidates_df)} candidates and {len(self.jobs_df)} jobs")
    
    def _extract_skills_set(self, skills_text):
        """Extract unique skills from skills text."""
        if pd.isna(skills_text) or skills_text == '':
            return set()
        # Split by comma and clean
        skills = [skill.strip().lower() for skill in re.split('[,;]', skills_text)]
        # Remove empty strings
        skills = [skill for skill in skills if skill]
        return set(skills)
    
    def _create_skill_profiles(self):
        """Create skill profiles for candidates and jobs."""
        # Combine all text for TF-IDF
        all_texts = []
        
        # Add candidate skills
        candidate_texts = self.candidates_df['skills'].tolist()
        all_texts.extend(candidate_texts)
        
        # Add job titles
        job_texts = self.jobs_df['Type_of_job'].tolist()
        all_texts.extend(job_texts)
        
        # Fit TF-IDF vectorizer
        self.tfidf_vectorizer.fit(all_texts)
        
        # Transform candidate and job texts
        self.candidate_vectors = self.tfidf_vectorizer.transform(candidate_texts)
        self.job_vectors = self.tfidf_vectorizer.transform(job_texts)
    
    def _calculate_skill_overlap(self, candidate_skills, job_skills):
        """Calculate skill overlap score."""
        if not candidate_skills or not job_skills:
            return 0.0
        
        intersection = len(candidate_skills.intersection(job_skills))
        union = len(candidate_skills.union(job_skills))
        
        return intersection / union if union > 0 else 0.0
    
    def recommend(self, candidate_idx, top_k=5):
        """
        Recommend internships for a candidate using TF-IDF similarity.
        
        Args:
            candidate_idx (int): Index of the candidate
            top_k (int): Number of recommendations to return
            
        Returns:
            list: List of recommended job indices with scores
        """
        if candidate_idx >= len(self.candidates_df):
            raise ValueError(f"Candidate index {candidate_idx} out of range")
        
        # Get candidate vector
        candidate_vector = self.candidate_vectors[candidate_idx]
        
        # Calculate cosine similarity with all jobs
        similarities = cosine_similarity(candidate_vector, self.job_vectors).flatten()
        
        # Get top-k most similar jobs
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Create job-score pairs
        recommendations = [(int(idx), float(similarities[idx])) for idx in top_indices]
        
        # Apply fairness boost (simplified)
        boosted_recommendations = []
        fairness_boost = 1.05  # 5% boost
        
        for job_idx, score in recommendations:
            # Apply boost
            boosted_score = score * fairness_boost
            boosted_recommendations.append((job_idx, boosted_score))
        
        # Sort by boosted scores
        boosted_recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return boosted_recommendations
    
    def get_job_details(self, job_idx):
        """
        Get details of a job by index.
        
        Args:
            job_idx (int): Index of the job
            
        Returns:
            dict: Job details
        """
        if job_idx >= len(self.jobs_df):
            return {}
            
        job = self.jobs_df.iloc[job_idx]
        return {
            'job_title': job.get('Type_of_job', 'N/A'),
            'company': job.get('company_name', 'N/A'),
            'location': job.get('location', 'N/A'),
            'salary': job.get('salary', 'N/A'),
            'experience_required': job.get('experience', 'N/A')
        }
    
    def display_recommendations(self, candidate_idx, top_k=5):
        """
        Display recommendations for a candidate in a readable format.
        
        Args:
            candidate_idx (int): Index of the candidate
            top_k (int): Number of recommendations to display
        """
        if candidate_idx >= len(self.candidates_df):
            print(f"Invalid candidate index: {candidate_idx}")
            return
            
        candidate = self.candidates_df.iloc[candidate_idx]
        print(f"\nRecommendations for Candidate {candidate_idx+1}:")
        print(f"Skills: {candidate['skills']}")
        print(f"Qualification: {candidate['qualification']}")
        print(f"Experience Level: {candidate['experience_level']}")
        print("-" * 50)
        
        recommendations = self.recommend(candidate_idx, top_k)
        
        for i, (job_idx, score) in enumerate(recommendations):
            job_details = self.get_job_details(job_idx)
            print(f"{i+1}. {job_details['job_title']}")
            print(f"   Company: {job_details['company']}")
            print(f"   Location: {job_details['location']}")
            print(f"   Salary: {job_details['salary']}")
            print(f"   Experience Required: {job_details['experience_required']}")
            print(f"   Match Score: {score:.4f}")
            print()

def main():
    # Initialize the recommendation engine
    print("Initializing Simple Recommendation Engine...")
    engine = SimpleInternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    print("\n" + "="*60)
    print("PM Internship Recommendation System - Simple Version")
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
    
    # Get recommendations for first 3 candidates
    print("\n" + "="*60)
    print("Generating Recommendations...")
    print("="*60)
    
    for i in range(3):
        engine.display_recommendations(i, top_k=3)

if __name__ == "__main__":
    main()