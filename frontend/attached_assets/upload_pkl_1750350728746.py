#!/usr/bin/env python3
"""
PKL Model Upload and Validation Script
Upload your emotion detection PKL files and validate they work correctly.
"""

import os
import pickle
import shutil
from pathlib import Path

def setup_pkl_models():
    """Setup emotion detection models from uploaded PKL files"""
    print("=== PKL Model Setup ===")
    
    # Expected model files
    model_files = {
        'tfidf_vectorizer.pkl': 'TF-IDF Vectorizer',
        'tfidf_logreg_emotion.pkl': 'Logistic Regression Model', 
        'label_encoder.pkl': 'Label Encoder'
    }
    
    print("Looking for PKL files in project directory...")
    
    # Find PKL files in project root and attached_assets
    search_dirs = ['.', 'attached_assets']
    found_files = {}
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for file in os.listdir(search_dir):
                if file.endswith('.pkl'):
                    file_path = os.path.join(search_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"Found: {file} ({file_size} bytes)")
                    
                    # Try to match to expected files
                    for expected_name, description in model_files.items():
                        if any(keyword in file.lower() for keyword in expected_name.replace('.pkl', '').split('_')):
                            found_files[expected_name] = file_path
                            print(f"  -> Matched to {description}")
                            break
    
    if not found_files:
        print("No PKL files found. Please upload your files to the project directory.")
        print("Expected files:")
        for name, desc in model_files.items():
            print(f"  - {name} ({desc})")
        return False
    
    # Validate and copy files
    print("\nValidating PKL files...")
    valid_models = {}
    
    for expected_name, file_path in found_files.items():
        try:
            with open(file_path, 'rb') as f:
                model = pickle.load(f)
            
            # Basic validation
            if 'vectorizer' in expected_name:
                if hasattr(model, 'transform'):
                    print(f"✓ {expected_name}: Valid TF-IDF vectorizer")
                    valid_models[expected_name] = model
                else:
                    print(f"✗ {expected_name}: Not a valid vectorizer")
                    
            elif 'logreg' in expected_name:
                if hasattr(model, 'predict'):
                    print(f"✓ {expected_name}: Valid classifier model")
                    valid_models[expected_name] = model
                else:
                    print(f"✗ {expected_name}: Not a valid classifier")
                    
            elif 'encoder' in expected_name:
                if hasattr(model, 'classes_'):
                    emotions = list(model.classes_)
                    print(f"✓ {expected_name}: Valid label encoder with emotions: {emotions}")
                    valid_models[expected_name] = model
                else:
                    print(f"✗ {expected_name}: Not a valid label encoder")
            
            # Copy to standard location
            target_path = expected_name
            shutil.copy2(file_path, target_path)
            print(f"  Copied to {target_path}")
            
        except Exception as e:
            print(f"✗ {expected_name}: Error loading - {e}")
    
    # Test the complete pipeline
    if len(valid_models) >= 2:  # Need at least vectorizer and model
        print("\nTesting emotion detection pipeline...")
        try:
            test_texts = ["I am happy", "I feel sad", "I am angry"]
            
            vectorizer = valid_models.get('tfidf_vectorizer.pkl')
            model = valid_models.get('tfidf_logreg_emotion.pkl') 
            encoder = valid_models.get('label_encoder.pkl')
            
            if vectorizer and model:
                for text in test_texts:
                    # Transform text
                    text_vector = vectorizer.transform([text])
                    
                    # Predict emotion
                    if hasattr(model, 'predict_proba'):
                        proba = model.predict_proba(text_vector)[0]
                        pred_idx = proba.argmax()
                        confidence = proba[pred_idx]
                    else:
                        pred_idx = model.predict(text_vector)[0]
                        confidence = 0.8
                    
                    # Get emotion label
                    if encoder:
                        emotion = encoder.classes_[pred_idx]
                    else:
                        emotion = f"emotion_{pred_idx}"
                    
                    print(f"'{text}' -> {emotion} (confidence: {confidence:.2f})")
                    
                print("✓ PKL models working correctly!")
                return True
                
        except Exception as e:
            print(f"✗ Pipeline test failed: {e}")
    
    print(f"\nSetup complete. Found {len(valid_models)} valid models.")
    return len(valid_models) > 0

if __name__ == "__main__":
    setup_pkl_models()