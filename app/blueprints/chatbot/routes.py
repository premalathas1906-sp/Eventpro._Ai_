from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.chatbot import chatbot_bp
from app.ai.chatbot_engine import ChatbotEngine

# Initialize the chatbot engine
chatbot_engine = ChatbotEngine()

@chatbot_bp.route('/chatbot')
@login_required
def chat():
    return render_template('chat.html')

@chatbot_bp.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot_api():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': 'Please enter a message.', 'reply': 'Please enter a message.'})
        
    try:
        response = chatbot_engine.get_response(message, user_id=current_user.id)
        # Handle formats expected by voice_assistant.js (reply) and chat.html (response)
        if isinstance(response, dict):
            if 'reply' not in response and 'text' in response:
                response['reply'] = response['text']
            return jsonify(response)
        else:
            return jsonify({'reply': response, 'response': response})
    except Exception as e:
        return jsonify({'reply': f"Error: {str(e)}", 'response': f"Error: {str(e)}"}), 500
