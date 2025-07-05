import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db  # Import from extensions instead of app
from models import User, Conversation, JournalEntry
from ml_utils import emotion_detector

# Create blueprint
main_bp = Blueprint('main', __name__)

# Authentication routes
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        if not all([full_name, email, password]):
            flash('Please fill in all fields.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            full_name=full_name,
            email=email
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Account created successfully! Welcome to Mental Wellness.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'error')
            current_app.logger.error(f"Registration error: {str(e)}")
    
    return render_template('register.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.login'))

# Main application routes
@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get summary statistics
    total_entries = Conversation.query.filter_by(user_id=current_user.id, is_user_message=True).count()
    
    # Get most common emotion
    emotions = db.session.query(Conversation.emotion).filter_by(
        user_id=current_user.id, 
        is_user_message=True
    ).filter(Conversation.emotion.isnot(None)).all()
    
    if emotions:
        emotion_counter = Counter([e[0] for e in emotions])
        most_common_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else 'neutral'
    else:
        most_common_emotion = 'neutral'
    
    # Calculate average sentiment
    sentiments = db.session.query(Conversation.sentiment_score).filter_by(
        user_id=current_user.id, 
        is_user_message=True
    ).filter(Conversation.sentiment_score.isnot(None)).all()
    
    avg_sentiment = sum([s[0] for s in sentiments]) / len(sentiments) if sentiments else 0.0
    
    # Get days tracked
    earliest_entry = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.timestamp.asc()).first()
    days_tracked = 0
    if earliest_entry and earliest_entry.timestamp:
        days_tracked = (datetime.utcnow() - earliest_entry.timestamp).days + 1
    
    summary_stats = {
        'total_entries': total_entries,
        'most_common_emotion': most_common_emotion,
        'average_sentiment': avg_sentiment,
        'days_tracked': days_tracked
    }
    
    # Get recent conversations (user messages only)
    recent_conversations = Conversation.query.filter_by(
        user_id=current_user.id, 
        is_user_message=True
    ).order_by(Conversation.timestamp.desc()).limit(5).all()
    
    # Get recent journal entries
    recent_journals = JournalEntry.query.filter_by(
        user_id=current_user.id
    ).order_by(JournalEntry.created_at.desc()).limit(3).all()
    
    return render_template('dashboard.html', 
                         summary_stats=summary_stats,
                         recent_conversations=recent_conversations,
                         recent_journals=recent_journals)

@main_bp.route('/chat')
@login_required
def chat():
    conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.timestamp.asc()).all()
    return render_template('chat.html', conversations=conversations)

@main_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    # Handle both form data and JSON requests
    if request.is_json:
        data = request.get_json()
        message = data.get('message', '').strip()
    else:
        message = request.form.get('message', '').strip()
    
    if not message:
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'error': 'Please enter a message'}), 400
        flash('Please enter a message.', 'error')
        return redirect(url_for('main.chat'))
    
    try:
        # Analyze user message
        emotion, confidence = emotion_detector.predict_emotion(message)
        sentiment = emotion_detector.analyze_sentiment(message)
        
        # Save user message
        user_message = Conversation(
            user_id=current_user.id,
            message=message,
            is_user_message=True,
            emotion=emotion,
            emotion_confidence=confidence,
            sentiment_score=sentiment
        )
        db.session.add(user_message)
        
        # Generate bot response based on detected emotion
        bot_response = generate_bot_response(emotion, sentiment, message)
        
        # Save bot response
        bot_message = Conversation(
            user_id=current_user.id,
            message=bot_response,
            is_user_message=False
        )
        db.session.add(bot_message)
        
        db.session.commit()
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({
                'success': True,
                'user_message': {
                    'message': message,
                    'emotion': emotion,
                    'confidence': confidence,
                    'timestamp': user_message.timestamp.strftime('%I:%M %p') if user_message.timestamp else 'Now'
                },
                'bot_response': {
                    'message': bot_response,
                    'timestamp': bot_message.timestamp.strftime('%I:%M %p') if bot_message.timestamp else 'Now'
                }
            })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving conversation: {str(e)}")
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'error': 'An error occurred while processing your message'}), 500
        flash('An error occurred while processing your message.', 'error')
    
    return redirect(url_for('main.chat'))

