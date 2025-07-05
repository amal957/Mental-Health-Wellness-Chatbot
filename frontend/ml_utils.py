import os
import logging
import joblib
import numpy as np
from textblob import TextBlob

logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.is_loaded = False
        self.load_models()
    
    def load_models(self):
        """Load the pre-trained emotion detection models"""
        try:
            # Load individual model components
            model_path = 'tfidf_logreg_emotion_1750350595249.pkl'
            vectorizer_path = 'tfidf_vectorizer_1750350595247.pkl'
            encoder_path = 'label_encoder_1750350595248.pkl'
            
            logger.info("Loading emotion detection model components...")
            
            # Try to load the main model
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info("Main emotion model loaded")
            
            # Try to load the vectorizer
            if os.path.exists(vectorizer_path):
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info("TF-IDF vectorizer loaded")
            
            # Try to load the label encoder
            if os.path.exists(encoder_path):
                self.label_encoder = joblib.load(encoder_path)
                logger.info("Label encoder loaded")
            
            # Check if all components are loaded
            if self.model is not None and self.vectorizer is not None and self.label_encoder is not None:
                self.is_loaded = True
                logger.info("Complete emotion detection system loaded successfully")
            else:
                logger.warning("Some model components missing, using fallback detection")
                self.is_loaded = False
                
        except Exception as e:
            logger.error(f"Error loading emotion detection models: {str(e)}")
            self.is_loaded = False
    
    def predict_emotion(self, text):
        """Predict emotion from text"""
        if not self.is_loaded or not text.strip():
            return self._fallback_emotion_detection(text)
        
        try:
            # Clean and preprocess text
            text = str(text).strip().lower()
            
            if self.vectorizer and self.model and self.label_encoder:
                # Use the trained model
                text_vector = self.vectorizer.transform([text])
                prediction = self.model.predict(text_vector)[0]
                probabilities = self.model.predict_proba(text_vector)[0]
                
                # Get emotion label and confidence
                emotion = self.label_encoder.inverse_transform([prediction])[0]
                confidence = max(probabilities)
                
                logger.debug(f"ML prediction: {emotion} (confidence: {confidence:.2f})")
                return emotion, confidence
            else:
                logger.warning("Model components not available, using fallback")
                return self._fallback_emotion_detection(text)
                
        except Exception as e:
            logger.error(f"Error in emotion prediction: {str(e)}")
            return self._fallback_emotion_detection(text)
    
    def _fallback_emotion_detection(self, text):
        """Fallback emotion detection using rule-based approach"""
        if not text.strip():
            return 'neutral', 0.5
        
        text = text.lower()
        
        # Simple keyword-based emotion detection
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 'love', 'awesome'],
            'sadness': ['sad', 'depressed', 'upset', 'down', 'crying', 'tears', 'lonely', 'grief'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'frustrated', 'annoyed'],
            'fear': ['scared', 'afraid', 'fear', 'anxious', 'worried', 'panic', 'terrified'],
            'surprise': ['surprised', 'shocked', 'amazed', 'wow', 'unexpected'],
            'love': ['love', 'adore', 'cherish', 'romantic', 'affection', 'caring']
        }
        
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            dominant_emotion = max(emotion_scores.keys(), key=lambda x: emotion_scores[x])
            # Simple confidence based on keyword matches
            confidence = min(0.9, emotion_scores[dominant_emotion] * 0.3 + 0.3)
            return dominant_emotion, confidence
        
        return 'neutral', 0.5
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            # TextBlob returns polarity from -1 (negative) to 1 (positive)
            sentiment = blob.sentiment.polarity
            return sentiment
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return 0.0

# Global emotion detector instance
emotion_detector = EmotionDetector()
