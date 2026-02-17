from pymongo import MongoClient
from datetime import datetime
class AnalyticsService:
    def __init__(self, mongodb_uri, db_name):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.conversations = self.db.conversations
    def log_conversation(self, session_id, user_input, bot_response, customer_email=None):
        try:
            conversation_log = {
                'session_id': session_id,
                'timestamp': datetime.utcnow(),
                'user_input': user_input,
                'bot_response': bot_response,
                'customer_email': customer_email,
                'input_length': len(user_input),
                'response_length': len(bot_response)
            }
            self.conversations.insert_one(conversation_log)
            return True
        except Exception as e:
            print(f"Error logging conversation: {e}")
            return False
    def get_session_history(self, session_id):
        try:
            conversations = list(
                self.conversations.find({'session_id': session_id})
                .sort('timestamp', 1)
            )
            for conv in conversations:
                conv['_id'] = str(conv['_id'])
                conv['timestamp'] = conv['timestamp'].isoformat()
            return conversations
        except Exception as e:
            print(f"Error fetching session history: {e}")
            return []
    def get_analytics_summary(self):
        try:
            total_conversations = self.conversations.count_documents({})
            unique_sessions = len(self.conversations.distinct('session_id'))
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'avg_response_length': {'$avg': '$response_length'},
                        'avg_input_length': {'$avg': '$input_length'}
                    }
                }
            ]
            avg_stats = list(self.conversations.aggregate(pipeline))
            return {
                'total_conversations': total_conversations,
                'unique_sessions': unique_sessions,
                'avg_response_length': round(avg_stats[0]['avg_response_length'], 2) if avg_stats else 0,
                'avg_input_length': round(avg_stats[0]['avg_input_length'], 2) if avg_stats else 0
            }
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {}
    def get_recent_conversations(self, limit=10):
        try:
            conversations = list(
                self.conversations.find()
                .sort('timestamp', -1)
                .limit(limit)
            )
            for conv in conversations:
                conv['_id'] = str(conv['_id'])
                conv['timestamp'] = conv['timestamp'].isoformat()
            return conversations
        except Exception as e:
            print(f"Error fetching recent conversations: {e}")
            return []
