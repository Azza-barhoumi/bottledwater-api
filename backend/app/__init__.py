from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

def create_app(config_object='app.config.Config'):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_object)
    CORS(app)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    
    # Initialize Swagger with enhanced documentation
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "BottledWater API",
            "version": "1.0.0",
            "description": "Comprehensive water mineral analysis and community rating platform with JWT authentication, PCA clustering, and personalized recommendations.",
            "contact": {
                "name": "BottledWater Team",
                "email": "support@bottledwater.example.com"
            },
            "license": {
                "name": "MIT"
            }
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "JWT Bearer token. Format: 'Bearer {token}'"
            }
        },
        "tags": [
            {
                "name": "Authentication",
                "description": "User registration, login, token refresh, and logout endpoints"
            },
            {
                "name": "Brands",
                "description": "Water brand listing, details, and mineral composition retrieval"
            },
            {
                "name": "Ratings",
                "description": "Community ratings submission and retrieval (taste, freshness, smoothness, overall)"
            },
            {
                "name": "Analysis",
                "description": "Machine learning analysis including PCA clustering and dimensionality reduction"
            },
            {
                "name": "Admin",
                "description": "Administrative operations (database seeding, data management)"
            },
            {
                "name": "Pages",
                "description": "SPA and page serving endpoints"
            }
        ]
    })

    # register blueprint(s)
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    # create tables
    with app.app_context():
        db.create_all()

    return app
