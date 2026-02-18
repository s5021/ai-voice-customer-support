from flask import Blueprint, request, jsonify, render_template
from app.models import Customer, Order
from app.services import DeepgramService, GroqService, AnalyticsService, RAGService
from app.config import Config
import uuid
import os

api = Blueprint('api', __name__)

deepgram_service = DeepgramService(Config.DEEPGRAM_API_KEY)
groq_service = GroqService(Config.GROQ_API_KEY, Config.GROQ_MODEL)
analytics_service = AnalyticsService(Config.MONGODB_URI, Config.MONGODB_DB_NAME)
rag_service = RAGService(Config.GROQ_API_KEY)

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

        rag_result = rag_service.query(user_message)
        rag_context = None
        rag_sources = []

        if rag_result["used_rag"] and rag_result["answer"]:
            rag_context = rag_result["answer"]
            rag_sources = rag_result["sources"]

        response = groq_service.chat(
            user_message,
            customer_email=customer_email,
            order_number=order_number,
            rag_context=rag_context
        )

        analytics_service.log_conversation(
            session_id=session_id,
            user_input=user_message,
            bot_response=response,
            customer_email=customer_email
        )

        return jsonify({
            'response': response,
            'session_id': session_id,
            'rag_sources': rag_sources,
            'used_rag': rag_result["used_rag"]
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


@api.route('/api/upload-doc', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filepath = os.path.join('knowledge_base/docs', file.filename)
        file.save(filepath)

        success = rag_service.add_document(filepath)

        if success:
            return jsonify({
                'message': f'Document {file.filename} added successfully!'
            })
        else:
            return jsonify({'error': 'Failed to add document'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/api/reload-knowledge-base', methods=['POST'])
def reload_knowledge_base():
    try:
        success = rag_service.reload_knowledge_base()
        if success:
            return jsonify({'message': 'Knowledge base reloaded!'})
        else:
            return jsonify({'error': 'Failed to reload'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/api/reset', methods=['POST'])
def reset_conversation():
    try:
        groq_service.reset_conversation()
        return jsonify({'message': 'Conversation reset successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500