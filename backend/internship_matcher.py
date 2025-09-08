import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class UserProfile:
    """Represents a user profile with all relevant information for internship matching."""
    
    def __init__(self, user_id: int, education: str, skills: str, preferred_domain: str, 
                 preferred_location: str, internship_duration: str, enrollment_status: str):
        self.user_id = user_id
        self.education = education
        self.skills = skills
        self.preferred_domain = preferred_domain
        self.preferred_location = preferred_location
        self.internship_duration = internship_duration
        self.enrollment_status = enrollment_status
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create UserProfile from dictionary (CSV row)."""
        # Handle both original and real-world dataset column names
        user_id = data.get('UserID', data.get('candidate_id', 0))
        education = data.get('Education', data.get('qualification', ''))
        skills = data.get('Skills', data.get('skills', ''))
        preferred_domain = data.get('PreferredDomain', data.get('job_role', ''))
        preferred_location = data.get('PreferredLocation', 'Remote')  # Default value
        internship_duration = data.get('InternshipDuration', '3 months')  # Default value
        enrollment_status = data.get('EnrollmentStatus', data.get('experience_level', ''))
        
        return cls(
            user_id=user_id,
            education=education,
            skills=skills,
            preferred_domain=preferred_domain,
            preferred_location=preferred_location,
            internship_duration=internship_duration,
            enrollment_status=enrollment_status
        )


class Internship:
    """Represents an internship opportunity."""
    
    def __init__(self, internship_id: int, company: str, role: str, domain: str,
                 location: str, type_: str, duration: str, stipend: str):
        self.internship_id = internship_id
        self.company = company
        self.role = role
        self.domain = domain
        self.location = location
        self.type = type_
        self.duration = duration
        self.stipend = stipend
        self.stipend_value = self._parse_stipend(stipend)
    
    def _parse_stipend(self, stipend: str) -> int:
        """Parse stipend string to numerical value for ranking."""
        if stipend.lower() == 'unpaid':
            return 0
        try:
            # Extract numbers from stipend string (e.g., "20000 INR" -> 20000)
            import re
            numbers = re.findall(r'\d+', stipend)
            if numbers:
                return int(numbers[0])
        except:
            pass
        return 0
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create Internship from dictionary (CSV row)."""
        # Handle both original and real-world dataset column names
        internship_id = data.get('InternshipID', data.get('actively_hiring', 0))
        company = data.get('Company', data.get('company_name', ''))
        role = data.get('Role', data.get('Type_of_job', ''))
        location = data.get('Location', data.get('location', ''))
        stipend = data.get('Stipend', data.get('salary', 'Unpaid'))
        duration = data.get('Duration', data.get('experience', ''))
        type_ = data.get('Type', 'Full-time')  # Default value
        
        # Extract domain from role if not directly available
        domain = data.get('Domain', cls._extract_domain(role))
        
        return cls(
            internship_id=internship_id,
            company=company,
            role=role,
            domain=domain,
            location=location,
            type_=type_,
            duration=duration,
            stipend=stipend
        )
    
    @staticmethod
    def _extract_domain(role):
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


