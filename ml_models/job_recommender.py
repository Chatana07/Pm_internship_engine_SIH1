"""
Simple interface for job recommendations using the trained model
"""

import pandas as pd
import joblib
import os

class JobRecommender:
    """Simple interface for job recommendations."""
    
    def __init__(self, jobs_dataset_path: str, model_path: str):
        """
        Initialize the job recommender.
        
        Args:
            jobs_dataset_path: Path to your jobs dataset CSV file
            model_path: Path to pre-trained model joblib file
        """
        self.jobs_dataset_path = jobs_dataset_path
        self.model_path = model_path
        self.matcher = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model."""
        try:
            # Load the trained model
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.model_data = joblib.load(self.model_path)
            
            # Load jobs dataset
            if not os.path.exists(self.jobs_dataset_path):
                raise FileNotFoundError(f"Jobs dataset not found: {self.jobs_dataset_path}")
            
            self.jobs_df = pd.read_csv(self.jobs_dataset_path)
            
            # Extract necessary components from the loaded model
            self.model = self.model_data['model']
            self.vectorizers = self.model_data['vectorizers']
            
            # Load configuration if available
            self.max_features = 100
            self.min_df = 2
            self.max_df = 0.8
            self.regularization_strength = 0.05
            self.ngram_range = (1, 2)
            
            if 'config' in self.model_data:
                config = self.model_data['config']
                self.max_features = config.get('max_features', 100)
                self.min_df = config.get('min_df', 2)
                self.max_df = config.get('max_df', 0.8)
                self.regularization_strength = config.get('regularization_strength', 0.05)
                self.ngram_range = config.get('ngram_range', (1, 2))
            
            # Update the job features in the model with the current dataset
            self.model['job_features'] = self.jobs_df.copy()
            
            # Re-vectorize job texts
            job_texts = (
                self.jobs_df['Type_of_job'].fillna('') + ' ' +
                self.jobs_df['company_name'].fillna('') + ' ' +
                self.jobs_df['location'].fillna('')
            )
            self.model['job_vectors'] = self.vectorizers['tfidf'].transform(job_texts)
            
            print("Job recommender initialized successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Please train the model first using jobs_matcher.py")
            raise
    
    def get_recommendations(self, skills: str, location: str, experience: str, top_k: int = 5):
        """
        Get job recommendations.
        
        Args:
            skills: Comma-separated skills
            location: Preferred job location
            experience: Experience level (e.g., "0-2 years")
            top_k: Number of recommendations to return
        """
        if not hasattr(self, 'model') or not hasattr(self, 'vectorizers'):
            raise ValueError("Model not loaded. Please check the model file.")
        
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Create user text for vectorization
        user_text = (
            str(skills) + ' ' +
            str(location) + ' ' +
            str(experience)
        )
        
        # Transform user text using the existing vectorizer
        user_vector = self.vectorizers['tfidf'].transform([user_text])
        
        # Get all jobs for matching
        all_jobs = self.model['job_features'].copy()
        
        # Filter by location if specified
        preferred_location = location.lower()
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
        
        # Extract domain keywords from user skills to infer preferred domain
        preferred_domain = None
        skills_lower = skills.lower()
        
        # Try to infer domain from skills
        if 'python' in skills_lower or 'javascript' in skills_lower or 'html' in skills_lower or 'css' in skills_lower or 'angular' in skills_lower or 'react' in skills_lower:
            preferred_domain = 'web development'
        elif 'data' in skills_lower or 'machine learning' in skills_lower or 'analysis' in skills_lower:
            preferred_domain = 'data science'
        elif 'testing' in skills_lower or 'qa' in skills_lower:
            preferred_domain = 'quality assurance'
        elif 'sales' in skills_lower or 'business' in skills_lower:
            preferred_domain = 'business development'
        
        # Boost scores for jobs in the inferred preferred domain
        if preferred_domain:
            for idx, row in similarity_df.iterrows():
                job_domain = self._extract_domain_from_role(row['Type_of_job']).lower()
                # If job is in the preferred domain, strongly boost its score
                if preferred_domain == job_domain:
                    similarity_df.at[idx, 'similarity_score'] = similarity_df.at[idx, 'similarity_score'] * 2.0
                # Penalize jobs in completely different domains
                elif preferred_domain != 'general' and job_domain != 'general' and preferred_domain != job_domain:
                    similarity_df.at[idx, 'similarity_score'] = similarity_df.at[idx, 'similarity_score'] * 0.3
        
        # Sort by similarity score (descending)
        similarity_df = similarity_df.sort_values('similarity_score', ascending=False)
        
        # Get top recommendations
        recommendations = []
        top_jobs = similarity_df.head(top_k)
        
        for _, job_row in top_jobs.iterrows():
            # Extract domain from job title
            domain = self._extract_domain_from_role(job_row['Type_of_job'])
            
            recommendation = {
                'job_id': job_row.name,  # Use row index as job ID
                'company_name': job_row['company_name'],
                'job_title': job_row['Type_of_job'],
                'domain': domain,
                'location': job_row['location'],
                'salary': job_row['salary'],
                'experience_required': job_row['experience'],
                'actively_hiring': job_row['actively_hiring'],
                'similarity_score': float(job_row['similarity_score']),
                'reason': self._generate_recommendation_reason(job_row, skills, location, experience, domain)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
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
    
    def _generate_recommendation_reason(self, job_row, skills, location, experience, domain):
        """Generate explanation for why this job is recommended."""
        reasons = []
        
        # Skills match
        if skills:
            skills_lower = skills.lower()
            role = job_row['Type_of_job'].lower()
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
        
        # Domain match
        if domain and domain != 'General':
            reasons.append(f"matches your domain expertise ({domain})")
        
        # Location match
        job_location = job_row['location'].lower()
        user_location = location.lower()
        if user_location and (user_location == job_location or job_location == 'remote'):
            reasons.append(f"available in your preferred location ({user_location.title()})")
        
        # Experience match
        job_experience = job_row['experience'].lower()
        user_experience = experience.lower()
        if user_experience and user_experience in job_experience:
            reasons.append(f"matches your experience level ({user_experience})")
        
        # If no specific reasons, provide a general reason
        if not reasons:
            reasons.append("matches your profile based on our AI analysis")
        
        return f"This job {' and '.join(reasons)}."
    
    def print_recommendations(self, skills: str, location: str, experience: str, top_k: int = 5):
        """Print formatted job recommendations."""
        try:
            recommendations = self.get_recommendations(skills, location, experience, top_k)
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return
        
        print(f"\n{'='*80}")
        print("JOB RECOMMENDATIONS")
        print(f"{'='*80}")
        print(f"Skills: {skills}")
        print(f"Preferred Location: {location}")
        print(f"Experience Level: {experience}")
        print(f"{'='*80}")
        
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

def main():
    """Demo function to test the job recommender."""
    # Initialize recommender
    recommender = JobRecommender(
        jobs_dataset_path='dataset/Jobs_cleaned.csv',
        model_path='ml_models/jobs_matcher_model.joblib'
    )
    
    # Example recommendations
    recommender.print_recommendations(
        skills="Python, Machine Learning, Data Analysis",
        location="bangalore",
        experience="0-2 years",
        top_k=3
    )

if __name__ == "__main__":
    main()