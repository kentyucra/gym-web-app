from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from app.auth import load_user_from_jwt
from app.commands import register_commands
from app.config import Config
from app.extensions import db, jwt, migrate
from app.models import (
    Exercise,
    ExerciseMedia,
    Member,
    MemberInvite,
    MemberSubscription,
    MembershipPlan,
    TrainingDay,
    TrainingDayExercise,
    TrainingDayExerciseSubstitution,
    TrainingProgram,
    TrainingWeek,
    User,
)
from app.routes.auth import auth_bp
from app.routes.health import health_bp
from app.routes.memberships import memberships_bp
from app.routes.members import members_bp
from app.routes.muscles import muscles_bp
from app.routes.notifications import notifications_bp
from app.routes.training import training_bp


SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Site Fitness API",
        "description": "Flask API for Site Fitness gym management and member portal access.",
        "version": "1.0.0",
    },
    "basePath": "/api",
    "schemes": ["http"],
    "securityDefinitions": {
        "cookieAuth": {
            "type": "apiKey",
            "name": "access_token_cookie",
            "in": "cookie",
            "description": "JWT access token cookie set by /auth/login.",
        }
    },
    "tags": [
        {"name": "Health", "description": "Service health checks"},
        {"name": "Auth", "description": "Authentication and member invite flows"},
        {"name": "Members", "description": "Gym member management"},
        {"name": "Memberships", "description": "Plans and member subscriptions"},
        {"name": "Muscles", "description": "Muscle image lookup"},
        {"name": "Notifications", "description": "WhatsApp notification utilities"},
        {"name": "Training", "description": "Exercise library and training programs"},
    ],
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "openapi",
            "route": "/api/openapi.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
}


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGINS"]}},
        supports_credentials=True,
    )

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    jwt.user_lookup_loader(load_user_from_jwt)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(members_bp, url_prefix="/api")
    app.register_blueprint(memberships_bp, url_prefix="/api")
    app.register_blueprint(muscles_bp, url_prefix="/api")
    app.register_blueprint(notifications_bp, url_prefix="/api")
    app.register_blueprint(training_bp, url_prefix="/api")
    register_commands(app)

    return app