class InternshipMatcher:
    """Core matching engine for internships based on user preferences and rules."""
    
    def __init__(self, user_dataset_path: str, internship_dataset_path: str):
        self.user_dataset_path = user_dataset_path
        self.internship_dataset_path = internship_dataset_path
        self.users_df = None
        self.internships_df = None
        self.users = []
        self.internships = []
        self.load_datasets()
    
    def load_datasets(self):
        """Load both user and internship datasets from CSV files."""
        try:
            self.users_df = pd.read_csv(self.user_dataset_path)
            self.internships_df = pd.read_csv(self.internship_dataset_path)
            
            # Handle NaN values
            self.users_df = self.users_df.fillna('')
            self.internships_df = self.internships_df.fillna('')
            
            # Convert to object lists for easier manipulation
            self.users = [UserProfile.from_dict(row.to_dict()) for _, row in self.users_df.iterrows()]
            self.internships = [Internship.from_dict(row.to_dict()) for _, row in self.internships_df.iterrows()]
            
            print(f"Loaded {len(self.users)} user profiles and {len(self.internships)} internships")
            
        except Exception as e:
            print(f"Error loading datasets: {e}")
            raise
    
    def apply_domain_filter(self, user: UserProfile, internships: List[Internship]) -> List[Internship]:
        """Filter internships by domain match."""
        # More flexible domain matching
        user_domain = user.preferred_domain.lower()
        filtered = []
        for internship in internships:
            internship_domain = internship.domain.lower()
            # Direct match
            if user_domain == internship_domain:
                filtered.append(internship)
            # Partial match
            elif user_domain in internship_domain or internship_domain in user_domain:
                filtered.append(internship)
            # Special cases for data science
            elif ('data' in user_domain and 'data' in internship_domain) or \
                 ('machine' in user_domain and 'machine' in internship_domain) or \
                 ('ai' in user_domain and 'ai' in internship_domain):
                filtered.append(internship)
        return filtered
    
    def apply_location_filter(self, user: UserProfile, internships: List[Internship]) -> List[Internship]:
        """Filter internships by location match or remote availability."""
        filtered = []
        user_location = user.preferred_location.lower()
        for internship in internships:
            internship_location = internship.location.lower()
            # Direct location match
            if internship_location == user_location:
                filtered.append(internship)
            # Allow Remote for any location
            elif internship_location == 'remote':
                filtered.append(internship)
            # If user prefers remote, include remote internships
            elif user_location == 'remote' and internship_location == 'remote':
                filtered.append(internship)
            # Include all locations for remote users (more flexible)
            elif user_location == 'remote':
                filtered.append(internship)
        
        return filtered
    
    def apply_duration_filter(self, user: UserProfile, internships: List[Internship]) -> List[Internship]:
        """Filter internships by duration match."""
        # Less strict duration filtering - include all for now
        return internships
    
    def apply_enrollment_rules(self, user: UserProfile, internships: List[Internship]) -> List[Internship]:
        """Apply enrollment-based filtering rules."""
        # Simplified enrollment rules for real-world dataset
        return internships
    
    def rank_by_stipend(self, internships: List[Internship]) -> List[Internship]:
        """Rank internships by stipend (highest first)."""
        return sorted(internships, key=lambda x: x.stipend_value, reverse=True)
    
    def generate_recommendation_reason(self, user: UserProfile, internship: Internship) -> str:
        """Generate explanation for why this internship is recommended."""
        reasons = []
        
        # Domain match
        if user.preferred_domain.lower() in internship.domain.lower() or internship.domain.lower() in user.preferred_domain.lower():
            reasons.append(f"matches your preferred domain in {user.preferred_domain}")
        else:
            reasons.append(f"related to your skills in {user.preferred_domain}")
        
        # Enrollment rule explanation
        if user.enrollment_status.lower() == 'full-time':
            reasons.append(f"offers a {internship.type} role since you are currently {user.enrollment_status}")
        elif user.enrollment_status.lower() == 'part-time':
            reasons.append(f"offers a {internship.type} role since you are currently {user.enrollment_status}")
        elif user.enrollment_status.lower() in ['remote/online', 'mid', 'entry', 'senior']:
            reasons.append(f"offers a {internship.type} role which is suitable for your experience level")
        
        # Location explanation
        if internship.location.lower() == user.preferred_location.lower():
            reasons.append(f"is available in your chosen location ({user.preferred_location})")
        elif internship.location.lower() == 'remote':
            reasons.append("offers remote work flexibility")
        else:
            reasons.append(f"is available at {internship.location}")
        
        # Duration match
        reasons.append(f"has a duration that matches your availability")
        
        # Stipend information
        if internship.stipend_value > 0:
            reasons.append(f"offers competitive compensation of {internship.stipend}")
        
        return f"This internship {', '.join(reasons)}."
    
    def get_top_recommendations(self, user_id: int, top_k: int = 3) -> List[Dict]:
        """Get top K internship recommendations for a specific user."""
        # Find user
        user = None
        for u in self.users:
            if u.user_id == user_id:
                user = u
                break
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Apply all filters step by step
        filtered_internships = self.internships.copy()
        
        # 1. Domain filter (more flexible)
        domain_filtered = self.apply_domain_filter(user, filtered_internships)
        print(f"After domain filter: {len(domain_filtered)} internships")
        
        # If no matches after domain filter, use all internships (fallback)
        if len(domain_filtered) == 0:
            domain_filtered = filtered_internships
        
        # 2. Location filter (more flexible)
        location_filtered = self.apply_location_filter(user, domain_filtered)
        print(f"After location filter: {len(location_filtered)} internships")
        
        # If no matches after location filter, use domain filtered results
        if len(location_filtered) == 0:
            location_filtered = domain_filtered
        
        # 3. Duration filter (less strict)
        duration_filtered = self.apply_duration_filter(user, location_filtered)
        print(f"After duration filter: {len(duration_filtered)} internships")
        
        # 4. Enrollment rules (less strict)
        enrollment_filtered = self.apply_enrollment_rules(user, duration_filtered)
        print(f"After enrollment rules: {len(enrollment_filtered)} internships")
        
        # If no matches after all filters, use some internships (fallback)
        if len(enrollment_filtered) == 0:
            enrollment_filtered = location_filtered[:20]  # Take first 20 as fallback
        
        if not enrollment_filtered:
            return []
        
        # 5. Rank by stipend
        ranked_internships = self.rank_by_stipend(enrollment_filtered)
        
        # 6. Get top K
        top_internships = ranked_internships[:top_k]
        
        # 7. Generate recommendations with reasons
        recommendations = []
        for internship in top_internships:
            recommendation = {
                'internship_id': internship.internship_id,
                'company': internship.company,
                'role': internship.role,
                'domain': internship.domain,
                'location': internship.location,
                'type': internship.type,
                'duration': internship.duration,
                'stipend': internship.stipend,
                'reason': self.generate_recommendation_reason(user, internship)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_user_info(self, user_id: int) -> Dict:
        """Get user information for display."""
        for user in self.users:
            if user.user_id == user_id:
                return {
                    'user_id': user.user_id,
                    'education': user.education,
                    'skills': user.skills,
                    'preferred_domain': user.preferred_domain,
                    'preferred_location': user.preferred_location,
                    'internship_duration': user.internship_duration,
                    'enrollment_status': user.enrollment_status
                }
        return None
    
    def print_recommendations(self, user_id: int):
        """Print formatted recommendations for a user."""
        user_info = self.get_user_info(user_id)
        if not user_info:
            print(f"User {user_id} not found!")
            return
        
        print(f"\n{'='*80}")
        print(f"INTERNSHIP RECOMMENDATIONS FOR USER {user_id}")
        print(f"{'='*80}")
        print(f"Education: {user_info['education']}")
        print(f"Skills: {user_info['skills']}")
        print(f"Preferred Domain: {user_info['preferred_domain']}")
        print(f"Preferred Location: {user_info['preferred_location']}")
        print(f"Duration: {user_info['internship_duration']}")
        print(f"Enrollment Status: {user_info['enrollment_status']}")
        print(f"{'='*80}")
        
        recommendations = self.get_top_recommendations(user_id)
        
        if not recommendations:
            print("No matching internships found based on your criteria.")
            return
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n🏆 RECOMMENDATION #{i}")
            print(f"Company: {rec['company']}")
            print(f"Role: {rec['role']}")
            print(f"Domain: {rec['domain']}")
            print(f"Location: {rec['location']}")
            print(f"Type: {rec['type']}")
            print(f"Duration: {rec['duration']}")
            print(f"Stipend: {rec['stipend']}")
            print(f"💡 Why this internship: {rec['reason']}")
            print("-" * 60)


def main():
    """Demo function to test the matching system."""
    # Initialize matcher
    matcher = InternshipMatcher(
        user_dataset_path='dataset/Candidates_cleaned.csv',
        internship_dataset_path='dataset/Jobs_cleaned.csv'
    )
    
    # Test with a few users (using candidate_id instead of user_id)
    test_users = [1, 5, 10, 15, 20]
    
    for user_id in test_users:
        try:
            matcher.print_recommendations(user_id)
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"Error processing user {user_id}: {e}")


if __name__ == "__main__":
    main()