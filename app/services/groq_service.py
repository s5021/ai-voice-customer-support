from groq import Groq
from app.models import Customer, Order


class GroqService:
    def __init__(self, api_key, model="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.conversation_history = []

    def get_customer_context(self, customer_email=None, order_number=None):
        """Fetch customer and order information from database"""
        context = ""

        if customer_email:
            customer = Customer.query.filter_by(email=customer_email).first()
            if customer:
                context += f"\nCustomer: {customer.name} ({customer.email})\n"
                orders = Order.query.filter_by(customer_id=customer.id).all()
                if orders:
                    context += "Recent Orders:\n"
                    for order in orders:
                        context += f"- Order #{order.order_number}: {order.product_name} (${order.amount}) - Status: {order.status}\n"

        if order_number:
            order = Order.query.filter_by(order_number=order_number).first()
            if order:
                customer = Customer.query.get(order.customer_id)
                context += f"\nOrder #{order.order_number}\n"
                context += f"Customer: {customer.name}\n"
                context += f"Product: {order.product_name}\n"
                context += f"Amount: ${order.amount}\n"
                context += f"Status: {order.status}\n"

        return context

    def chat(self, user_message, customer_email=None,
             order_number=None, rag_context=None):
        """Process user message and generate response"""
        try:
            db_context = self.get_customer_context(
                customer_email, order_number
            )

            system_prompt = """You are a helpful customer support agent for an e-commerce company. You help customers with:
- Order status inquiries
- Product information
- Returns and refunds
- General questions
Be friendly, concise, and professional.
"""

            if rag_context:
                system_prompt += f"""
Use this knowledge base information to answer:
{rag_context}

Always cite your source when using this information.
Example: According to our policy...
"""

            if db_context:
                system_prompt += f"\n\nCustomer Information:\n{db_context}"

            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            messages = [
                {"role": "system", "content": system_prompt}
            ] + self.conversation_history

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            assistant_message = response.choices[0].message.content

            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return assistant_message

        except Exception as e:
            print(f"Error in Groq chat: {e}")
            return "I apologize, but I'm having trouble processing your request. Please try again."

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
