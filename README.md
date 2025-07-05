# Mental Wellness Chatbot App
This is an intelligent, emotion-aware mental wellness assistant designed to help users reflect on their feelings, track emotional trends, and receive compassionate support through a chatbot interface.

Built using Flask, SQLAlchemy, and a machine learning emotion classifier, this app creates a safe, supportive space for journaling and self-awareness.

### ✨ Features
🧠 Emotion detection from user journal/chat messages using a trained ML model (TF-IDF + Logistic Regression)
🤖 Smart chatbot responses tailored to the user’s emotional state
📈 Mood tracking with emotion/sentiment trend visualizations
📝 Personal journal entries with auto-labeled emotions
🔄 Conversation history for reflection
💡 Resource page with therapy and journaling tools
📊 Analytics dashboard for insights (pie charts, trends, radar plots, etc.)

### Its working
**🧠 How the Mental Wellness Chatbot Works**
This mental wellness chatbot isn’t just chatting back with random replies — it’s powered by a trained ML model that analyzes emotions from journal-like text and gives supportive, intelligent responses.

Here’s a simplified walkthrough of how it works:

🎯 1. The User Writes a Message

On the chat.html page (or via the Streamlit UI), the user types a message like:

"I feel overwhelmed and exhausted after everything today."

🧠 2. Emotion Detection Using ML Model

This message is sent to the backend where we process it like this:
First, the text is vectorized using TF-IDF (Term Frequency-Inverse Document Frequency).
Then, it's passed through a trained Logistic Regression classifier.
The classifier predicts the emotion label (e.g., "sadness", "anger", "joy").

This happens via:
vect = tfidf.transform([text])
pred = clf.predict(vect)[0]
emotion = label_encoder.inverse_transform([pred])[0]
So if the model predicts class 2 and class 2 = "sadness", then:
→ Detected Emotion = Sadness

💬 3. Bot Generates a Response

Once emotion is detected, we craft a helpful or empathetic response. For example:

If detected emotion = sadness:
→ "I'm here for you. Want to talk more about what's been making you feel down lately?"

If detected emotion = anger:
→ "It’s okay to feel upset. Do you want to talk about what triggered it?"

These responses can either be:

Predefined templates based on emotion

Or dynamically generated using Dialogflow or another NLP engine (optional)

📊 4. Save the Interaction

Each message and the emotion are saved to a database, so:

You can view your mood trends over time

The chatbot can refer to your past states ("Last time you felt sad... is it better today?")

📋 5. Displayed in Chat UI

The chat.html file then displays:
Your message (on the right)
Bot reply (on the left)
Emotion label and timestamp
From your uploaded chat.html:

✅ It supports:

Human-like back and forth
Emojis or badges for detected emotions
Tracking emotion confidence

**1. Emotion Detection Exists**

emotion = predict_emotion_tfidf(user_message)
It uses: tfidf_vectorizer.pkl, tfidf_logreg_emotion.pkl, label_encoder.pkl
This gives you a label like: "joy", "sadness", "anger", etc.

**🧠 How Your Flask Chatbot Generates Responses**

**1. User sends a message to /send_message (via chat.html or API).**

**2. Inside routes.py, this happens:**

The emotion and confidence are predicted using your emotion_detector module:

emotion, confidence = emotion_detector.predict_emotion(message)
sentiment = emotion_detector.analyze_sentiment(message)
**3. A bot response is generated dynamically:**
bot_response = generate_bot_response(emotion, sentiment, message)
That function uses:
Emotion-specific response templates

Sentiment-based enhancements
Random selection from multiple variants for variety

### 4. Both messages are saved:

User message (with emotion + sentiment)
Bot message (is_user_message=False)
In this part:
user_message = Conversation(...)
bot_message = Conversation(message=bot_response, is_user_message=False)
db.session.add(user_message)
db.session.add(bot_message)
### 5. In the chat UI (chat.html), the frontend displays both messages using:

{% for message in conversations %}
    {% if message.is_user_message %}
        <div class="user">{{ message.message }}</div>
    {% else %}
        <div class="bot">{{ message.message }}</div>
    {% endif %}
{% endfor %}
### 📦 Where the Responses Are Stored

In the Conversation table
Each user and bot message is saved
Bot messages have: is_user_message=False
You can access them from the /chat route:
Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.timestamp.asc()).all()
![SignIn Page](https://github.com/user-attachments/assets/36a3a004-f1b9-49dc-a37c-e14cb4fe5106)
![After login](https://github.com/user-attachments/assets/8cba6958-d878-4d85-911b-9ee549901c38)
![Chat page](https://github.com/user-attachments/assets/b768bbab-724d-4612-8f5e-391ee5957561)
![Conversation flow](https://github.com/user-attachments/assets/288910ba-5754-48f4-b0d7-e156be8b466b)
![After a little conversation](https://github.com/user-attachments/assets/ad59f874-1dbb-405a-aa69-938f94a4bff1)
![Emotion Analytics](https://github.com/user-attachments/assets/1086e6e7-df46-4a5a-8f68-85313d4571a3)
![Journal entry](https://github.com/user-attachments/assets/ede64ef0-9f0c-4ef4-9a3e-616a4866d673)







