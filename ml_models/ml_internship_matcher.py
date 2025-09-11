"""
ML-based internship matching system that integrates with the existing system
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import re
import os
from typing import List, Dict

class MLInternshipMatcher:
    """ML-based internship matching engine that works with the existing system."""
    
    def __init__(self, user_dataset_path: str, internship_dataset_path: str, model_path: str = None):
        """
        Initialize the ML internship matcher.
        
        Args:
            user_dataset_path: Path to user dataset CSV file
            internship_dataset_path: Path to internship dataset CSV file
            model_path: Path to pre-trained model joblib file (optional)
        """
        self.user_dataset_path = os.path.abspath(user_dataset_path)
        self.internship_dataset_path = os.path.abspath(internship_dataset_path)
        self.users_df = None
        self.internships_df = None
        self.model = None
        self.vectorizers = {}
        
        # Regularization parameters
        self.max_features = 100
        self.min_df = 2
        self.max_df = 0.8
        self.regularization_strength = 0.05
        self.ngram_range = (1, 2)
        
        # Load datasets
        self.load_datasets()
        
        # Load model if provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_datasets(self):
        """Load both user and internship datasets from CSV files."""
        try:
            print(f"Loading user dataset from: {self.user_dataset_path}")
            self.users_df = pd.read_csv(self.user_dataset_path)
            print(f"Loaded {len(self.users_df)} users")
            
            print(f"Loading internship dataset from: {self.internship_dataset_path}")
            self.internships_df = pd.read_csv(self.internship_dataset_path)
            print(f"Loaded {len(self.internships_df)} internships")
            
            # Handle NaN values
            self.users_df = self.users_df.fillna('')
            self.internships_df = self.internships_df.fillna('')
            
        except Exception as e:
            print(f"Error loading datasets: {e}")
            raise
    
    def _preprocess_data(self):
        """Preprocess data for ML training."""
        # Create features for users and internships
        user_features = self.users_df.copy()
        internship_features = self.internships_df.copy()
        
        # Handle different column naming conventions for stipend/salary
        salary_col = 'salary' if 'salary' in internship_features.columns else 'stipend'
        internship_features['stipend_value'] = internship_features[salary_col].apply(self._parse_salary)
        
        return user_features, internship_features
    
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
    
    def _create_features(self, user_features, internship_features):
        """Create feature vectors for users and internships."""
        # Combine text features for vectorization
        # Handle different column naming conventions
        user_skills_col = 'Skills' if 'Skills' in user_features.columns else 'skills'
        user_domain_col = 'PreferredDomain' if 'PreferredDomain' in user_features.columns else 'job_role'
        user_location_col = 'PreferredLocation' if 'PreferredLocation' in user_features.columns else 'location'
        user_education_col = 'Education' if 'Education' in user_features.columns else 'qualification'
        
        internship_role_col = 'Type_of_job' if 'Type_of_job' in internship_features.columns else 'role'
        internship_company_col = 'company_name' if 'company_name' in internship_features.columns else 'company'
        internship_location_col = 'location'
        
        user_texts = (
            user_features[user_skills_col].fillna('') + ' ' +
            user_features[user_domain_col].fillna('') + ' ' +
            user_features[user_location_col].fillna('') + ' ' +
            user_features[user_education_col].fillna('')
        )
        
        internship_texts = (
            internship_features[internship_role_col].fillna('') + ' ' +
            internship_features[internship_company_col].fillna('') + ' ' +
            internship_features[internship_location_col].fillna('')
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
        
        # Fit and transform all texts
        all_texts = list(user_texts) + list(internship_texts)
        tfidf.fit(all_texts)
        
        # Transform user and internship texts separately
        user_vectors = tfidf.transform(user_texts)
        internship_vectors = tfidf.transform(internship_texts)
        
        self.vectorizers['tfidf'] = tfidf
        
        return user_vectors, internship_vectors
    
    def train_model(self):
        """Train the ML model for internship recommendations."""
        print("Preprocessing data...")
        user_features, internship_features = self._preprocess_data()
        
        print("Creating features...")
        user_vectors, internship_vectors = self._create_features(user_features, internship_features)
        
        # Store model components
        self.model = {
            'user_vectors': user_vectors,
            'internship_vectors': internship_vectors,
            'user_features': user_features,
            'internship_features': internship_features
        }
        
        print("Model training completed.")
    
    def get_recommendations(self, user_id: int, top_k: int = 5) -> List[Dict]:
        """
        Get internship recommendations for a specific user ID.
        
        Args:
            user_id: User ID to get recommendations for
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended internships
        """
        if not self.model:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        # Find user index
        user_indices = self.users_df[self.users_df['UserID'] == user_id].index
        if len(user_indices) == 0:
            raise ValueError(f"User with ID {user_id} not found")
        
        user_index = user_indices[0]
        
        # Get user vector
        user_vector = self.model['user_vectors'][user_index]
        
        # Get all internships for matching
        all_internships = self.model['internship_features'].copy()
        internship_vectors = self.model['internship_vectors']
        
        # Filter by location if user has a preferred location
        user_location = self.users_df.iloc[user_index]['PreferredLocation'].lower()
        if user_location and user_location != 'any':
            # Check if there are internships in the preferred location
            location_filtered = all_internships[
                (all_internships['location'].str.lower() == user_location) |
                (all_internships['location'].str.lower() == 'remote')
            ]
            
            # If internships available in preferred location or remote, use them
            if len(location_filtered) > 0:
                # Get indices of filtered internships
                filtered_indices = location_filtered.index
                all_internships = location_filtered
                internship_vectors = self.model['internship_vectors'][filtered_indices]
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector, internship_vectors).flatten()
        
        # Apply regularization
        similarities = similarities * (1 - self.regularization_strength)
        
        # Create a dataframe with similarities for sorting
        similarity_df = all_internships.copy()
        similarity_df['similarity_score'] = similarities
        
        # Sort by similarity score (descending)
        similarity_df = similarity_df.sort_values('similarity_score', ascending=False)
        
        # Get top recommendations
        recommendations = []
        top_internships = similarity_df.head(top_k)
        
        # Get user profile for reason generation
        user_row = self.users_df.iloc[user_index]
        user_profile = {
            'skills': user_row['Skills'],
            'preferred_domain': user_row['PreferredDomain'],
            'preferred_location': user_row['PreferredLocation'],
            'education': user_row['Education']
        }
        
        for _, internship_row in top_internships.iterrows():
            # Extract domain properly from the job role
            job_role = internship_row['Type_of_job']
            domain = self._extract_domain_from_role(job_role)
            
            recommendation = {
                'internship_id': internship_row.name,  # Use row index as internship ID
                'company': internship_row['company_name'],
                'role': job_role,
                'domain': domain,
                'location': internship_row['location'],
                'type': 'Full-time',  # Default value
                'duration': internship_row.get('experience', 'Not specified'),
                'stipend': internship_row['salary'],
                'similarity_score': float(internship_row['similarity_score']),
                'reason': self._generate_recommendation_reason(internship_row, user_profile)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_recommendations_for_profile(self, user_profile: dict, top_k: int = 5) -> List[Dict]:
        """
        Get internship recommendations for a user profile (used for frontend form data).
        
        Args:
            user_profile: Dictionary with user information
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended internships
        """
        if not self.model or not self.vectorizers:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        # Get user's preferred domain
        preferred_domain = str(user_profile.get('preferred_domain', '')).lower()
        
        # Create user text for vectorization with stronger domain preference
        # Repeat the domain preference to give it more weight
        domain_preference = str(user_profile.get('preferred_domain', ''))
        user_text = (
            str(user_profile.get('skills', '')) + ' ' +
            domain_preference + ' ' + domain_preference + ' ' + domain_preference + ' ' +  # Weight domain preference more heavily
            str(user_profile.get('preferred_location', '')) + ' ' +
            str(user_profile.get('education', ''))
        )
        
        # Transform user text using the existing vectorizer
        user_vector = self.vectorizers['tfidf'].transform([user_text])
        
        # Get all internships for matching
        all_internships = self.model['internship_features'].copy()
        internship_vectors = self.model['internship_vectors']
        
        # Filter by location if specified
        preferred_location = user_profile.get('preferred_location', '').lower()
        if preferred_location and preferred_location != 'any':
            # Check if there are internships in the preferred location
            location_filtered = all_internships[
                (all_internships['location'].str.lower() == preferred_location) |
                (all_internships['location'].str.lower() == 'remote')
            ]
            
            # If internships available in preferred location or remote, use them
            if len(location_filtered) > 0:
                # Get indices of filtered internships
                filtered_indices = location_filtered.index
                all_internships = location_filtered
                internship_vectors = self.model['internship_vectors'][filtered_indices]
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector, internship_vectors).flatten()
        
        # Apply regularization
        similarities = similarities * (1 - self.regularization_strength)
        
        # Create a dataframe with similarities for sorting
        similarity_df = all_internships.copy()
        similarity_df['similarity_score'] = similarities
        
        # Strongly boost scores for jobs in the preferred domain
        if preferred_domain:
            for idx, row in similarity_df.iterrows():
                job_domain = self._extract_domain_from_role(row['Type_of_job']).lower()
                # If job is in the preferred domain, strongly boost its score
                if preferred_domain == job_domain:
                    similarity_df.at[idx, 'similarity_score'] = similarity_df.at[idx, 'similarity_score'] * 2.0
                # For Web Development specifically, also boost related tech roles
                elif preferred_domain == 'web development' and job_domain == 'web development':
                    similarity_df.at[idx, 'similarity_score'] = similarity_df.at[idx, 'similarity_score'] * 2.0
                # Penalize jobs in completely different domains
                elif preferred_domain != 'general' and job_domain != 'general' and preferred_domain != job_domain:
                    similarity_df.at[idx, 'similarity_score'] = similarity_df.at[idx, 'similarity_score'] * 0.3
        
        # Sort by similarity score (descending)
        similarity_df = similarity_df.sort_values('similarity_score', ascending=False)
        
        # Get top recommendations
        recommendations = []
        top_internships = similarity_df.head(top_k)
        
        for _, internship_row in top_internships.iterrows():
            # Extract domain properly from the job role
            job_role = internship_row['Type_of_job']
            domain = self._extract_domain_from_role(job_role)
            
            recommendation = {
                'internship_id': internship_row.name,  # Use row index as internship ID
                'company': internship_row['company_name'],
                'role': job_role,
                'domain': domain,
                'location': internship_row['location'],
                'type': 'Full-time',  # Default value
                'duration': internship_row.get('experience', 'Not specified'),
                'stipend': internship_row['salary'],
                'similarity_score': float(internship_row['similarity_score']),
                'reason': self._generate_recommendation_reason(internship_row, user_profile)
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
    
    def _extract_domain_from_role(self, role):
        """Extract domain from job role."""
        role_lower = str(role).lower()
        # Check for Data Science first (more specific terms)
        if 'data scientist' in role_lower or 'data analyst' in role_lower or 'data engineer' in role_lower or 'data science' in role_lower:
            return 'Data Science'
        # Check for Quality Assurance (before Web Development to avoid conflicts)
        elif 'testing' in role_lower or 'qa' in role_lower or 'quality' in role_lower or 'tester' in role_lower or 'assurance' in role_lower:
            return 'Quality Assurance'
        # Check for Business Development
        elif 'business development' in role_lower or 'sales' in role_lower or 'business' in role_lower or 'corporate sales' in role_lower:
            return 'Business Development'
        # Check for Finance
        elif 'finance' in role_lower or 'financial' in role_lower or 'account' in role_lower or 'accounts' in role_lower:
            return 'Finance'
        # Check for Web Development
        elif 'web' in role_lower or 'developer' in role_lower or 'engineer' in role_lower or 'frontend' in role_lower or 'backend' in role_lower or 'full stack' in role_lower or 'react' in role_lower or 'angular' in role_lower or 'javascript' in role_lower or 'python' in role_lower:
            return 'Web Development'
        # Check for Design
        elif 'design' in role_lower or 'ui' in role_lower or 'ux' in role_lower or 'graphic' in role_lower or 'visual' in role_lower:
            return 'Design'
        # Check for Marketing
        elif 'marketing' in role_lower or 'digital marketing' in role_lower or 'seo' in role_lower or 'social media' in role_lower:
            return 'Marketing'
        # Check for Human Resources
        elif 'hr' in role_lower or 'human' in role_lower or 'recruitment' in role_lower:
            return 'Human Resources'
        # Check for Content Writing
        elif 'content' in role_lower or 'writer' in role_lower or 'editor' in role_lower:
            return 'Content Writing'
        # Check for Growth roles
        elif 'growth' in role_lower or 'growth catalyst' in role_lower:
            return 'Business Development'
        # Check for Insurance roles
        elif 'insurance' in role_lower or 'consultant' in role_lower:
            return 'Finance'
        else:
            return 'General'
    
    def _generate_recommendation_reason(self, internship_row, user_profile):
        """Generate explanation for why this internship is recommended."""
        reasons = []
        
        # Skills match
        if user_profile.get('skills'):
            skills = user_profile['skills'].lower()
            role = internship_row['Type_of_job'].lower()
            # Check for skill matches
            skill_list = [skill.strip().lower() for skill in skills.split(',')]
            matched_skills = []
            for skill in skill_list:
                # Check if skill is in role description
                if skill in role or role in skill:
                    matched_skills.append(skill)
            
            # Also check for partial matches
            if not matched_skills:
                for skill in skill_list:
                    # Split skill into words and check each word
                    skill_words = skill.split()
                    for word in skill_words:
                        if len(word) > 2 and word in role:  # Only check words longer than 2 characters
                            matched_skills.append(skill)
                            break
            
            if matched_skills:
                # Remove duplicates and format
                unique_skills = list(set(matched_skills))
                reasons.append(f"matches your skills ({', '.join(unique_skills)})")
        
        # Domain match - more explicit checking
        user_domain = user_profile.get('preferred_domain', '').lower()
        internship_domain = self._extract_domain_from_role(internship_row['Type_of_job']).lower()
        
        # If user specified a domain preference, check for match
        if user_domain and user_domain != 'general':
            if user_domain == internship_domain:
                reasons.append(f"matches your preferred domain ({user_domain.title()})")
            elif user_domain in internship_domain or internship_domain in user_domain:
                reasons.append(f"related to your preferred domain ({user_domain.title()})")
            # Additional check for Web Development
            elif user_domain == 'web development' and internship_domain == 'web development':
                reasons.append(f"matches your preferred domain ({user_domain.title()})")
        
        # Location match
        user_location = user_profile.get('preferred_location', '').lower()
        internship_location = internship_row['location'].lower()
        if user_location and (user_location == internship_location or internship_location == 'remote'):
            reasons.append(f"available in your preferred location ({user_location.title()})")
        
        # If no specific reasons, provide a general reason
        if not reasons:
            reasons.append("matches your profile based on our AI analysis")
        
        return f"This internship {' and '.join(reasons)}."
