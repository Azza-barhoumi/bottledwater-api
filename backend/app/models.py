from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ratings = db.relationship('Rating', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(50))
    dmb = db.Column(db.String(40))
    company = db.Column(db.String(120))
    region = db.Column(db.String(120))

    total_salts = db.Column(db.Float)
    calcium = db.Column(db.Float)
    magnesium = db.Column(db.Float)
    sodium = db.Column(db.Float)
    potassium = db.Column(db.Float)
    bicarbonates = db.Column(db.Float)
    sulfates = db.Column(db.Float)
    chlorides = db.Column(db.Float)
    nitrates = db.Column(db.Float)
    fluorides = db.Column(db.Float)

    ratings = db.relationship('Rating', backref='brand', lazy='dynamic')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)

    taste = db.Column(db.Integer)
    freshness = db.Column(db.Integer)
    smoothness = db.Column(db.Integer)
    overall = db.Column(db.Integer)
    comment = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TokenBlocklist(db.Model):
    """
    Store revoked JWTs. We store the jti (JWT ID), type ('access'/'refresh'), and when revoked.
    """
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
