from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    current_user,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from app.extensions import db
from app.models import Member, User
from app.services.auth import (
    accept_member_invite,
    create_member_invite,
    get_valid_member_invite,
    normalize_email,
)
from app.services.openwa import send_member_invite_whatsapp

auth_bp = Blueprint("auth", __name__)


def error_response(message, status_code=400):
    return jsonify({"error": message}), status_code


def user_payload(user):
    return {"user": user.to_dict()}


@auth_bp.post("/auth/login")
def login():
    """Log in and set the JWT cookie.
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: owner@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login succeeded.
      400:
        description: Email or password missing.
      401:
        description: Invalid credentials.
      403:
        description: Account is not active.
    """
    data = request.get_json(silent=True) or {}
    email = normalize_email(data.get("email", ""))
    password = data.get("password", "")

    if not email or not password:
        return error_response("Email and password are required.", 400)

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return error_response("Invalid email or password.", 401)

    if user.status != "active":
        return error_response("This account is not active.", 403)

    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )
    response = jsonify(user_payload(user))
    set_access_cookies(response, access_token)

    return response


@auth_bp.post("/auth/logout")
def logout():
    """Log out and clear the JWT cookie.
    ---
    tags:
      - Auth
    responses:
      200:
        description: Logout succeeded.
    """
    response = jsonify({"status": "ok"})
    unset_jwt_cookies(response)
    return response


@auth_bp.get("/auth/me")
@jwt_required()
def me():
    """Get the current authenticated user.
    ---
    tags:
      - Auth
    security:
      - cookieAuth: []
    responses:
      200:
        description: Current user profile.
      401:
        description: Missing or invalid authentication cookie.
    """
    return jsonify(user_payload(current_user))


@auth_bp.post("/auth/member-invites")
@jwt_required()
def create_invite():
    """Create a member portal invite.
    ---
    tags:
      - Auth
    security:
      - cookieAuth: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              example: member@example.com
            memberId:
              type: integer
              example: 1
    responses:
      201:
        description: Invite created.
      400:
        description: Email is required.
      403:
        description: User cannot create invites.
    """
    if current_user.role not in {"owner", "staff", "trainer"}:
        return error_response("You do not have permission to create invites.", 403)

    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    member_id = data.get("memberId")

    if not email:
        return error_response("Email is required.", 400)

    invite, token = create_member_invite(email=email, member_id=member_id)
    frontend_origin = current_app.config["PUBLIC_FRONTEND_ORIGIN"].rstrip("/")
    invite_url = f"{frontend_origin}/register?token={token}"
    member = Member.query.get(member_id) if member_id else None
    whatsapp_delivery = send_member_invite_whatsapp(member, invite_url)

    return (
        jsonify(
            {
                "invite": invite.to_dict(),
                "inviteUrl": invite_url,
                "whatsappDelivery": whatsapp_delivery,
            }
        ),
        201,
    )


@auth_bp.post("/auth/member-invites/accept")
def accept_invite():
    """Accept a member invite and create the member login password.
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - token
            - password
          properties:
            token:
              type: string
              example: invite-token-from-url
            password:
              type: string
              example: new-password-123
    responses:
      201:
        description: Invite accepted and user created.
      400:
        description: Invalid invite token or password.
    """
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    password = data.get("password", "")

    if not token or not password:
        return error_response("Invite token and password are required.", 400)

    if len(password) < 8:
        return error_response("Password must be at least 8 characters.", 400)

    user, error = accept_member_invite(token=token, password=password)
    if error:
        return error_response(error, 400)

    return jsonify(user_payload(user)), 201


@auth_bp.get("/auth/member-invites/lookup")
def lookup_invite():
    """Look up an invite token before password setup.
    ---
    tags:
      - Auth
    parameters:
      - in: query
        name: token
        required: true
        type: string
    responses:
      200:
        description: Invite details.
      400:
        description: Invalid or expired invite token.
    """
    token = request.args.get("token", "")
    if not token:
        return error_response("Invite token is required.", 400)

    invite, error = get_valid_member_invite(token)
    if error:
        return error_response(error, 400)

    return jsonify({"invite": invite.to_dict()})
