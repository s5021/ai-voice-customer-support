from flask import Blueprint, request, jsonify, render_template
from app.models import Customer, Order
from app.services import DeepgramService, GroqService, AnalyticsService
from app.config import Config
import uuid
api = Blueprint('api', __name__)
deepgram_service = DeepgramService(Config.DEEPGRAM_API_KEY)
groq_service = GroqService(Config.GROQ_API_KEY, Config.GROQ_MODEL)
analytics_service = AnalyticsService(Config.MONGODB_URI, Config.MONGODB_DB_NAME)
sessions = {}
@api.route('/')
def index():
    return render_template('index.html')
@api.route('/api/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.get_json()
        audio_data = data.get('audio')
        if not audio_data:
            return jsonify({'error': 'No audio data provided'}), 400
        transcript = deepgram_service.transcribe_audio(audio_data)
        if transcript is None:
            return jsonify({'error': 'Failed to transcribe audio'}), 500
        return jsonify({'text': transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@api.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message')
        session_id = data.get('session_id', str(uuid.uuid4()))
        customer_email = data.get('customer_email')
        order_number = data.get('order_number')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        response = groq_service.chat(
            user_message,
            customer_email=customer_email,
            order_number=order_number
        )
        analytics_service.log_conversation(
            session_id=session_id,
            user_input=user_message,
            bot_response=response,
            customer_email=customer_email
        )
        return jsonify({
            'response': response,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@api.route('/api/synthesize', methods=['POST'])
def synthesize():
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        audio_data = deepgram_service.synthesize_speech(text)
        if audio_data is None:
            return jsonify({'error': 'Failed to synthesize speech'}), 500
        return jsonify({'audio': audio_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@api.route('/api/customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        orders = Order.query.filter_by(customer_id=customer_id).all()
        return jsonify({
            'customer': customer.to_dict(),
            'orders': [order.to_dict() for order in orders]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@api.route('/api/customer/email/<email>', methods=['GET'])
def get_customer_by_email(email):
    try:
        customer = Customer.query.filter_by(email=email).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        orders = Order.query.filter_by(customer_id=customer.id).all()
        return jsonify({
            'customer': customer.to_dict(),
            'orders': [order.to_dict() for order in orders]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@api.route('/api/order/<order_number>', methods=['GET'])
def get_order(order_number):
    try:
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        customer = Customer.query.get(order.customer_id)
        return jsonify({
            'order': order.to_dict(),
            'customer': customer.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@api.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        summary = analytics_service.get_analytics_summary()
        recent = analytics_service.get_recent_conversations(limit=5)
        return jsonify({
            'summary': summary,
            'recent_conversations': recent
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@api.route('/api/reset', methods=['POST'])
def reset_conversation():
    try:
        groq_service.reset_conversation()
        return jsonify({'message': 'Conversation reset successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
