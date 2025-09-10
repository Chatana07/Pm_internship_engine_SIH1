#!/usr/bin/env python3
"""
Visualization script to create confusion matrix plot for the ML model evaluation
"""

import json
import numpy as np
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Try to import matplotlib, if not available, provide instructions
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available. To install, run: pip install matplotlib seaborn")

def create_confusion_matrix_plot():
    """Create and save confusion matrix visualization."""
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot create visualization without matplotlib. Please install it first.")
        return
    
    # Load evaluation results
    try:
        with open('ml_model_evaluation_results.json', 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("Evaluation results file not found. Please run the evaluation script first.")
        return
    
    # Extract confusion matrix
    if 'confusion_matrix' not in results:
        print("Confusion matrix not found in results.")
        return
    
    cm = np.array(results['confusion_matrix'])
    
    # Create heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Predicted Negative', 'Predicted Positive'],
                yticklabels=['Actual Negative', 'Actual Positive'])
    
    plt.title('Confusion Matrix for ML Internship Matcher')
    plt.xlabel('Predicted Label')
    plt.ylabel('Actual Label')
    
    # Add accuracy information to the plot
    tn, fp, fn, tp = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    plt.figtext(0.15, 0.02, f'Accuracy: {accuracy:.4f}', fontsize=12)
    
    # Save plot
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Confusion matrix visualization saved as 'confusion_matrix.png'")

def main():
    """Main function to create visualization."""
    print("Creating confusion matrix visualization...")
    create_confusion_matrix_plot()

if __name__ == "__main__":
    main()