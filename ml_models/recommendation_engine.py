"""
AI-based Recommendation Engine for PM Internship Scheme

This lightweight recommendation engine suggests relevant internships to candidates
based on their profile, skills, education, and location preferences.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import re
import warnings
warnings.filterwarnings('ignore')

class InternshipRecommendationEngine:
    def __init__(self, candidates_path, jobs_path):
        """
        Initialize the recommendation engine with candidate and job data.
        
        Args:
            candidates_path (str): Path to candidates CSV file
            jobs_path (str): Path to jobs CSV file
        """
        self.candidates_df = pd.read_csv(candidates_path)
        self.jobs_df = pd.read_csv(jobs_path)
        self.tfidf_vectorizer = None
        self.model = None
        self.scaler = StandardScaler()
        self._preprocess_data()
    
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
        skills = [skill.strip().lower() for skill in skills_text.split(',')]
        return set(skills)
    
    def _calculate_skill_jaccard(self, candidate_skills, job_text):
        """Calculate Jaccard similarity between candidate skills and job text."""
        if not candidate_skills:
            return 0.0
            
        # Extract skills from job text
        job_skills = self._extract_skills_set(job_text)
        
        if not job_skills:
            return 0.0
            
        # Calculate Jaccard similarity
        intersection = len(candidate_skills.intersection(job_skills))
        union = len(candidate_skills.union(job_skills))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_skill_overlap(self, candidate_skills, job_text):
        """Calculate number of overlapping skills."""
        if not candidate_skills:
            return 0
            
        job_skills = self._extract_skills_set(job_text)
        return len(candidate_skills.intersection(job_skills))
    
    def _create_tfidf_features(self):
        """Create TF-IDF features for candidates and jobs."""
        # Combine candidate skills for TF-IDF
        candidate_skills_text = self.candidates_df['skills'].tolist()
        
        # Combine job titles/descriptions for TF-IDF
        job_text = self.jobs_df['Type_of_job'].tolist()
        
        # Fit TF-IDF vectorizer
        all_text = candidate_skills_text + job_text
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        self.tfidf_vectorizer.fit(all_text)
        
        # Transform candidate and job text
        candidate_tfidf = self.tfidf_vectorizer.transform(candidate_skills_text)
        job_tfidf = self.tfidf_vectorizer.transform(job_text)
        
        return candidate_tfidf, job_tfidf
    
    def _compute_interaction_features(self, candidate_idx, job_indices):
        """
        Compute interaction features between a candidate and multiple jobs.
        
        Args:
            candidate_idx (int): Index of the candidate
            job_indices (list): List of job indices to compute features for
            
        Returns:
            pd.DataFrame: DataFrame with interaction features
        """
        candidate = self.candidates_df.iloc[candidate_idx]
        candidate_skills = self._extract_skills_set(candidate['skills'])
        
        features_list = []
        
        for job_idx in job_indices:
            job = self.jobs_df.iloc[job_idx]
            
            # Skill-based features
            skill_jaccard = self._calculate_skill_jaccard(candidate_skills, job['Type_of_job'])
            skill_overlap_count = self._calculate_skill_overlap(candidate_skills, job['Type_of_job'])
            
            # Location match
            location_match_flag = 1 if candidate['job_role'].lower() == job['location'].lower() else 0
            
            # Experience difference
            experience_diff = candidate['experience_enc'] - job['experience_enc']
            
            # Same sector flag (simplified)
            same_sector_flag = 1 if candidate['job_role'].lower() in job['Type_of_job'].lower() else 0
            
            features = {
                'skill_jaccard': skill_jaccard,
                'skill_overlap_count': skill_overlap_count,
                'location_match_flag': location_match_flag,
                'experience_diff': experience_diff,
                'same_sector_flag': same_sector_flag
            }
            
            features_list.append(features)
        
        return pd.DataFrame(features_list)
    
    def _shortlist_jobs(self, candidate_idx, top_n=100):
        """
        Shortlist jobs using filters and TF-IDF similarity.
        
        Args:
            candidate_idx (int): Index of the candidate
            top_n (int): Number of jobs to shortlist
            
        Returns:
            list: Indices of shortlisted jobs
        """
        # Create TF-IDF features if not already done
        if self.tfidf_vectorizer is None:
            candidate_tfidf, job_tfidf = self._create_tfidf_features()
        else:
            candidate_skills_text = [self.candidates_df.iloc[candidate_idx]['skills']]
            candidate_tfidf = self.tfidf_vectorizer.transform(candidate_skills_text)
            job_tfidf = self.tfidf_vectorizer.transform(self.jobs_df['Type_of_job'])
        
        # Calculate cosine similarity
        similarity_scores = cosine_similarity(
            candidate_tfidf, 
            job_tfidf
        ).flatten()
        
        # Get top N most similar jobs
        top_indices = similarity_scores.argsort()[-top_n:][::-1]
        
        return top_indices.tolist()
    
    def train_model(self, sample_size=1000):
        """
        Train a logistic regression model on engineered features.
        
        Args:
            sample_size (int): Number of candidate-job pairs to sample for training
        """
        print("Training recommendation model...")
        
        # Create TF-IDF features
        candidate_tfidf, job_tfidf = self._create_tfidf_features()
        
        # Sample candidate-job pairs for training
        pairs = []
        labels = []
        
        # Positive examples (using heuristic for now)
        for i in range(min(sample_size // 2, len(self.candidates_df))):
            candidate_idx = i
            shortlisted_jobs = self._shortlist_jobs(candidate_idx, top_n=10)
            
            # Create positive examples (high similarity jobs)
            candidate_similarities = cosine_similarity(
                candidate_tfidf[candidate_idx], 
                job_tfidf[shortlisted_jobs]
            ).flatten()
            
            for j, job_idx in enumerate(shortlisted_jobs):
                # Positive label if similarity is high
                label = 1 if candidate_similarities[j] > 0.1 else 0
                pairs.append((candidate_idx, job_idx, candidate_similarities[j]))
                labels.append(label)
        
        if len(pairs) == 0:
            print("No training pairs generated")
            return
        
        # Extract features for training pairs
        features_list = []
        valid_labels = []
        
        for i, (candidate_idx, job_idx, similarity) in enumerate(pairs):
            if i >= len(labels):
                break
                
            # Compute interaction features
            features_df = self._compute_interaction_features(candidate_idx, [job_idx])
            if len(features_df) > 0:
                features_list.append(features_df.iloc[0].to_dict())
                valid_labels.append(labels[i])
        
        if len(features_list) == 0:
            print("No valid features extracted")
            return
        
        # Train logistic regression model
        X = pd.DataFrame(features_list)
        y = np.array(valid_labels)
        
        # Handle missing values
        X = X.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = LogisticRegression(
            C=1.0,
            max_iter=500,
            class_weight='balanced',
            solver='saga'
        )
        self.model.fit(X_scaled, y)
        
        print(f"Model trained on {len(X)} samples")
        return self.model
    
    def recommend(self, candidate_idx, top_k=5, use_model=True):
        """
        Recommend internships for a candidate.
        
        Args:
            candidate_idx (int): Index of the candidate
            top_k (int): Number of recommendations to return
            use_model (bool): Whether to use trained model or TF-IDF similarity
            
        Returns:
            list: List of recommended job indices with scores
        """
        # Shortlist jobs
        shortlisted_jobs = self._shortlist_jobs(candidate_idx, top_n=100)
        
        if use_model and self.model is not None:
            # Use trained model for scoring
            features_df = self._compute_interaction_features(candidate_idx, shortlisted_jobs)
            features_df = features_df.fillna(0)
            
            # Scale features
            X_scaled = self.scaler.transform(features_df)
            
            # Get predictions
            scores = self.model.predict_proba(X_scaled)[:, 1]  # Probability of positive class
        else:
            # Use TF-IDF similarity as fallback
            candidate_tfidf, job_tfidf = self._create_tfidf_features()
            candidate_skills_text = [self.candidates_df.iloc[candidate_idx]['skills']]
            candidate_tfidf = self.tfidf_vectorizer.transform(candidate_skills_text)
            similarity_scores = cosine_similarity(
                candidate_tfidf, 
                job_tfidf[shortlisted_jobs]
            ).flatten()
            scores = similarity_scores
        
        # Create job-score pairs
        job_scores = list(zip(shortlisted_jobs, scores))
        
        # Sort by score (descending)
        job_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Apply fairness boost for rural candidates (simplified)
        # In a real implementation, you would check candidate's rural/urban status
        fairness_boost = 1.05  # 5% boost
        boosted_scores = []
        for job_idx, score in job_scores[:top_k*2]:  # Boost top candidates
            boosted_score = score * fairness_boost
            boosted_scores.append((job_idx, boosted_score))
        
        # Sort by boosted scores
        boosted_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k recommendations
        return boosted_scores[:top_k]
    
    def get_job_details(self, job_idx):
        """
        Get details of a job by index.
        
        Args:
            job_idx (int): Index of the job
            
        Returns:
            dict: Job details
        """
        job = self.jobs_df.iloc[job_idx]
        return {
            'job_title': job['Type_of_job'],
            'company': job['company_name'],
            'location': job['location'],
            'salary': job['salary'],
            'experience_required': job['experience']
        }
    
    def display_recommendations(self, candidate_idx, top_k=5):
        """
        Display recommendations for a candidate in a readable format.
        
        Args:
            candidate_idx (int): Index of the candidate
            top_k (int): Number of recommendations to display
        """
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

# Example usage
if __name__ == "__main__":
    # Initialize the recommendation engine
    engine = InternshipRecommendationEngine(
        'dataset/Candidates_cleaned.csv',
        'dataset/Jobs_cleaned.csv'
    )
    
    # Train the model (optional, for better recommendations)
    # engine.train_model()
    
    # Get recommendations for the first candidate
    engine.display_recommendations(0, top_k=5)