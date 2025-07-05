from datetime import datetime, timedelta
from collections import Counter
from models import EmotionHistory, Conversation, JournalEntry
from app import db

class EmotionAnalytics:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def get_emotion_distribution(self, days=30):
        """Get emotion distribution for pie chart"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        emotions = db.session.query(EmotionHistory).filter(
            EmotionHistory.user_id == self.user_id,
            EmotionHistory.timestamp >= cutoff_date
        ).all()
        
        if not emotions:
            return {}
        
        emotion_counts = Counter([emotion.emotion for emotion in emotions])
        total_count = sum(emotion_counts.values())
        
        return {emotion: (count / total_count) * 100 
                for emotion, count in emotion_counts.items()}
    
    def get_daily_mood_data(self, days=30):
        """Get daily mood data for heatmap"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        emotions = db.session.query(EmotionHistory).filter(
            EmotionHistory.user_id == self.user_id,
            EmotionHistory.timestamp >= cutoff_date
        ).all()
        
        if not emotions:
            return []
        
        # Group by date and calculate average intensity
        daily_data = {}
        for emotion in emotions:
            date_str = emotion.timestamp.strftime('%Y-%m-%d')
            if date_str not in daily_data:
                daily_data[date_str] = []
            daily_data[date_str].append(emotion.intensity or 0.5)
        
        # Calculate average intensity per day
        result = []
        for date_str, intensities in daily_data.items():
            avg_intensity = sum(intensities) / len(intensities)
            result.append({
                'date': date_str,
                'intensity': round(avg_intensity, 2),
                'count': len(intensities)
            })
        
        return sorted(result, key=lambda x: x['date'])
    
    def get_emotion_trends(self, days=30):
        """Get emotion trends over time for line chart"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        emotions = db.session.query(EmotionHistory).filter(
            EmotionHistory.user_id == self.user_id,
            EmotionHistory.timestamp >= cutoff_date
        ).all()
        
        if not emotions:
            return {}
        
        # Group by date and emotion
        trend_data = {}
        for emotion in emotions:
            date_str = emotion.timestamp.strftime('%Y-%m-%d')
            emotion_type = emotion.emotion
            
            if date_str not in trend_data:
                trend_data[date_str] = {}
            if emotion_type not in trend_data[date_str]:
                trend_data[date_str][emotion_type] = 0
            trend_data[date_str][emotion_type] += 1
        
        # Convert to format suitable for Chart.js
        dates = sorted(trend_data.keys())
        all_emotions = set()
        for date_emotions in trend_data.values():
            all_emotions.update(date_emotions.keys())
        
        result = {}
        for emotion in all_emotions:
            result[emotion] = []
            for date in dates:
                count = trend_data[date].get(emotion, 0)
                result[emotion].append({'x': date, 'y': count})
        
        return result
    
    def get_emotion_frequency(self, days=30):
        """Get emotion frequency for bar chart"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        emotions = db.session.query(EmotionHistory).filter(
            EmotionHistory.user_id == self.user_id,
            EmotionHistory.timestamp >= cutoff_date
        ).all()
        
        if not emotions:
            return {}
        
        emotion_counts = Counter([emotion.emotion for emotion in emotions])
        return dict(emotion_counts)
    
    def get_emotional_balance(self, days=30):
        """Get emotional balance data for radar chart"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        emotions = db.session.query(EmotionHistory).filter(
            EmotionHistory.user_id == self.user_id,
            EmotionHistory.timestamp >= cutoff_date
        ).all()
        
        if not emotions:
            return {}
        
        # Define emotion categories
        emotion_categories = {
            'Positive': ['joy', 'love', 'surprise'],
            'Negative': ['sadness', 'anger', 'fear'],
            'Neutral': ['neutral']
        }
        
        category_scores = {}
        for category, emotion_list in emotion_categories.items():
            scores = []
            for emotion in emotions:
                if emotion.emotion in emotion_list:
                    scores.append(emotion.intensity or 0.5)
            
            if scores:
                category_scores[category] = sum(scores) / len(scores)
            else:
                category_scores[category] = 0
        
        return category_scores
    
    def get_sentiment_trends(self, days=30):
        """Get sentiment score trends over time"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        emotions = db.session.query(EmotionHistory).filter(
            EmotionHistory.user_id == self.user_id,
            EmotionHistory.timestamp >= cutoff_date,
            EmotionHistory.sentiment_score.isnot(None)
        ).all()
        
        if not emotions:
            return []
        
        # Group by date and calculate average sentiment
        daily_sentiment = {}
        for emotion in emotions:
            date_str = emotion.timestamp.strftime('%Y-%m-%d')
            if date_str not in daily_sentiment:
                daily_sentiment[date_str] = []
            daily_sentiment[date_str].append(emotion.sentiment_score)
        
        result = []
        for date_str, scores in daily_sentiment.items():
            avg_sentiment = sum(scores) / len(scores)
            result.append({
                'date': date_str,
                'sentiment': round(avg_sentiment, 3)
            })
        
        return sorted(result, key=lambda x: x['date'])
    
    def get_summary_stats(self, days=30):
        """Get summary statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        emotions = db.session.query(EmotionHistory).filter(
            EmotionHistory.user_id == self.user_id,
            EmotionHistory.timestamp >= cutoff_date
        ).all()
        
        if not emotions:
            return {
                'total_entries': 0,
                'most_common_emotion': 'N/A',
                'average_sentiment': 0,
                'days_tracked': 0
            }
        
        emotion_counts = Counter([emotion.emotion for emotion in emotions])
        most_common = emotion_counts.most_common(1)[0] if emotion_counts else ('N/A', 0)
        
        sentiment_scores = [e.sentiment_score for e in emotions if e.sentiment_score is not None]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        unique_dates = len(set(e.timestamp.date() for e in emotions))
        
        return {
            'total_entries': len(emotions),
            'most_common_emotion': most_common[0],
            'average_sentiment': round(avg_sentiment, 3),
            'days_tracked': unique_dates
        }
