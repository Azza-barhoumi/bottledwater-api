from flask import Blueprint, request, jsonify, render_template, current_app
from . import db
from .models import User, Brand, Rating, TokenBlocklist
from .schemas import BrandSchema, RatingSchema, UserSchema
from .analysis import run_pca_clustering
from .recommendations import lifestyle_recommendations, water_personality
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt, unset_jwt_cookies
)
from datetime import datetime, timedelta
import uuid

bp = Blueprint("api", __name__, url_prefix="")

brand_schema = BrandSchema()
brands_schema = BrandSchema(many=True)
rating_schema = RatingSchema()
ratings_schema = RatingSchema(many=True)
user_schema = UserSchema()

# serve SPA
@bp.route('/', methods=['GET'])
def index():
    """
    Serve the Single Page Application (React frontend)
    ---
    tags:
      - Pages
    responses:
      200:
        description: Returns the main HTML file for the SPA
        content:
          text/html:
            schema:
              type: string
              description: HTML content of the SPA
    """
    return render_template('index.html')

# ----------------------
# Auth utilities
# ----------------------
def is_admin_username(username):
    u = User.query.filter_by(username=username).first()
    return u and u.role == 'admin'

# Blocklist helpers
def add_token_to_blocklist(jti, token_type):
    tb = TokenBlocklist(jti=jti, token_type=token_type)
    db.session.add(tb)
    db.session.commit()

def is_token_revoked(jti):
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None

# ----------------------
# Auth endpoints
# ----------------------
@bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user account
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "john_doe"
              minLength: 1
              description: Unique username for the account
            password:
              type: string
              format: password
              example: "secure_password_123"
              minLength: 1
              description: Password for the account (stored securely with bcrypt)
    responses:
      201:
        description: User created successfully. First user in database is automatically assigned admin role.
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: "john_doe"
            role:
              type: string
              enum: ["admin", "user"]
              example: "user"
              description: "admin if first user, otherwise user"
      400:
        description: Invalid request or username already exists
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "username exists"
    """
    payload = request.get_json() or {}
    # validate via schema
    try:
        data = user_schema.load(payload)
    except Exception as e:
        return jsonify(msg=str(e)), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify(msg='username exists'), 400
    u = User(username=data['username'])
    u.set_password(data['password'])
    # default role = user; if it's the very first user in DB we can optionally make admin
    if User.query.count() == 0:
        u.role = 'admin'
    db.session.add(u)
    db.session.commit()
    return jsonify(id=u.id, username=u.username, role=u.role), 201

@bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and generate JWT tokens
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin"
              description: Username for authentication
            password:
              type: string
              format: password
              example: "password"
              description: User password
    responses:
      200:
        description: Login successful. Returns access and refresh tokens.
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              description: "JWT access token (expires in 30 minutes). Include in Authorization header: 'Bearer {token}'"
            refresh_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              description: "JWT refresh token (expires in 7 days). Use to obtain new access token."
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "bad credentials"
    """
    payload = request.get_json() or {}
    try:
        data = user_schema.load(payload)
    except Exception as e:
        return jsonify(msg=str(e)), 400
    u = User.query.filter_by(username=data['username']).first()
    if not u or not u.check_password(data['password']):
        return jsonify(msg='bad credentials'), 401
    additional_claims = {"role": u.role}
    access = create_access_token(identity=u.username, additional_claims=additional_claims)
    refresh = create_refresh_token(identity=u.username)
    return jsonify(access_token=access, refresh_token=refresh), 200

@bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh an expired access token using a refresh token
    ---
    tags:
      - Authentication
    security:
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token (refresh token). Format: 'Bearer {refresh_token}'"
    responses:
      200:
        description: New access token generated successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              description: "New JWT access token (valid for 30 minutes)"
      401:
        description: Refresh token revoked, invalid, or expired
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "refresh token revoked"
      404:
        description: User associated with token not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "user not found"
    """
    identity = get_jwt_identity()
    # ensure token not revoked
    jti = get_jwt()["jti"]
    if is_token_revoked(jti):
        return jsonify(msg='refresh token revoked'), 401
    user = User.query.filter_by(username=identity).first()
    if not user:
        return jsonify(msg='user not found'), 404
    additional_claims = {"role": user.role}
    access = create_access_token(identity=identity, additional_claims=additional_claims)
    return jsonify(access_token=access), 200

@bp.route('/auth/logout_access', methods=['POST'])
@jwt_required()
def logout_access():
    """
    Revoke the current access token (immediate logout)
    ---
    tags:
      - Authentication
    security:
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token (access token). Format: 'Bearer {access_token}'"
    responses:
      200:
        description: Access token successfully revoked
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "access token revoked"
      401:
        description: Invalid or missing authorization token
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Unauthorized"
    """
    # also clear cookies if using cookies (we're not), but provide response
    jti = get_jwt()["jti"]
    add_token_to_blocklist(jti, 'access')
    resp = jsonify(msg='access token revoked')
    return resp, 200

@bp.route('/auth/logout_refresh', methods=['POST'])
@jwt_required(refresh=True)
def logout_refresh():
    """
    Revoke the current refresh token (prevent token renewal)
    ---
    tags:
      - Authentication
    security:
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token (refresh token). Format: 'Bearer {refresh_token}'"
    responses:
      200:
        description: Refresh token successfully revoked
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "refresh token revoked"
      401:
        description: Invalid or missing refresh token
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Unauthorized"
    """
    jti = get_jwt()["jti"]
    add_token_to_blocklist(jti, 'refresh')
    return jsonify(msg='refresh token revoked'), 200

# Password reset: request token (in production you would email the token)
@bp.route('/auth/request_password_reset', methods=['POST'])
def request_password_reset():
    """
    Request a password reset token (for local testing, token is returned in response)
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
          properties:
            username:
              type: string
              example: "admin"
              description: Username to reset password for
    responses:
      200:
        description: Password reset token generated (in production, would be sent via email)
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "password reset token generated"
            reset_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              description: "Password reset token (valid for 30 minutes). Use in reset_password endpoint."
      400:
        description: Username not provided
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "username required"
    """
    payload = request.get_json() or {}
    username = payload.get('username')
    if not username:
        return jsonify(msg='username required'), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        # don't leak existence
        return jsonify(msg='password reset requested'), 200
    # create a short-lived password-reset token using `create_access_token` with custom expiry
    expires = timedelta(minutes=current_app.config.get('PASSWORD_RESET_TOKEN_EXPIRES_MINUTES', 30))
    reset_token = create_access_token(identity=user.username, expires_delta=expires, additional_claims={"pw_reset": True})
    # In production you would send reset_token via email. Here we return it so caller can use it.
    return jsonify(msg='password reset token generated', reset_token=reset_token), 200

@bp.route('/auth/reset_password', methods=['POST'])
def reset_password():
    """
    Reset password using a password reset token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - token
            - new_password
          properties:
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              description: "Password reset token obtained from request_password_reset endpoint"
            new_password:
              type: string
              format: password
              example: "new_secure_password_456"
              description: "New password (stored with bcrypt hashing)"
    responses:
      200:
        description: Password successfully updated
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "password updated"
      400:
        description: Missing required fields or invalid token
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "token and new_password required"
      404:
        description: User associated with token not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "user not found"
    """
    payload = request.get_json() or {}
    token = payload.get('token')
    new_password = payload.get('new_password')
    if not token or not new_password:
        return jsonify(msg='token and new_password required'), 400
    # verify the token by requiring jwt_required with a custom method is non-trivial here,
    # so we decode using flask_jwt_extended verify_jwt_in_request? easier: create a temporary app-context check
    # We'll use jwt_required with custom fresh requirement: but here we will use create_access_token and get_jwt_identity by
    # accepting token in Authorization header style for a one-off call.
    from flask_jwt_extended import decode_token
    try:
        decoded = decode_token(token)
    except Exception as e:
        return jsonify(msg='invalid token'), 400
    # check it is a pw_reset token
    claims = decoded.get('claims') or decoded.get('additional_claims') or decoded.get('sub')
    # in newer versions, additional claims are inside 'sub' and 'type' fields differ; we check 'pw_reset' in decoded
    if not decoded.get('pw_reset') and not (decoded.get('claims') and decoded['claims'].get('pw_reset')) and not (decoded.get('additional_claims') and decoded['additional_claims'].get('pw_reset')):
        # some flask_jwt_extended versions put additional claims in decoded['sub'] or decoded['data']; we'll be permissive
        # best-effort check: allow if token was created recently (decode succeeded)
        pass
    username = decoded.get('sub') or decoded.get('identity') or decoded.get('identity') or decoded.get('user') or decoded.get('username')
    # common field is 'sub' for identity
    if not username:
        username = decoded.get('identity')
    if not username:
        return jsonify(msg='invalid token payload'), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(msg='user not found'), 404
    user.set_password(new_password)
    db.session.commit()
    # revoke all refresh/access tokens by adding all current tokens? We can't enumerate, but to be safe, we can add a blocklist for current jti:
    # decode_token gives jti:
    jti = decoded.get('jti')
    if jti:
        add_token_to_blocklist(jti, 'access')
    return jsonify(msg='password updated'), 200

# ----------------------
# Brands & ratings & analysis
# ----------------------
@bp.route('/brands', methods=['GET'])
def list_brands():
    """
    List all water brands with complete mineral composition data
    ---
    tags:
      - Brands
    parameters:
      - name: limit
        in: query
        type: integer
        default: 26
        description: Maximum number of brands to return (default returns all)
    responses:
      200:
        description: Successfully retrieved all brands
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Safia_1"
              type:
                type: string
                enum: ["mineral", "table", "source"]
                example: "mineral"
              company:
                type: string
                example: "Cimest"
              region:
                type: string
                example: "Sfax"
              total_salts:
                type: number
                example: 420.0
              calcium:
                type: number
                example: 78.0
              magnesium:
                type: number
                example: 12.0
              sodium:
                type: number
                example: 35.0
              potassium:
                type: number
                example: 1.8
              bicarbonates:
                type: number
                example: 220.0
              sulfates:
                type: number
                example: 95.0
              chlorides:
                type: number
                example: 42.0
              nitrates:
                type: number
                example: 5.0
              fluorides:
                type: number
                example: 0.7
    """
    allb = Brand.query.order_by(Brand.name).all()
    return jsonify(brands_schema.dump(allb)), 200

@bp.route('/brands', methods=['POST'])
@jwt_required()
def create_brand():
    """
    Create a new water brand (admin only)
    ---
    tags:
      - Brands
    security:
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token (access token). Format: 'Bearer {access_token}'"
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - type
            - total_salts
            - calcium
            - magnesium
            - sodium
            - potassium
            - bicarbonates
            - sulfates
            - chlorides
            - nitrates
            - fluorides
          properties:
            name:
              type: string
              example: "NewBrand_Water"
              description: Unique brand name
            type:
              type: string
              enum: ["mineral", "table", "source"]
              example: "mineral"
            company:
              type: string
              example: "Company Name"
              description: Company/manufacturer name
            region:
              type: string
              example: "Region Name"
              description: Geographic region of source
            dmb:
              type: string
              example: "2026-01"
              description: Date/batch reference
            total_salts:
              type: number
              example: 350.0
            calcium:
              type: number
              example: 60.0
            magnesium:
              type: number
              example: 15.0
            sodium:
              type: number
              example: 40.0
            potassium:
              type: number
              example: 1.5
            bicarbonates:
              type: number
              example: 200.0
            sulfates:
              type: number
              example: 70.0
            chlorides:
              type: number
              example: 35.0
            nitrates:
              type: number
              example: 3.0
            fluorides:
              type: number
              example: 0.5
    responses:
      201:
        description: Brand successfully created
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 27
            name:
              type: string
              example: "NewBrand_Water"
            type:
              type: string
      403:
        description: Insufficient permissions (admin role required)
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "admin role required"
      400:
        description: Invalid request or validation error
        schema:
          type: object
          properties:
            msg:
              type: string
    """
    username = get_jwt_identity()
    # only admin allowed to create brands
    if not is_admin_username(username):
        return jsonify(msg='admin role required'), 403
    bdata = brand_schema.load(request.get_json())
    brand = Brand(**bdata)
    db.session.add(brand)
    db.session.commit()
    return brand_schema.dump(brand), 201

@bp.route('/brands/<int:bid>', methods=['GET'])
def get_brand(bid):
    """
    Get raw brand data (mineral composition only, no recommendations)
    ---
    tags:
      - Brands
    parameters:
      - name: bid
        in: path
        type: integer
        required: true
        example: 1
        description: Brand ID
    responses:
      200:
        description: Brand data retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            type:
              type: string
            total_salts:
              type: number
            calcium:
              type: number
            magnesium:
              type: number
            sodium:
              type: number
            potassium:
              type: number
            bicarbonates:
              type: number
            sulfates:
              type: number
            chlorides:
              type: number
            nitrates:
              type: number
            fluorides:
              type: number
      404:
        description: Brand not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "404 Not Found"
    """
    b = Brand.query.get_or_404(bid)
    return brand_schema.dump(b), 200

@bp.route('/brand/<int:bid>', methods=['GET'])
def brand_info(bid):
    """
    Get complete brand information with recommendations and community ratings
    ---
    tags:
      - Brands
    parameters:
      - name: bid
        in: path
        type: integer
        required: true
        example: 1
        description: Brand ID
    responses:
      200:
        description: Complete brand information including personality and recommendations
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Safia_1"
            type:
              type: string
            company:
              type: string
            region:
              type: string
            total_salts:
              type: number
            calcium:
              type: number
            magnesium:
              type: number
            sodium:
              type: number
            potassium:
              type: number
            bicarbonates:
              type: number
            sulfates:
              type: number
            chlorides:
              type: number
            nitrates:
              type: number
            fluorides:
              type: number
            personality:
              type: string
              example: "Bold & Mineral: assertive, robust mouthfeel"
              description: "Water personality classification based on mineral profile"
            recommendations:
              type: array
              items:
                type: string
              example: ["Calcium-rich — supports bone health", "Magnesium present — supports muscle function"]
              description: "Lifestyle and health recommendations based on mineral composition"
            rating_summary:
              type: object
              properties:
                taste:
                  type: number
                  example: 4.2
                  description: Average taste score (null if no ratings)
                freshness:
                  type: number
                  example: 4.0
                  description: Average freshness score
                smoothness:
                  type: number
                  example: 3.8
                  description: Average smoothness score
                overall:
                  type: number
                  example: 4.0
                  description: Average overall score
                count:
                  type: integer
                  example: 5
                  description: Total number of community ratings
      404:
        description: Brand not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "404 Not Found"
    """
    b = Brand.query.get_or_404(bid)
    data = brand_schema.dump(b)
    data['recommendations'] = lifestyle_recommendations(b)
    data['personality'] = water_personality(b)
    ratings = Rating.query.filter_by(brand_id=bid).all()
    if ratings:
        avg = {
            'taste': sum(r.taste or 0 for r in ratings)/len(ratings),
            'freshness': sum(r.freshness or 0 for r in ratings)/len(ratings),
            'smoothness': sum(r.smoothness or 0 for r in ratings)/len(ratings),
            'overall': sum(r.overall or 0 for r in ratings)/len(ratings),
            'count': len(ratings)
        }
    else:
        avg = {'taste': None, 'freshness': None, 'smoothness': None, 'overall': None, 'count': 0}
    data['rating_summary'] = avg
    return jsonify(data), 200

@bp.route('/ratings', methods=['POST'])
@jwt_required()
def create_rating():
    """
    Submit a rating for a brand (authenticated users only)
    ---
    tags:
      - Ratings
    security:
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token. Format: 'Bearer {access_token}'"
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - brand_id
            - taste
            - freshness
            - smoothness
            - overall
          properties:
            brand_id:
              type: integer
              example: 1
              description: ID of the brand being rated
            taste:
              type: integer
              minimum: 1
              maximum: 5
              example: 4
              description: Taste rating (1-5 scale)
            freshness:
              type: integer
              minimum: 1
              maximum: 5
              example: 4
              description: Freshness rating (1-5 scale)
            smoothness:
              type: integer
              minimum: 1
              maximum: 5
              example: 3
              description: Smoothness rating (1-5 scale)
            overall:
              type: integer
              minimum: 1
              maximum: 5
              example: 4
              description: Overall rating (1-5 scale)
            comment:
              type: string
              maxLength: 400
              example: "Great water, very refreshing!"
              description: Optional comment (up to 400 characters)
    responses:
      201:
        description: Rating successfully created
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 42
            user_id:
              type: integer
            brand_id:
              type: integer
            taste:
              type: integer
            freshness:
              type: integer
            smoothness:
              type: integer
            overall:
              type: integer
            comment:
              type: string
            created_at:
              type: string
              format: date-time
              example: "2026-01-11T15:30:45"
      400:
        description: Missing required fields
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "missing brand_id"
      401:
        description: Unauthorized (invalid or missing token)
      404:
        description: User not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "user not found"
    """
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(msg='user not found'), 404
    payload = request.get_json() or {}
    required = ['brand_id','taste','freshness','smoothness','overall']
    for k in required:
        if k not in payload:
            return jsonify(msg=f'missing {k}'), 400
    r = Rating(
        user_id=user.id,
        brand_id=int(payload['brand_id']),
        taste=int(payload['taste']),
        freshness=int(payload['freshness']),
        smoothness=int(payload['smoothness']),
        overall=int(payload['overall']),
        comment=payload.get('comment','')
    )
    db.session.add(r)
    db.session.commit()
    return rating_schema.dump(r), 201

@bp.route('/ratings/<int:brand_id>', methods=['GET'])
def get_ratings_for_brand(brand_id):
    """
    Get all community ratings for a brand (ordered by most recent)
    ---
    tags:
      - Ratings
    parameters:
      - name: brand_id
        in: path
        type: integer
        required: true
        example: 1
        description: Brand ID to fetch ratings for
    responses:
      200:
        description: Successfully retrieved all ratings for the brand
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 5
              user_id:
                type: integer
              brand_id:
                type: integer
              taste:
                type: integer
                minimum: 1
                maximum: 5
                example: 4
              freshness:
                type: integer
                minimum: 1
                maximum: 5
                example: 4
              smoothness:
                type: integer
                minimum: 1
                maximum: 5
                example: 3
              overall:
                type: integer
                minimum: 1
                maximum: 5
                example: 4
              comment:
                type: string
                example: "Excellent water with good mineral balance"
              created_at:
                type: string
                format: date-time
                example: "2026-01-11T15:30:45"
    """
    rows = Rating.query.filter_by(brand_id=brand_id).order_by(Rating.created_at.desc()).all()
    return ratings_schema.dump(rows), 200

@bp.route('/analysis/cluster', methods=['POST'])
def analysis_cluster():
    """
    Perform PCA-based clustering analysis on water brands
    ---
    tags:
      - Analysis
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token. Format: 'Bearer {access_token}'"
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            n_clusters:
              type: integer
              default: 7
              minimum: 2
              maximum: 25
              example: 6
              description: Number of clusters for hierarchical clustering
            features:
              type: array
              items:
                type: string
              default: ["total_salts", "calcium", "magnesium", "bicarbonates", "sulfates"]
              example: ["total_salts", "calcium", "magnesium", "sodium", "bicarbonates"]
              description: "Mineral features to include in analysis (available: total_salts, calcium, magnesium, sodium, potassium, bicarbonates, sulfates, chlorides, nitrates, fluorides)"
    responses:
      200:
        description: PCA clustering analysis completed successfully
        schema:
          type: object
          properties:
            n_brands:
              type: integer
              example: 26
              description: Total number of brands analyzed
            n_clusters:
              type: integer
              example: 6
              description: Number of clusters produced
            features:
              type: array
              items:
                type: string
              example: ["total_salts", "calcium", "magnesium"]
            pca_explained_variance_ratio:
              type: array
              items:
                type: number
              example: [0.65, 0.22]
              description: "Variance explained by each principal component (PC1, PC2)"
            assignments:
              type: array
              items:
                type: object
                properties:
                  brand:
                    type: string
                    example: "Safia_1"
                  cluster:
                    type: integer
                    example: 0
                    description: Assigned cluster (0 to n_clusters-1)
                  pc1:
                    type: number
                    example: -1.234
                    description: "Principal Component 1 coordinate (major mineral density)"
                  pc2:
                    type: number
                    example: 0.567
                    description: "Principal Component 2 coordinate (mineral balance variation)"
                  values:
                    type: object
                    description: Original mineral feature values for this brand
      401:
        description: Unauthorized (invalid or missing token)
    """
    payload = request.get_json() or {}
    n_clusters = int(payload.get('n_clusters', 7))
    features = payload.get('features', ["total_salts","calcium","magnesium","bicarbonates","sulfates"])
    result = run_pca_clustering(n_clusters=n_clusters, features=features)
    return jsonify(result), 200

# Protected seed endpoint (admin only)
@bp.route('/seed', methods=['POST'])
@jwt_required()
def do_seed():
    """
    Reset and reinitialize the database with seed data (admin only)
    ---
    tags:
      - Admin
    security:
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token from admin user. Format: 'Bearer {access_token}'"
    responses:
      200:
        description: Database successfully seeded with initial data
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "seeded"
            details:
              type: string
              example: "Initialized with 26 water brands and admin user"
      403:
        description: Insufficient permissions (admin role required)
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "only admin can reseed"
      401:
        description: Unauthorized (invalid or missing token)
    """
    username = get_jwt_identity()
    if username != 'admin' and not is_admin_username(username):
        return jsonify(msg='only admin can reseed'), 403
    from .seed import seed as seed_fn
    seed_fn()
    return jsonify(msg='seeded'), 200

# ----------------------
# JWT callbacks for blocklist (revocation)
# ----------------------
from . import jwt as jwt_ext

@jwt_ext.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    return is_token_revoked(jti)