def generate_bot_response(emotion, sentiment, message):
    """Generate contextual bot responses based on emotion and sentiment"""
    
    responses = {
        'joy': [
            "I'm so glad to hear you're feeling positive! That's wonderful. What's bringing you this joy today?",
            "It's beautiful to see your happiness shine through! Would you like to share more about what's making you feel so good?",
            "Your positive energy is contagious! How can we help you maintain this wonderful feeling?"
        ],
        'sadness': [
            "I can sense you're going through a difficult time. I'm here to listen and support you. Would you like to talk about what's troubling you?",
            "It's okay to feel sad sometimes. Your feelings are valid, and I'm here with you. How can I best support you right now?",
            "I'm sorry you're feeling down. Remember that it's brave to reach out and share your feelings. What would help you feel a little better today?"
        ],
        'anger': [
            "I can hear the frustration in your words. It's natural to feel angry sometimes. Would you like to talk about what's bothering you?",
            "Strong emotions like anger can be overwhelming. Let's work through this together. What triggered these feelings?",
            "I understand you're feeling upset. Taking a moment to breathe can help. What's causing this anger, and how can we address it?"
        ],
        'fear': [
            "I can sense you're feeling anxious or scared. That must be really difficult. You're safe here, and we can work through this together.",
            "Fear can be overwhelming, but you're not alone. I'm here to help you process these feelings. What's making you feel afraid?",
            "It takes courage to acknowledge fear. You're being brave by sharing this with me. How can I help you feel more secure?"
        ],
        'surprise': [
            "It sounds like something unexpected happened! How are you processing this surprise?",
            "Life can certainly throw us curveballs! How are you feeling about this unexpected turn of events?",
            "Surprises can be overwhelming. Take your time to process what happened. How can I support you through this?"
        ],
        'love': [
            "It's wonderful to hear about the love and connection in your life! These feelings are so important for our wellbeing.",
            "Love is such a beautiful emotion. It's lovely that you're experiencing these positive feelings. Tell me more about what's bringing you this joy.",
            "The love you're expressing is heartwarming. How does it feel to experience such positive emotions?"
        ],
        'neutral': [
            "Thank you for sharing with me. I'm here to listen and support you in whatever way you need.",
            "I appreciate you opening up to me. How are you feeling right now, and what would be most helpful for you?",
            "I'm glad you're here and willing to share your thoughts. What's on your mind today?"
        ]
    }
    
    # Get appropriate responses for the detected emotion
    emotion_responses = responses.get(emotion, responses['neutral'])
    
    # Add sentiment-based modifications
    if sentiment < -0.3:  # Very negative sentiment
        supportive_phrases = [
            "I want you to know that your feelings are completely valid. ",
            "It's important that you're expressing these difficult emotions. ",
            "Remember, you don't have to go through this alone. "
        ]
        import random
        prefix = random.choice(supportive_phrases)
        return prefix + random.choice(emotion_responses)
    
    elif sentiment > 0.3:  # Very positive sentiment
        encouraging_phrases = [
            "It's wonderful to hear such positivity from you! ",
            "Your positive outlook is inspiring. ",
            "I love hearing about the good things in your life. "
        ]
        import random
        prefix = random.choice(encouraging_phrases)
        return prefix + random.choice(emotion_responses)
    
    # Default response for neutral sentiment
    import random
    return random.choice(emotion_responses)

@main_bp.route('/journal')
@login_required
def journal():
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.created_at.desc()).all()
    return render_template('journal.html', entries=entries)

@main_bp.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new_journal_entry():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            flash('Please provide both a title and content for your journal entry.', 'error')
            return render_template('journal_entry.html')
        
        try:
            # Analyze the journal entry
            emotion, confidence = emotion_detector.predict_emotion(content)
            sentiment = emotion_detector.analyze_sentiment(content)
            
            # Create new journal entry
            entry = JournalEntry(
                user_id=current_user.id,
                title=title,
                content=content,
                emotion=emotion,
                emotion_confidence=confidence,
                sentiment_score=sentiment
            )
            
            db.session.add(entry)
            db.session.commit()
            
            flash('Journal entry saved successfully!', 'success')
            return redirect(url_for('main.journal'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving journal entry: {str(e)}")
            flash('An error occurred while saving your entry.', 'error')
    
    return render_template('journal_entry.html')

@main_bp.route('/journal/<int:entry_id>')
@login_required
def view_journal_entry(entry_id):
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    return render_template('journal_view.html', entry=entry)

@main_bp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@main_bp.route('/resources')
@login_required
def resources():
    return render_template('resources.html')

# Analytics API endpoints
@main_bp.route('/api/analytics/emotion-distribution')
@login_required
def emotion_distribution():
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    emotions = db.session.query(Conversation.emotion).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_user_message == True,
        Conversation.timestamp >= cutoff_date,
        Conversation.emotion.isnot(None)
    ).all()
    
    if not emotions:
        return jsonify({})
    
    emotion_counts = Counter([e[0] for e in emotions])
    total = sum(emotion_counts.values())
    
    # Convert to percentages
    distribution = {emotion: (count / total) * 100 for emotion, count in emotion_counts.items()}
    
    return jsonify(distribution)

@main_bp.route('/api/analytics/emotion-frequency')
@login_required
def emotion_frequency():
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    emotions = db.session.query(Conversation.emotion).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_user_message == True,
        Conversation.timestamp >= cutoff_date,
        Conversation.emotion.isnot(None)
    ).all()
    
    emotion_counts = Counter([e[0] for e in emotions])
    return jsonify(dict(emotion_counts))

