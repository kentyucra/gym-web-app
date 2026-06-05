from flask_jwt_extended import verify_jwt_in_request
from functools import wraps

from app.models import User


def load_user_from_jwt(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(int(identity))


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            from flask_jwt_extended import current_user

            if current_user.role not in roles:
                return {"error": "You do not have permission for this action."}, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator

