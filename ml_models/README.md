# PM Internship Recommendation Engine

A lightweight AI-based recommendation system for suggesting relevant internships to candidates in the PM Internship Scheme.

## Overview

This recommendation engine helps match candidates with suitable internships based on their skills, qualifications, experience, and preferences. The system is designed to be:

- **Lightweight**: Fast inference with minimal compute requirements
- **Mobile-friendly**: Simple interface suitable for low digital literacy users
- **Fairness-aware**: Incorporates affirmative action considerations
- **Scalable**: Can handle large numbers of candidates and jobs

## Features

### Candidate Features
- Skills vector (multi-hot representation)
- Qualification (ordinal/label-encoded)
- Experience level (numeric/ordinal)
- Preferred location
- Rural/urban flag (for fairness)

### Job Features
- Job title/type (TF-IDF representation)
- Company industry
- Location (region code)
- Experience requirements
- Stipend/salary
- Sector/industry

### Interaction Features
- Skill overlap (Jaccard similarity)
- Location match
- Experience alignment
- Sector alignment

## Implementation

### Simple TF-IDF Approach (`simple_recommendation_engine.py`)

The current implementation uses a TF-IDF + cosine similarity approach:

1. **Text Processing**: Skills and job descriptions are converted to TF-IDF vectors
2. **Similarity Calculation**: Cosine similarity between candidate and job vectors
3. **Ranking**: Jobs are ranked by similarity score
4. **Fairness Boost**: Small score boost for underrepresented groups

### Advanced Model Approach (Conceptual)

For future enhancement, the system can incorporate:

1. **Logistic Regression**: On engineered features for binary classification
2. **LightGBM Ranker**: For learning-to-rank with NDCG optimization
3. **Neural Dual-Encoder**: For semantic matching with contrastive loss

## Datasets

### Candidates (`Candidates_cleaned.csv`)
- `candidate_id`: Unique identifier
- `skills`: Comma-separated list of skills
- `qualification`: Educational background
- `experience_level`: Experience category
- `job_role`: Preferred job role
- `experience_enc`: Encoded experience level

### Jobs (`Jobs_cleaned.csv`)
- `Type_of_job`: Job title/description
- `company_name`: Company offering the internship
- `location`: Job location
- `salary`: Stipend/salary information
- `experience`: Experience requirements
- `experience_enc`: Encoded experience requirements

## Usage

### Installation
```bash
pip install pandas scikit-learn numpy
```

### Running Recommendations
```python
from simple_recommendation_engine import SimpleInternshipRecommendationEngine

# Initialize the engine
engine = SimpleInternshipRecommendationEngine(
    'dataset/Candidates_cleaned.csv',
    'dataset/Jobs_cleaned.csv'
)

# Get recommendations for candidate 0
engine.display_recommendations(0, top_k=5)
```

## Fairness Strategy

The system incorporates fairness considerations through:

1. **Score Boosting**: Small multiplier for candidates from rural/underrepresented groups
2. **Affirmative Action**: Ensuring diverse recommendations
3. **Monitoring**: Tracking performance across different groups

## Evaluation Metrics

### Ranking Metrics
- Precision@3, Precision@5
- NDCG@3, NDCG@5
- MRR (Mean Reciprocal Rank)

### Classification Metrics
- ROC-AUC
- F1-score
- Recall

### Fairness Metrics
- Group-wise Precision@k (rural vs urban)
- Equity across categories

## System Architecture

```
[User Input] → [Candidate Profile]
                    ↓
         [TF-IDF Vectorization]
                    ↓
        [Cosine Similarity Scoring]
                    ↓
         [Fairness Adjustment]
                    ↓
        [Top-K Recommendation]
                    ↓
            [Output Display]
```

## Performance

- **Latency**: Sub-second inference for individual candidates
- **Scalability**: Handles thousands of jobs and candidates
- **Accuracy**: TF-IDF baseline with fairness adjustments

## Future Enhancements

1. **Advanced Models**: Implement logistic regression or LightGBM ranker
2. **User Feedback Loop**: Incorporate explicit feedback for continuous learning
3. **Real-time Updates**: Dynamic model updating as new jobs are posted
4. **Mobile Interface**: Web-based mobile-friendly UI
5. **Multi-language Support**: Support for regional languages

## Example Output

```
Recommendations for Candidate 1:
Skills: python, sql, tensorflow, machine learning, communication
Qualification: master's in data science
Experience Level: senior
--------------------------------------------------
1. machine learning developer (python)
   Company: warewe consultancy private limited
   Location: gurgaon
   Salary: ₹  5 - 7 lpa
   Experience Required: 0-5 years
   Match Score: 0.6655

2. business communication executive
   Company: scg design solutions
   Location: chandigarh
   Salary: ₹  2.4 - 3.6 lpa
   Experience Required: 0-2 years
   Match Score: 0.4896
```

## License

This project is for educational purposes as part of the ML PM Internship program.