@main_bp.route('/api/analytics/emotion-trends')
@login_required
def emotion_trends():
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    conversations = db.session.query(
        Conversation.emotion, 
        Conversation.timestamp
    ).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_user_message == True,
        Conversation.timestamp >= cutoff_date,
        Conversation.emotion.isnot(None)
    ).all()
    
    # Group by date and emotion
    daily_emotions = defaultdict(lambda: defaultdict(int))
    for emotion, timestamp in conversations:
        date_str = timestamp.strftime('%Y-%m-%d')
        daily_emotions[emotion][date_str] += 1
    
    # Convert to Chart.js format
    trends = {}
    for emotion, daily_counts in daily_emotions.items():
        trends[emotion] = [
            {'x': date, 'y': count} 
            for date, count in sorted(daily_counts.items())
        ]
    
    return jsonify(trends)

@main_bp.route('/api/analytics/emotional-balance')
@login_required
def emotional_balance():
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    emotions = db.session.query(Conversation.emotion).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_user_message == True,
        Conversation.timestamp >= cutoff_date,
        Conversation.emotion.isnot(None)
    ).all()
    
    if not emotions:
        return jsonify({})
    
    emotion_counts = Counter([e[0] for e in emotions])
    total = sum(emotion_counts.values())
    
    # Normalize to 0-1 scale for radar chart
    balance = {emotion: count / total for emotion, count in emotion_counts.items()}
    
    return jsonify(balance)

@main_bp.route('/api/analytics/sentiment-trends')
@login_required
def sentiment_trends():
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    sentiments = db.session.query(
        Conversation.sentiment_score,
        Conversation.timestamp
    ).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_user_message == True,
        Conversation.timestamp >= cutoff_date,
        Conversation.sentiment_score.isnot(None)
    ).all()
    
    # Group by date and calculate average sentiment
    daily_sentiments = defaultdict(list)
    for sentiment, timestamp in sentiments:
        date_str = timestamp.strftime('%Y-%m-%d')
        daily_sentiments[date_str].append(sentiment)
    
    # Calculate daily averages
    trends = [
        {'x': date, 'y': sum(scores) / len(scores)}
        for date, scores in sorted(daily_sentiments.items())
    ]
    
    return jsonify(trends)

@main_bp.route('/api/analytics/daily-mood')
@login_required
def daily_mood():
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    conversations = db.session.query(
        Conversation.emotion,
        Conversation.sentiment_score,
        Conversation.timestamp
    ).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_user_message == True,
        Conversation.timestamp >= cutoff_date,
        Conversation.emotion.isnot(None)
    ).all()
    
    # Create heatmap data
    heatmap_data = []
    daily_moods = defaultdict(list)
    
    for emotion, sentiment, timestamp in conversations:
        date_str = timestamp.strftime('%Y-%m-%d')
        # Convert emotion to numeric value for heatmap
        emotion_values = {
            'joy': 1, 'love': 0.8, 'surprise': 0.6, 'neutral': 0,
            'fear': -0.4, 'sadness': -0.6, 'anger': -0.8
        }
        mood_value = emotion_values.get(emotion.lower(), 0)
        if sentiment:
            mood_value = (mood_value + sentiment) / 2
        
        daily_moods[date_str].append(mood_value)
    
    # Calculate daily average mood
    for date, moods in daily_moods.items():
        avg_mood = sum(moods) / len(moods)
        heatmap_data.append({
            'date': date,
            'value': avg_mood
        })
    
    return jsonify(heatmap_data)

@main_bp.route('/api/analytics/summary')
@login_required
def analytics_summary():
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all user messages in the time range
    conversations = Conversation.query.filter(
        Conversation.user_id == current_user.id,
        Conversation.is_user_message == True,
        Conversation.timestamp >= cutoff_date
    ).all()
    
    total_entries = len(conversations)
    
    # Calculate most common emotion
    emotions = [c.emotion for c in conversations if c.emotion]
    most_common_emotion = 'neutral'
    if emotions:
        emotion_counter = Counter(emotions)
        most_common_emotion = emotion_counter.most_common(1)[0][0]
    
    # Calculate average sentiment
    sentiments = [c.sentiment_score for c in conversations if c.sentiment_score is not None]
    average_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    # Calculate days tracked
    unique_dates = set()
    for conv in conversations:
        unique_dates.add(conv.timestamp.date())
    days_tracked = len(unique_dates)
    
    return jsonify({
        'total_entries': total_entries,
        'most_common_emotion': most_common_emotion,
        'average_sentiment': average_sentiment,
        'days_tracked': days_tracked
    })