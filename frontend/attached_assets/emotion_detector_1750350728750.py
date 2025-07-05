import os
import pickle
import logging
import joblib
from textblob import TextBlob

class EmotionDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.emotion_labels = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'love', 'neutral']
        self.load_models()
    
    def load_models(self):
        """Load the pre-trained emotion detection models"""
        try:
            # Look for various model file patterns
            model_files = [
                'emotion_model.pkl',
                'emotion_classifier.pkl', 
                'sentiment_model.pkl',
                'text_classifier.pkl',
                'model.pkl'
            ]
            
            vectorizer_files = [
                'emotion_vectorizer.pkl',
                'tfidf_vectorizer.pkl',
                'text_vectorizer.pkl',
                'vectorizer.pkl'
            ]
            
            label_encoder_files = [
                'label_encoder.pkl',
                'emotion_label_encoder.pkl',
                'encoder.pkl'
            ]
            
            model_loaded = False
            vectorizer_loaded = False
            label_encoder_loaded = False
            
            # Try to find and load model
            for model_file in model_files:
                model_path = os.path.join(os.getcwd(), model_file)
                if os.path.exists(model_path):
                    try:
                        # Try pickle first
                        with open(model_path, 'rb') as f:
                            self.model = pickle.load(f)
                        model_loaded = True
                        logging.info(f"Successfully loaded model from {model_file}")
                        break
                    except:
                        try:
                            # Try joblib
                            self.model = joblib.load(model_path)
                            model_loaded = True
                            logging.info(f"Successfully loaded model from {model_file} using joblib")
                            break
                        except Exception as e:
                            logging.warning(f"Failed to load {model_file}: {e}")
                            continue
            
            # Try to find and load vectorizer
            for vec_file in vectorizer_files:
                vec_path = os.path.join(os.getcwd(), vec_file)
                if os.path.exists(vec_path):
                    try:
                        # Try pickle first
                        with open(vec_path, 'rb') as f:
                            self.vectorizer = pickle.load(f)
                        vectorizer_loaded = True
                        logging.info(f"Successfully loaded vectorizer from {vec_file}")
                        break
                    except:
                        try:
                            # Try joblib
                            self.vectorizer = joblib.load(vec_path)
                            vectorizer_loaded = True
                            logging.info(f"Successfully loaded vectorizer from {vec_file} using joblib")
                            break
                        except Exception as e:
                            logging.warning(f"Failed to load {vec_file}: {e}")
                            continue
            
            # Try to find and load label encoder
            for le_file in label_encoder_files:
                le_path = os.path.join(os.getcwd(), le_file)
                if os.path.exists(le_path):
                    try:
                        # Try pickle first
                        with open(le_path, 'rb') as f:
                            self.label_encoder = pickle.load(f)
                        label_encoder_loaded = True
                        logging.info(f"Successfully loaded label encoder from {le_file}")
                        break
                    except:
                        try:
                            # Try joblib
                            self.label_encoder = joblib.load(le_path)
                            label_encoder_loaded = True
                            logging.info(f"Successfully loaded label encoder from {le_file} using joblib")
                            break
                        except Exception as e:
                            logging.warning(f"Failed to load {le_file}: {e}")
                            continue
            
            if not model_loaded or not vectorizer_loaded:
                logging.warning("Model or vectorizer files not found. Using fallback emotion detection.")
                self.model = None
                self.vectorizer = None
                self.label_encoder = None
            else:
                # Validate loaded models
                if not (hasattr(self.model, 'predict') or hasattr(self.model, 'predict_proba')):
                    logging.warning("Loaded model doesn't have predict method. Using fallback.")
                    self.model = None
                
                if not (hasattr(self.vectorizer, 'transform') or hasattr(self.vectorizer, 'fit_transform')):
                    logging.warning("Loaded vectorizer doesn't have transform method. Using fallback.")
                    self.vectorizer = None
                
                if label_encoder_loaded and self.label_encoder:
                    # Update emotion labels from label encoder if available
                    if hasattr(self.label_encoder, 'classes_'):
                        self.emotion_labels = list(self.label_encoder.classes_)
                        logging.info(f"Updated emotion labels from encoder: {self.emotion_labels}")
                
                if model_loaded and vectorizer_loaded:
                    logging.info("Successfully loaded all emotion detection models!")
                    
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            self.model = None
            self.vectorizer = None
    
    def detect_emotion(self, text):
        """Detect emotion from text"""
        if not text or not text.strip():
            return 'neutral', 0.5, 0.0
        
        try:
            if self.model and self.vectorizer:
                # Use trained models
                return self._predict_with_model(text)
            else:
                # Fallback to rule-based detection
                return self._fallback_detection(text)
        except Exception as e:
            logging.error(f"Error in emotion detection: {e}")
            return 'neutral', 0.5, 0.0
    
    def _predict_with_model(self, text):
        """Predict emotion using trained model"""
        try:
            # Vectorize the text
            text_vector = self.vectorizer.transform([text])
            
            # Predict emotion
            prediction_encoded = self.model.predict(text_vector)[0]
            probabilities = self.model.predict_proba(text_vector)[0]
            confidence = max(probabilities)
            
            # Decode prediction if label encoder is available
            if self.label_encoder and hasattr(self.label_encoder, 'inverse_transform'):
                try:
                    prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
                except:
                    # Fallback: use index to get emotion from labels
                    if isinstance(prediction_encoded, (int, float)) and 0 <= int(prediction_encoded) < len(self.emotion_labels):
                        prediction = self.emotion_labels[int(prediction_encoded)]
                    else:
                        prediction = str(prediction_encoded)
            else:
                # If no label encoder, assume prediction is already decoded or use as index
                if isinstance(prediction_encoded, (int, float)) and 0 <= int(prediction_encoded) < len(self.emotion_labels):
                    prediction = self.emotion_labels[int(prediction_encoded)]
                else:
                    prediction = str(prediction_encoded)
            
            # Get sentiment score
            sentiment_score = self._get_sentiment_score(text)
            
            logging.info(f"Model prediction: {prediction} (confidence: {confidence:.3f})")
            return prediction, confidence, sentiment_score
            
        except Exception as e:
            logging.error(f"Error in model prediction: {e}")
            return self._fallback_detection(text)
    
    def _fallback_detection(self, text):
        """Fallback emotion detection using keyword matching"""
        text_lower = text.lower()
        
        # Enhanced emotion keywords for better detection
        emotion_keywords = {
            'joy': ['happy', 'joyful', 'excited', 'cheerful', 'glad', 'delighted', 'elated', 'content', 'thrilled', 'ecstatic', 'blissful', 'pleased', 'wonderful', 'fantastic', 'great', 'amazing', 'awesome', 'brilliant', 'excellent'],
            'sadness': ['sad', 'depressed', 'down', 'unhappy', 'melancholy', 'gloomy', 'miserable', 'heartbroken', 'sorrowful', 'dejected', 'disappointed', 'hurt', 'upset', 'blue', 'low', 'terrible', 'awful', 'bad'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 'rage', 'outraged', 'livid', 'irate', 'enraged', 'indignant', 'incensed', 'pissed', 'hostile'],
            'fear': ['scared', 'afraid', 'anxious', 'worried', 'nervous', 'terrified', 'panicked', 'frightened', 'fearful', 'apprehensive', 'concerned', 'uneasy', 'distressed', 'alarmed'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'startled', 'astounded', 'flabbergasted', 'dumbfounded'],
            'love': ['love', 'adore', 'cherish', 'affection', 'romantic', 'caring', 'devoted', 'fond', 'attached', 'passionate', 'infatuated'],
            'neutral': ['okay', 'fine', 'normal', 'regular', 'usual', 'alright', 'decent', 'average']
        }
        
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            detected_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(0.8, emotion_scores[detected_emotion] * 0.2 + 0.3)
        else:
            detected_emotion = 'neutral'
            confidence = 0.5
        
        sentiment_score = self._get_sentiment_score(text)
        
        return detected_emotion, confidence, sentiment_score
    
    def _get_sentiment_score(self, text):
        """Get sentiment score using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity  # Returns value between -1 and 1
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return 0.0
    
    def calculate_intensity(self, emotion, confidence, sentiment_score):
        """Calculate emotion intensity based on various factors"""
        base_intensity = confidence
        
        # Adjust based on sentiment for certain emotions
        if emotion in ['joy', 'love']:
            intensity = base_intensity * (1 + sentiment_score * 0.5)
        elif emotion in ['sadness', 'anger', 'fear']:
            intensity = base_intensity * (1 - sentiment_score * 0.5)
        else:
            intensity = base_intensity
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, intensity))

# Global emotion detector instance
emotion_detector = EmotionDetector()
