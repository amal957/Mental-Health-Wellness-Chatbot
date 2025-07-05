import json
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Conversation, JournalEntry, EmotionHistory
from emotion_detector import emotion_detector
from analytics import EmotionAnalytics

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(full_name=full_name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent conversations
    recent_conversations = Conversation.query.filter_by(
        user_id=current_user.id
    ).order_by(Conversation.timestamp.desc()).limit(5).all()
    
    # Get recent journal entries
    recent_journals = JournalEntry.query.filter_by(
        user_id=current_user.id
    ).order_by(JournalEntry.created_at.desc()).limit(3).all()
    
    # Get basic analytics
    analytics = EmotionAnalytics(current_user.id)
    summary_stats = analytics.get_summary_stats(days=7)
    
    return render_template('dashboard.html', 
                         recent_conversations=recent_conversations,
                         recent_journals=recent_journals,
                         summary_stats=summary_stats)

@app.route('/chat')
@login_required
def chat():
    # Get conversation history
    conversations = Conversation.query.filter_by(
        user_id=current_user.id
    ).order_by(Conversation.timestamp.asc()).all()
    
    logging.info(f"Chat route: Found {len(conversations)} conversations for user {current_user.id}")
    for conv in conversations:
        user_type = "USER" if conv.is_user_message else "BOT"
        logging.info(f"  {user_type}: {conv.message[:50]}...")
    
    return render_template('chat.html', conversations=conversations)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    user_message = request.form.get('message', '').strip()
    
    logging.info(f"Received message from user {current_user.id}: '{user_message}'")
    
    if not user_message:
        logging.warning("Empty message received, redirecting")
        return redirect(url_for('chat'))
    
    # Detect emotion from user message
    emotion, confidence, sentiment_score = emotion_detector.detect_emotion(user_message)
    intensity = emotion_detector.calculate_intensity(emotion, confidence, sentiment_score)
    
    # Save user message
    user_conv = Conversation(
        user_id=current_user.id,
        message=user_message,
        is_user_message=True,
        emotion=emotion,
        emotion_confidence=confidence,
        sentiment_score=sentiment_score
    )
    db.session.add(user_conv)
    
    # Save emotion history
    emotion_history = EmotionHistory(
        user_id=current_user.id,
        emotion=emotion,
        confidence=confidence,
        sentiment_score=sentiment_score,
        intensity=intensity,
        source_type='chat',
        source_id=user_conv.id
    )
    db.session.add(emotion_history)
    
    # Generate bot response based on detected emotion
    bot_response = generate_bot_response(emotion, confidence, sentiment_score)
    
    # Save bot response
    bot_conv = Conversation(
        user_id=current_user.id,
        message=bot_response,
        is_user_message=False
    )
    db.session.add(bot_conv)
    
    try:
        db.session.commit()
        logging.info(f"Saved conversation: User said '{user_message}', Bot responded '{bot_response[:50]}...'")
        print(f"DEBUG: Conversation saved successfully. User: {user_message}, Bot: {bot_response}")
    except Exception as e:
        logging.error(f"Error saving conversation: {e}")
        print(f"DEBUG: Error saving conversation: {e}")
        db.session.rollback()
    
    return redirect(url_for('chat'))

def generate_bot_response(emotion, confidence, sentiment_score):
    """Generate contextual bot response based on detected emotion"""
    
    responses = {
        'joy': [
            "I'm so glad to hear you're feeling joyful! What's bringing you happiness today?",
            "That's wonderful! It sounds like you're in a great mood. Would you like to share what's making you feel so positive?",
            "Your joy is contagious! It's beautiful to see you feeling so uplifted."
        ],
        'sadness': [
            "I hear that you're feeling sad, and I want you to know that it's okay to feel this way. Would you like to talk about what's troubling you?",
            "I'm sorry you're going through a difficult time. Remember that sadness is a natural emotion, and it's important to acknowledge it.",
            "It sounds like you're experiencing some sadness. I'm here to listen if you'd like to share more about what you're feeling."
        ],
        'anger': [
            "I can sense your frustration. Anger can be a powerful emotion. Would you like to explore what's triggering these feelings?",
            "It sounds like something has really upset you. Sometimes it helps to talk through what's making you feel this way.",
            "I understand you're feeling angry. Let's work through this together. What's causing these intense feelings?"
        ],
        'fear': [
            "I can hear the worry in your words. Fear and anxiety can be overwhelming. What's causing you to feel this way?",
            "It's brave of you to share your fears. Remember that you're not alone in this. Would you like to talk about what's making you feel anxious?",
            "I understand you're feeling scared or anxious. These feelings are valid, and I'm here to support you through this."
        ],
        'surprise': [
            "It sounds like something unexpected happened! How are you processing this surprise?",
            "Life can certainly throw us curveballs. How are you feeling about this unexpected situation?",
            "That sounds surprising! Sometimes unexpected events can bring up a mix of emotions."
        ],
        'love': [
            "It's beautiful to hear the love and care in your words. Love is such a powerful and healing emotion.",
            "The warmth and affection you're expressing is touching. Love can be such a source of strength and joy.",
            "I can feel the love in what you're sharing. It's wonderful that you're experiencing these deep, caring feelings."
        ],
        'neutral': [
            "Thank you for sharing with me. How are you feeling overall today?",
            "I'm here to listen and support you. Is there anything specific on your mind that you'd like to discuss?",
            "How has your day been? I'm here if you need someone to talk to about anything you're experiencing."
        ]
    }
    
    import random
    emotion_responses = responses.get(emotion, responses['neutral'])
    base_response = random.choice(emotion_responses)
    
    # Add additional support based on confidence and sentiment
    if confidence > 0.8:
        if sentiment_score < -0.3:
            base_response += " I want you to know that what you're feeling is completely valid, and you don't have to go through this alone."
        elif sentiment_score > 0.3:
            base_response += " It's wonderful to see you feeling so positive!"
    
    # Add therapeutic suggestions
    suggestions = {
        'sadness': " Would you like to try some journaling or explore some resources that might help?",
        'anger': " Sometimes deep breathing or physical activity can help process these intense emotions.",
        'fear': " Remember that you have the strength to face your fears, and there are techniques that can help manage anxiety.",
        'joy': " Consider writing down what's making you happy so you can reflect on it later!",
        'love': " These positive feelings are precious - they remind us of what's truly important in life."
    }
    
    suggestion = suggestions.get(emotion, " Is there anything specific I can help you with today?")
    
    return base_response + suggestion

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not content:
            flash('Journal content cannot be empty.', 'error')
            return redirect(url_for('journal'))
        
        # Detect emotion from journal content
        emotion, confidence, sentiment_score = emotion_detector.detect_emotion(content)
        intensity = emotion_detector.calculate_intensity(emotion, confidence, sentiment_score)
        
        # Save journal entry
        journal_entry = JournalEntry(
            user_id=current_user.id,
            title=title or f"Journal Entry - {datetime.now().strftime('%B %d, %Y')}",
            content=content,
            emotion=emotion,
            emotion_confidence=confidence,
            sentiment_score=sentiment_score
        )
        db.session.add(journal_entry)
        
        # Save emotion history
        emotion_history = EmotionHistory(
            user_id=current_user.id,
            emotion=emotion,
            confidence=confidence,
            sentiment_score=sentiment_score,
            intensity=intensity,
            source_type='journal',
            source_id=journal_entry.id
        )
        db.session.add(emotion_history)
        
        db.session.commit()
        
        flash(f'Journal entry saved! Detected emotion: {emotion.title()} (Confidence: {confidence:.2f})', 'success')
        return redirect(url_for('journal'))
    
    # Get journal entries
    entries = JournalEntry.query.filter_by(
        user_id=current_user.id
    ).order_by(JournalEntry.created_at.desc()).all()
    
    return render_template('journal.html', entries=entries)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/api/analytics/emotion-distribution')
@login_required
def api_emotion_distribution():
    days = request.args.get('days', 30, type=int)
    analytics = EmotionAnalytics(current_user.id)
    data = analytics.get_emotion_distribution(days)
    return jsonify(data)

@app.route('/api/analytics/daily-mood')
@login_required
def api_daily_mood():
    days = request.args.get('days', 30, type=int)
    analytics = EmotionAnalytics(current_user.id)
    data = analytics.get_daily_mood_data(days)
    return jsonify(data)

@app.route('/api/analytics/emotion-trends')
@login_required
def api_emotion_trends():
    days = request.args.get('days', 30, type=int)
    analytics = EmotionAnalytics(current_user.id)
    data = analytics.get_emotion_trends(days)
    return jsonify(data)

@app.route('/api/analytics/emotion-frequency')
@login_required
def api_emotion_frequency():
    days = request.args.get('days', 30, type=int)
    analytics = EmotionAnalytics(current_user.id)
    data = analytics.get_emotion_frequency(days)
    return jsonify(data)

@app.route('/api/analytics/emotional-balance')
@login_required
def api_emotional_balance():
    days = request.args.get('days', 30, type=int)
    analytics = EmotionAnalytics(current_user.id)
    data = analytics.get_emotional_balance(days)
    return jsonify(data)

@app.route('/api/analytics/sentiment-trends')
@login_required
def api_sentiment_trends():
    days = request.args.get('days', 30, type=int)
    analytics = EmotionAnalytics(current_user.id)
    data = analytics.get_sentiment_trends(days)
    return jsonify(data)

@app.route('/api/analytics/summary')
@login_required
def api_summary():
    days = request.args.get('days', 30, type=int)
    analytics = EmotionAnalytics(current_user.id)
    data = analytics.get_summary_stats(days)
    return jsonify(data)

@app.route('/resources')
@login_required
def resources():
    # Get user's most common emotions for personalized recommendations
    analytics = EmotionAnalytics(current_user.id)
    emotion_frequency = analytics.get_emotion_frequency(days=14)
    
    return render_template('resources.html', emotion_frequency=emotion_frequency)
