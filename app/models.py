from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship
    orders = db.relationship('Order', backref='customer', lazy=True)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat()
        }
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'order_number': self.order_number,
            'product_name': self.product_name,
            'amount': self.amount,
            'status': self.status,
            'order_date': self.order_date.isoformat()
        }
def init_db(app):
    """Initialize database with sample data"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if Customer.query.first() is None:
            customer1 = Customer(
                name='John Doe',
                email='john@example.com',
                phone='+1234567890'
            )
            customer2 = Customer(
                name='Jane Smith',
                email='jane@example.com',
                phone='+0987654321'
            )
            db.session.add(customer1)
            db.session.add(customer2)
            db.session.commit()
            order1 = Order(
                customer_id=customer1.id,
                order_number='ORD-001',
                product_name='Wireless Headphones',
                amount=99.99,
                status='delivered'
            )
            order2 = Order(
                customer_id=customer1.id,
                order_number='ORD-002',
                product_name='Laptop Stand',
                amount=49.99,
                status='shipped'
            )
            order3 = Order(
                customer_id=customer2.id,
                order_number='ORD-003',
                product_name='USB-C Cable',
                amount=19.99,
                status='pending'
            )
            db.session.add(order1)
            db.session.add(order2)
            db.session.add(order3)
            db.session.commit()
            print("Database initialized with sample data!")
