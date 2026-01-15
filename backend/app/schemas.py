from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from .models import Brand, Rating, User
from marshmallow import fields, ValidationError, validate, pre_load
import re

ma = Marshmallow()


def validate_username(username):
    """Username must be 3-20 chars, alphanumeric + underscore"""
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValidationError(
            'Username must be 3-20 characters, alphanumeric or underscore only'
        )


def validate_password_strength(password):
    """Password must be at least 1 character"""
    if not password or len(password) < 1:
        raise ValidationError('Password is required')


def validate_rating_value(value):
    """Rating must be 1-5"""
    if value is None:
        return  # Allow None/null
    if not isinstance(value, int) or value < 1 or value > 5:
        raise ValidationError('Rating must be an integer between 1 and 5')


def validate_comment(comment):
    """Comment validation - must not contain dangerous characters"""
    if comment and len(comment) > 500:
        raise ValidationError('Comment must be 500 characters or less')
    # Check for dangerous HTML/script characters
    dangerous_chars = ['<', '>', '"', "'"]
    if comment and any(char in comment for char in dangerous_chars):
        raise ValidationError('Comment contains invalid characters')


def validate_mineral_value(value):
    """Mineral values must be non-negative"""
    if value is None:
        return
    if not isinstance(value, (int, float)) or value < 0:
        raise ValidationError('Mineral value must be non-negative')


class BrandSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Brand

    id = ma.auto_field(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120)
    )
    type = fields.Str(validate=validate.Length(max=50))
    dmb = fields.Str(validate=validate.Length(max=40))
    company = fields.Str(validate=validate.Length(max=120))
    region = fields.Str(validate=validate.Length(max=120))
    
    # Mineral fields with validation
    total_salts = fields.Float(validate=validate_mineral_value, allow_none=True)
    calcium = fields.Float(validate=validate_mineral_value, allow_none=True)
    magnesium = fields.Float(validate=validate_mineral_value, allow_none=True)
    sodium = fields.Float(validate=validate_mineral_value, allow_none=True)
    potassium = fields.Float(validate=validate_mineral_value, allow_none=True)
    bicarbonates = fields.Float(validate=validate_mineral_value, allow_none=True)
    sulfates = fields.Float(validate=validate_mineral_value, allow_none=True)
    chlorides = fields.Float(validate=validate_mineral_value, allow_none=True)
    nitrates = fields.Float(validate=validate_mineral_value, allow_none=True)
    fluorides = fields.Float(validate=validate_mineral_value, allow_none=True)


class RatingSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Rating

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    brand_id = fields.Int(required=True)
    
    taste = fields.Int(required=True, validate=validate_rating_value)
    freshness = fields.Int(required=True, validate=validate_rating_value)
    smoothness = fields.Int(required=True, validate=validate_rating_value)
    overall = fields.Int(required=True, validate=validate_rating_value)
    
    comment = fields.Str(validate=validate_comment, allow_none=True)
    created_at = ma.auto_field(dump_only=True)


class UserSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(
        required=True,
        validate=validate_username,
        load_only=True
    )
    password = fields.Str(
        required=True,
        validate=validate_password_strength,
        load_only=True
    )
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
