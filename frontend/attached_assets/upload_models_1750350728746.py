#!/usr/bin/env python3
"""
Script to help upload and setup emotion detection models.
Place your PKL files in the project directory and run this script.
"""

import os
import pickle
import logging

def setup_emotion_models():
    """Setup emotion detection models from PKL files"""
    
    # Look for common model file names
    model_files = [
        'emotion_model.pkl',
        'emotion_classifier.pkl', 
        'sentiment_model.pkl',
        'text_classifier.pkl',
        'roberta_model.pkl',
        'tfidf_model.pkl'
    ]
    
    vectorizer_files = [
        'emotion_vectorizer.pkl',
        'tfidf_vectorizer.pkl',
        'text_vectorizer.pkl',
        'vectorizer.pkl'
    ]
    
    print("Looking for emotion detection model files...")
    
    found_models = []
    found_vectorizers = []
    
    # Check current directory for model files
    for file in os.listdir('.'):
        if file.endswith('.pkl'):
            print(f"Found PKL file: {file}")
            
            # Try to load and inspect the file
            try:
                with open(file, 'rb') as f:
                    obj = pickle.load(f)
                    obj_type = type(obj).__name__
                    print(f"  - Type: {obj_type}")
                    
                    # Check if it might be a model or vectorizer
                    if hasattr(obj, 'predict') or hasattr(obj, 'predict_proba'):
                        found_models.append(file)
                        print(f"  - Identified as potential MODEL")
                    elif hasattr(obj, 'transform') or hasattr(obj, 'fit_transform'):
                        found_vectorizers.append(file)
                        print(f"  - Identified as potential VECTORIZER")
                    else:
                        print(f"  - Unknown object type, might need manual inspection")
                        
            except Exception as e:
                print(f"  - Error loading {file}: {e}")
    
    # Rename files to standard names if found
    if found_models:
        model_file = found_models[0]
        if model_file != 'emotion_model.pkl':
            os.rename(model_file, 'emotion_model.pkl')
            print(f"Renamed {model_file} to emotion_model.pkl")
    
    if found_vectorizers:
        vectorizer_file = found_vectorizers[0]
        if vectorizer_file != 'emotion_vectorizer.pkl':
            os.rename(vectorizer_file, 'emotion_vectorizer.pkl')
            print(f"Renamed {vectorizer_file} to emotion_vectorizer.pkl")
    
    print("\nSetup complete!")
    print("The emotion detector will now use your PKL files.")
    
    return len(found_models) > 0 and len(found_vectorizers) > 0

if __name__ == "__main__":
    setup_emotion_models()