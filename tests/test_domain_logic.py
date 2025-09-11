"""
Test script to verify domain extraction logic in isolation
"""

import sys
import os
sys.path.append('ml_models')

from ml_internship_matcher import MLInternshipMatcher

def test_domain_extraction():
    """Test domain extraction logic."""
    # Initialize the matcher
    matcher = MLInternshipMatcher.__new__(MLInternshipMatcher)  # Create instance without calling __init__
    
    # Test cases
    test_cases = [
        ("full stack developer", "Web Development"),
        ("laravel developer", "Web Development"),
        ("python developer", "Web Development"),
        ("frontend engineer", "Web Development"),
        ("backend developer", "Web Development"),
        ("data scientist", "Data Science"),
        ("data analyst", "Data Science"),
        ("ui designer", "Design"),
        ("ux designer", "Design"),
        ("graphic designer", "Design"),
        ("sales executive", "Business Development"),
        ("business analyst", "Business Development"),
        ("accountant", "Finance"),
        ("financial analyst", "Finance"),
        ("marketing specialist", "Marketing"),
        ("hr manager", "Human Resources"),
        ("content writer", "Content Writing"),
        ("technical writer", "Content Writing"),
        ("qa engineer", "Quality Assurance"),
        ("software tester", "Quality Assurance"),
        ("project manager", "General")
    ]
    
    print("Testing domain extraction logic:")
    print("=" * 50)
    
    all_passed = True
    for role, expected_domain in test_cases:
        extracted_domain = matcher._extract_domain_from_role(role)
        status = "✅ PASS" if extracted_domain == expected_domain else "❌ FAIL"
        if extracted_domain != expected_domain:
            all_passed = False
        print(f"{status} '{role}' -> Expected: {expected_domain}, Got: {extracted_domain}")
    
    print("=" * 50)
    if all_passed:
        print("🎉 All domain extraction tests passed!")
    else:
        print("⚠️  Some domain extraction tests failed.")
    
    return all_passed

def test_recommendation_reason():
    """Test recommendation reason generation."""
    # Initialize the matcher
    matcher = MLInternshipMatcher.__new__(MLInternshipMatcher)  # Create instance without calling __init__
    
    # Test data
    internship_row = {
        'Type_of_job': 'full stack developer',
        'location': 'bangalore'
    }
    
    user_profile = {
        'skills': 'JavaScript, React, Node.js',
        'preferred_domain': 'Web Development',
        'preferred_location': 'bangalore'
    }
    
    reason = matcher._generate_recommendation_reason(internship_row, user_profile)
    print(f"\nTesting recommendation reason generation:")
    print(f"Internship: {internship_row['Type_of_job']}")
    print(f"User domain: {user_profile['preferred_domain']}")
    print(f"Generated reason: {reason}")
    
    # Check if reason contains expected elements
    expected_elements = [
        "matches your skills",
        "matches your preferred domain",
        "available in your preferred location"
    ]
    
    print("\nChecking reason elements:")
    for element in expected_elements:
        if element in reason:
            print(f"✅ Contains '{element}'")
        else:
            print(f"❌ Missing '{element}'")

if __name__ == "__main__":
    test_domain_extraction()
    test_recommendation_reason()