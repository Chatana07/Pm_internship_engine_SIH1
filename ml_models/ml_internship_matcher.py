import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import re
import warnings
import joblib
import os
warnings.filterwarnings('ignore')

class MLInternshipMatcher:
    def __init__(self, user_dataset_path, internship_dataset_path):
        """
        Initialize the ML-based internship matcher.
        
        Args:
            user_dataset_path (str): Path to user profile CSV file
            internship_dataset_path (str): Path to internship CSV file
        """
        self.user_dataset_path = user_dataset_path
        self.internship_dataset_path = internship_dataset_path
        self.users_df = None
        self.internships_df = None
        self.tfidf_vectorizer = None
        self.model = None
        self.scaler = StandardScaler()
        self.load_datasets()
    
    def load_datasets(self):
        """Load user and internship datasets."""
        try:
            # Load datasets with correct paths
            print(f"Loading user dataset from: {self.user_dataset_path}")
            print(f"Loading internship dataset from: {self.internship_dataset_path}")
            
            self.users_df = pd.read_csv(self.user_dataset_path)
            self.internships_df = pd.read_csv(self.internship_dataset_path)
            
            # Map new dataset columns to expected column names
            self._map_columns()
            
            print(f"Loaded {len(self.users_df)} user profiles and {len(self.internships_df)} internships")
        except Exception as e:
            print(f"Error loading datasets: {e}")
            raise
    
    def _map_columns(self):
        """Map new dataset columns to expected column names."""
        # Map user dataset columns (Candidates_cleaned.csv)
        if 'candidate_id' in self.users_df.columns:
            self.users_df.rename(columns={
                'candidate_id': 'UserID',
                'skills': 'Skills',
                'qualification': 'Education',
                'job_role': 'PreferredDomain',
                'experience_level': 'EnrollmentStatus'
            }, inplace=True)
            # Add missing columns with default values
            self.users_df['PreferredLocation'] = 'Remote'  # Default value
            self.users_df['InternshipDuration'] = '3 months'  # Default value
            # Handle NaN values
            self.users_df['Skills'] = self.users_df['Skills'].fillna('').astype(str)
            self.users_df['Education'] = self.users_df['Education'].fillna('').astype(str)
            self.users_df['PreferredDomain'] = self.users_df['PreferredDomain'].fillna('').astype(str)
            self.users_df['EnrollmentStatus'] = self.users_df['EnrollmentStatus'].fillna('').astype(str)
        
        # Map internship dataset columns (Jobs_cleaned.csv)
        if 'Type_of_job' in self.internships_df.columns:
            self.internships_df.rename(columns={
                'Type_of_job': 'Role',
                'company_name': 'Company',
                'location': 'Location',
                'experience': 'Duration',
                'salary': 'Stipend'
            }, inplace=True)
            # Add missing columns with default values
            self.internships_df['InternshipID'] = self.internships_df.index + 1
            self.internships_df['Domain'] = self.internships_df['Role'].apply(lambda x: self._extract_domain(x))
            self.internships_df['Type'] = 'Full-time'  # Default value
            # Handle NaN values
            self.internships_df['Role'] = self.internships_df['Role'].fillna('').astype(str)
            self.internships_df['Company'] = self.internships_df['Company'].fillna('').astype(str)
            self.internships_df['Location'] = self.internships_df['Location'].fillna('').astype(str)
            self.internships_df['Duration'] = self.internships_df['Duration'].fillna('').astype(str)
            self.internships_df['Stipend'] = self.internships_df['Stipend'].fillna('').astype(str)
        
        print("Dataset columns mapped successfully")
    
    def _extract_domain(self, role):
        """Extract domain from job role."""
        role_lower = str(role).lower()
        if 'data' in role_lower or 'analyst' in role_lower:
            return 'Data Science'
        elif 'developer' in role_lower or 'engineer' in role_lower:
            return 'Web Development'
        elif 'design' in role_lower:
            return 'Design'
        elif 'sales' in role_lower or 'business' in role_lower:
            return 'Business Development'
        else:
            return 'General'
    
    def _extract_skills_set(self, skills_text):
        """Extract unique skills from skills text."""
        if pd.isna(skills_text) or skills_text == '':
            return set()
        # Split by comma and clean
        skills = [skill.strip().lower() for skill in re.split('[,;]', str(skills_text))]
        # Remove empty strings
        skills = [skill for skill in skills if skill]
        return set(skills)
    
    def _calculate_skill_jaccard(self, candidate_skills, job_text):
        """Calculate Jaccard similarity between candidate skills and job text."""
        if not candidate_skills:
            return 0.0
            
        # Extract skills from job text (simple approach)
        job_skills = set(str(job_text).lower().split())
        
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
            
        job_skills = set(str(job_text).lower().split())
        return len(candidate_skills.intersection(job_skills))
    
    def _create_tfidf_features(self):
        """Create TF-IDF features for users and internships."""
        # Combine user skills for TF-IDF
        user_skills_text = self.users_df['Skills'].fillna('').astype(str).tolist()
        
        # Combine internship descriptions for TF-IDF
        internship_text = self.internships_df['Role'].fillna('').astype(str).tolist()
        
        # Fit TF-IDF vectorizer
        all_text = user_skills_text + internship_text
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        self.tfidf_vectorizer.fit(all_text)
        
        # Transform user and internship text
        user_tfidf = self.tfidf_vectorizer.transform(user_skills_text)
        internship_tfidf = self.tfidf_vectorizer.transform(internship_text)
        
        return user_tfidf, internship_tfidf
    
    def _compute_interaction_features(self, user_idx, internship_indices):
        """
        Compute interaction features between a user and multiple internships.
        
        Args:
            user_idx (int): Index of the user
            internship_indices (list): List of internship indices to compute features for
            
        Returns:
            pd.DataFrame: DataFrame with interaction features
        """
        user = self.users_df.iloc[user_idx]
        user_skills = self._extract_skills_set(user['Skills'])
        
        features_list = []
        
        for internship_idx in internship_indices:
            # Make sure internship_idx is within bounds
            if internship_idx >= len(self.internships_df):
                continue
                
            internship = self.internships_df.iloc[internship_idx]
            
            # Skill-based features
            skill_jaccard = self._calculate_skill_jaccard(user_skills, str(internship['Role']))
            skill_overlap_count = self._calculate_skill_overlap(user_skills, str(internship['Role']))
            
            # Domain match (more important)
            user_domain = str(user['PreferredDomain']).lower()
            internship_domain = str(internship['Domain']).lower()
            domain_match_flag = 1 if (user_domain == internship_domain or 
                                    user_domain in internship_domain or 
                                    internship_domain in user_domain) else 0
            
            # Location match (simplified but more accurate)
            user_location = str(user['PreferredLocation']).lower()
            internship_location = str(internship['Location']).lower()
            location_match_flag = 1 if (user_location == internship_location or 
                                      internship_location == 'remote' or 
                                      user_location == 'remote') else 0
            
            # Duration match - improved logic
            user_duration = str(user['InternshipDuration']).lower()
            internship_duration = str(internship['Duration']).lower()
            
            # Exact match
            if user_duration == internship_duration:
                duration_match_flag = 1
            # Partial match (e.g., user wants "12 Months" and job offers "3-5 years")
            elif ('12' in user_duration and ('year' in internship_duration or 'month' in internship_duration)) or \
                 ('6' in user_duration and 'month' in internship_duration):
                duration_match_flag = 0.5  # Partial match
            else:
                duration_match_flag = 0  # No match
            
            # Create a more nuanced score based on priorities
            # Domain match is most important (weight 0.4), then skills (0.3), location (0.2), duration (0.1)
            priority_score = (domain_match_flag * 0.4 + 
                            skill_jaccard * 0.3 + 
                            location_match_flag * 0.2 + 
                            duration_match_flag * 0.1)
            
            features = {
                'skill_jaccard': skill_jaccard,
                'skill_overlap_count': skill_overlap_count,
                'domain_match_flag': domain_match_flag,
                'location_match_flag': location_match_flag,
                'duration_match_flag': duration_match_flag,
                'priority_score': priority_score  # New feature for better scoring
            }
            
            features_list.append(features)
        
        return pd.DataFrame(features_list)
    
    def _shortlist_internships(self, user_idx, top_n=100):
        """
        Shortlist internships using filters and TF-IDF similarity.
        Prioritizes domain match, then location, then duration.
        
        Args:
            user_idx (int): Index of the user
            top_n (int): Number of internships to shortlist
            
        Returns:
            list: Indices of shortlisted internships
        """
        user = self.users_df.iloc[user_idx]
        user_domain = str(user['PreferredDomain']).lower()
        user_location = str(user['PreferredLocation']).lower()
        user_duration = str(user['InternshipDuration']).lower()
        
        # Filter by domain first - this is the most important
        domain_filtered = []
        for idx, internship in self.internships_df.iterrows():
            internship_domain = str(internship['Domain']).lower()
            # More strict domain matching to prevent overfitting
            if user_domain == internship_domain:
                domain_filtered.append(idx)
        
        # If no exact domain matches, try partial matches but with a limit
        if not domain_filtered:
            for idx, internship in self.internships_df.iterrows():
                internship_domain = str(internship['Domain']).lower()
                if user_domain in internship_domain or internship_domain in user_domain:
                    domain_filtered.append(idx)
                    # Limit to prevent too many irrelevant matches
                    if len(domain_filtered) >= 100:
                        break
        
        # If still no domain matches, return empty list to prevent overfitting
        # This is the key fix - don't fallback to all internships
        if not domain_filtered:
            return []
        
        # Filter by location - prefer exact match or remote
        location_filtered = []
        for idx in domain_filtered:
            internship = self.internships_df.iloc[idx]
            internship_location = str(internship['Location']).lower()
            
            # Exact location match or remote work
            if user_location == internship_location or internship_location == 'remote' or user_location == 'remote':
                location_filtered.append(idx)
        
        # If no location matches, use domain filtered results (but still better than all internships)
        if not location_filtered:
            location_filtered = domain_filtered
        
        # Filter by duration - prefer exact match or compatible duration
        duration_filtered = []
        for idx in location_filtered:
            internship = self.internships_df.iloc[idx]
            internship_duration = str(internship['Duration']).lower()
            
            # Exact duration match
            if user_duration == internship_duration:
                duration_filtered.append(idx)
            # Compatible duration (e.g., user wants "12 Months" and job offers "3-5 years")
            elif ('12' in user_duration and ('year' in internship_duration or 'month' in internship_duration)) or \
                 ('6' in user_duration and 'month' in internship_duration):
                duration_filtered.append(idx)
        
        # If no duration matches, use location filtered results
        if not duration_filtered:
            duration_filtered = location_filtered
        
        # Limit the number of internships to prevent overfitting
        if len(duration_filtered) > 200:
            duration_filtered = duration_filtered[:200]
        
        # Now calculate TF-IDF similarity only for filtered internships
        if self.tfidf_vectorizer is None:
            user_tfidf, internship_tfidf = self._create_tfidf_features()
        else:
            user_skills_text = [str(user['Skills']) if not pd.isna(user['Skills']) else '']
            user_tfidf = self.tfidf_vectorizer.transform(user_skills_text)
            # Only transform filtered internships
            filtered_descriptions = self.internships_df.iloc[duration_filtered]['Role'].fillna('').astype(str).tolist()
            internship_tfidf = self.tfidf_vectorizer.transform(filtered_descriptions)
        
        # Calculate cosine similarity
        similarity_scores = cosine_similarity(
            user_tfidf, 
            internship_tfidf
        ).flatten()
        
        # Create pairs of (original_index, similarity_score)
        internship_scores = list(zip(duration_filtered, similarity_scores))
        
        # Sort by score (descending)
        internship_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N indices
        result_indices = [idx for idx, score in internship_scores[:top_n]]
        
        return result_indices
    
    def train_model(self, sample_size=500):
        """
        Train a logistic regression model on engineered features.
        
        Args:
            sample_size (int): Number of user-internship pairs to sample for training
        """
        print("Training ML recommendation model...")
        
        # Create TF-IDF features
        user_tfidf, internship_tfidf = self._create_tfidf_features()
        
        # Sample user-internship pairs for training
        pairs = []
        labels = []
        
        # Positive examples (using heuristic for now)
        num_users = min(sample_size // 10, len(self.users_df))
        
        for i in range(num_users):
            user_idx = i
            shortlisted_internships = self._shortlist_internships(user_idx, top_n=20)
            
            # Skip if no internships are shortlisted
            if not shortlisted_internships:
                continue
                
            # Create positive examples (high similarity internships)
            user_similarities = cosine_similarity(
                user_tfidf[user_idx:user_idx+1], 
                internship_tfidf[shortlisted_internships]
            ).flatten()
            
            for j, internship_idx in enumerate(shortlisted_internships):
                if j < len(user_similarities):
                    # Positive label if similarity is high
                    label = 1 if user_similarities[j] > 0.1 else 0
                    pairs.append((user_idx, internship_idx, user_similarities[j]))
                    labels.append(label)
        
        if len(pairs) == 0:
            print("No training pairs generated")
            return
        
        # Extract features for training pairs
        features_list = []
        valid_labels = []
        
        for i, (user_idx, internship_idx, similarity) in enumerate(pairs):
            if i >= len(labels):
                break
                
            # Compute interaction features
            features_df = self._compute_interaction_features(user_idx, [internship_idx])
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
    
    def get_recommendations(self, user_id, top_k=5):
        """
        Get internship recommendations for a user by ID.
        
        Args:
            user_id (int): User ID
            top_k (int): Number of recommendations to return
            
        Returns:
            list: List of recommended internships with details
        """
        # Find user index
        user_indices = self.users_df[self.users_df['UserID'] == user_id].index.tolist()
        if not user_indices:
            raise ValueError(f"User with ID {user_id} not found")
        
        user_idx = user_indices[0]
        return self._get_recommendations_by_index(user_idx, top_k)
    
    def get_recommendations_for_profile(self, user_profile, top_k=5):
        """
        Get internship recommendations for a user profile (not in dataset).
        
        Args:
            user_profile (dict): User profile dictionary
            top_k (int): Number of recommendations to return
            
        Returns:
            list: List of recommended internships with details
        """
        print(f"Getting recommendations for profile: {user_profile}")
        
        # Map user profile fields to expected column names
        mapped_profile = {
            'UserID': 9999,  # Temporary ID
            'Skills': user_profile.get('skills', ''),
            'Education': user_profile.get('education', ''),
            'PreferredDomain': user_profile.get('preferred_domain', user_profile.get('domain', '')),
            'PreferredLocation': user_profile.get('preferred_location', user_profile.get('location', 'Remote')),
            'InternshipDuration': user_profile.get('internship_duration', user_profile.get('duration', '3 months')),
            'EnrollmentStatus': user_profile.get('enrollment_status', 'Remote/Online')
        }
        
        print(f"Mapped profile: {mapped_profile}")
        
        # Handle NaN values
        for key, value in mapped_profile.items():
            if pd.isna(value):
                mapped_profile[key] = ''
        
        # Create a temporary dataframe with the user profile
        temp_user_df = pd.DataFrame([mapped_profile])
        
        # Combine with existing users
        combined_users = pd.concat([self.users_df, temp_user_df], ignore_index=True)
        
        # Get the index of the new user
        user_idx = len(combined_users) - 1
        
        # Temporarily update the users dataframe
        original_users_df = self.users_df.copy()
        self.users_df = combined_users
        
        try:
            recommendations = self._get_recommendations_by_index(user_idx, top_k)
            print(f"Generated {len(recommendations)} recommendations")
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            raise
        finally:
            # Restore original users dataframe
            self.users_df = original_users_df
        
        return recommendations
    
    def _get_recommendations_by_index(self, user_idx, top_k=5):
        """
        Get internship recommendations for a user by index.
        Prioritizes domain match, then location, then duration, then skills.
        
        Args:
            user_idx (int): User index
            top_k (int): Number of recommendations to return
            
        Returns:
            list: List of recommended internships with details
        """
        # Validate user index
        if user_idx >= len(self.users_df):
            raise ValueError(f"User index {user_idx} out of range. Max index is {len(self.users_df)-1}")
        
        user = self.users_df.iloc[user_idx]
        user_domain = str(user['PreferredDomain']).lower()
        user_location = str(user['PreferredLocation']).lower()
        user_duration = str(user['InternshipDuration']).lower()
        
        # Shortlist internships with proper filtering
        shortlisted_internships = self._shortlist_internships(user_idx, top_n=100)
        
        # If no internships are shortlisted, return empty list to prevent overfitting
        if not shortlisted_internships:
            print(f"No relevant internships found for user {user_idx}. This prevents overfitting.")
            return []
            
        # Compute features for scoring
        features_df = self._compute_interaction_features(user_idx, shortlisted_internships)
        if len(features_df) == 0:
            return []
        
        # Use priority score for ranking instead of ML model predictions
        scores = features_df['priority_score'].values
        
        # Create internship-score pairs
        internship_scores = list(zip(shortlisted_internships, scores))
        
        # Sort by score (descending)
        internship_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Generate recommendations with details
        recommendations = []
        
        for i, (internship_idx, score) in enumerate(internship_scores[:top_k]):
            internship = self.internships_df.iloc[internship_idx]
            
            # Generate detailed explanation based on matching criteria
            reasons = []
            
            # Domain match
            internship_domain = str(internship['Domain']).lower()
            if user_domain == internship_domain:
                reasons.append("exactly matches your preferred domain")
            elif user_domain in internship_domain or internship_domain in user_domain:
                reasons.append("partially matches your preferred domain")
            
            # Location match
            internship_location = str(internship['Location']).lower()
            if user_location == internship_location:
                reasons.append("exactly matches your preferred location")
            elif internship_location == 'remote' or user_location == 'remote':
                reasons.append("offers remote work")
            
            # Duration match
            internship_duration = str(internship['Duration']).lower()
            if user_duration == internship_duration:
                reasons.append("exactly matches your preferred duration")
            elif ('12' in user_duration and ('year' in internship_duration or 'month' in internship_duration)) or \
                 ('6' in user_duration and 'month' in internship_duration):
                reasons.append("has a compatible duration")
            
            # Skills match
            user_skills = self._extract_skills_set(user['Skills'])
            skill_overlap = self._calculate_skill_overlap(user_skills, str(internship['Role']))
            if skill_overlap > 0:
                reasons.append("matches your skills")
            
            # If no specific reasons, provide a general one
            if not reasons:
                reasons.append("relevant based on your profile")
            
            reason_text = " and ".join(reasons)
            
            recommendation = {
                'internship_id': int(internship['InternshipID']) if not pd.isna(internship['InternshipID']) else 0,
                'company': str(internship['Company']) if not pd.isna(internship['Company']) else 'N/A',
                'role': str(internship['Role']) if not pd.isna(internship['Role']) else 'N/A',
                'domain': str(internship['Domain']) if not pd.isna(internship['Domain']) else 'N/A',
                'location': str(internship['Location']) if not pd.isna(internship['Location']) else 'N/A',
                'type': str(internship['Type']) if not pd.isna(internship['Type']) else 'N/A',
                'duration': str(internship['Duration']) if not pd.isna(internship['Duration']) else 'N/A',
                'stipend': str(internship['Stipend']) if not pd.isna(internship['Stipend']) else 'N/A',
                'similarity_score': float(score),  # This will now be a proper score between 0 and 1
                'reason': f"This internship {reason_text}."
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def save_model(self, model_path):
        """
        Save the trained model to disk.
        
        Args:
            model_path (str): Path to save the model
        """
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'tfidf_vectorizer': self.tfidf_vectorizer
        }
        joblib.dump(model_data, model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        """
        Load a trained model from disk.
        
        Args:
            model_path (str): Path to load the model from
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        print(f"Model loaded from {model_path}")


def main():
    """Demo function to test the ML-based matching system."""
    # Initialize matcher with correct dataset paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_dataset_path = os.path.join(root_dir, 'dataset', 'Candidates_cleaned.csv')
    internship_dataset_path = os.path.join(root_dir, 'dataset', 'Jobs_cleaned.csv')
    
    matcher = MLInternshipMatcher(
        user_dataset_path=user_dataset_path,
        internship_dataset_path=internship_dataset_path
    )
    
    # Train model
    print("Training model...")
    matcher.train_model()
    
    # Save model
    model_path = os.path.join(root_dir, 'ml_models', 'internship_matcher_model.joblib')
    matcher.save_model(model_path)
    
    # Test with a few users
    print("Testing recommendations...")
    try:
        # Test with the first user in the dataset
        if len(matcher.users_df) > 0:
            first_user_id = matcher.users_df.iloc[0]['UserID']
            recommendations = matcher.get_recommendations(first_user_id, top_k=3)
            
            print(f"\nRecommendations for User {first_user_id}:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['company']} - {rec['role']}")
                print(f"   Domain: {rec['domain']}, Location: {rec['location']}")
                print(f"   Score: {rec['similarity_score']:.3f}")
                print(f"   Reason: {rec['reason']}")
                print()
    except Exception as e:
        print(f"Error testing recommendations: {e}")


if __name__ == "__main__":
    main()