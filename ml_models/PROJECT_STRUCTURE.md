# PM Internship Recommendation Engine - Project Structure

## Overview
This project implements a lightweight AI-based recommendation system for matching candidates with internships in the PM Internship Scheme.

## Project Structure

```
ml pm internship with kaggle/
├── dataset/
│   ├── Candidates_cleaned.csv     # Candidate data (1000 candidates)
│   └── Jobs_cleaned.csv           # Job data (5806 jobs)
├── README.md                      # Project documentation
├── PROJECT_SUMMARY.md             # High-level project summary
├── PROJECT_STRUCTURE.md           # This file
├── requirements.txt               # Python dependencies
├── simple_recommendation_engine.py # Main recommendation engine (TF-IDF + Cosine Similarity)
├── recommendation_engine.py        # Enhanced version with ML models (baseline)
├── recommendation_engine_v2.py     # Improved version with fixes
├── system_demo.py                 # Comprehensive system demonstration
├── usage_examples.py              # Practical usage examples
├── demo_recommendations.py         # Model training demo (baseline)
└── __pycache__/                   # Python cache files
```

## Key Implementation Files

### 1. [simple_recommendation_engine.py](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/simple_recommendation_engine.py)
**Main recommendation engine implementation**
- TF-IDF vectorization for skills and job descriptions
- Cosine similarity for matching candidates to jobs
- Fairness boosting for underrepresented groups
- Clean, robust implementation

### 2. [system_demo.py](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/system_demo.py)
**Comprehensive system demonstration**
- Dataset analysis
- Recommendation examples
- Fairness features showcase
- System benefits explanation

### 3. [usage_examples.py](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/usage_examples.py)
**Practical usage examples**
- Basic usage patterns
- Multiple candidate recommendations
- Programmatic access to recommendations
- Fairness awareness demonstration

### 4. [README.md](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/README.md)
**Detailed technical documentation**
- System overview and features
- Implementation details
- Usage instructions
- Future enhancement suggestions

### 5. [PROJECT_SUMMARY.md](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/PROJECT_SUMMARY.md)
**High-level project summary**
- Problem statement and solution approach
- Key features and benefits
- Sample results and performance metrics
- Technical requirements and installation

## Dataset Files

### [Candidates_cleaned.csv](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/dataset/Candidates_cleaned.csv)
**Candidate information**
- 1000 candidates
- Fields: candidate_id, skills, qualification, experience_level, job_role, experience_enc

### [Jobs_cleaned.csv](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/dataset/Jobs_cleaned.csv)
**Job/internship information**
- 5806 jobs
- Fields: Type_of_job, company_name, location, salary, experience, experience_enc

## Configuration Files

### [requirements.txt](file:///C:/Users/MADHURIMA/Desktop/ml%20pm%20internship%20with%20kaggle/requirements.txt)
**Python dependencies**
- pandas>=1.3.0
- scikit-learn>=1.0.0
- numpy>=1.21.0

## Usage Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run basic recommendations**:
   ```python
   python simple_recommendation_engine.py
   ```

3. **Run comprehensive demo**:
   ```python
   python system_demo.py
   ```

4. **Run usage examples**:
   ```python
   python usage_examples.py
   ```

## System Features

### Core Functionality
- TF-IDF vectorization of skills and job descriptions
- Cosine similarity matching
- Top-K recommendation generation
- Fairness-aware scoring adjustments

### Technical Characteristics
- **Lightweight**: Minimal computational requirements
- **Fast**: Sub-second inference time
- **Scalable**: Handles large datasets efficiently
- **Interpretable**: Clear scoring and ranking

### Fairness Features
- Score boosting for underrepresented groups
- Diverse recommendation generation
- Transparent scoring explanations

## Performance
- **Latency**: < 1 second per recommendation
- **Memory**: Efficient implementation
- **Scalability**: Tested with 1000 candidates and 5806 jobs
- **Accuracy**: TF-IDF baseline with cosine similarity

## Future Enhancements
1. Advanced ML models (Logistic Regression, LightGBM)
2. User feedback integration
3. Mobile application interface
4. Multi-language support
5. Real-time model updates