from datetime import date

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Member
from app.routes.auth import error_response
from app.services.auth import create_member_invite, normalize_email
from app.services.openwa import send_member_invite_whatsapp

members_bp = Blueprint("members", __name__)


def parse_date(value):
    if not value:
        return None

    return date.fromisoformat(value)


def staff_required():
    return current_user.role in {"owner", "staff", "trainer"}


@members_bp.get("/members")
@jwt_required()
def list_members():
    """List recent members.
    ---
    tags:
      - Members
    security:
      - cookieAuth: []
    responses:
      200:
        description: Recent members.
      403:
        description: User cannot view members.
    """
    if not staff_required():
        return error_response("You do not have permission to view members.", 403)

    members = Member.query.order_by(Member.created_at.desc()).limit(100).all()

    return jsonify({"members": [member.to_dict() for member in members]})


@members_bp.post("/members")
@jwt_required()
def create_member():
    """Create a gym member and optionally send a WhatsApp portal invite.
    ---
    tags:
      - Members
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
            - fullName
          properties:
            fullName:
              type: string
              example: Maria Quispe
            dni:
              type: string
              example: "12345678"
            phone:
              type: string
              example: "948327856"
            email:
              type: string
              example: maria@example.com
            dateOfBirth:
              type: string
              format: date
              example: "1995-05-20"
            address:
              type: string
            emergencyContact:
              type: string
            medicalNotes:
              type: string
            joinDate:
              type: string
              format: date
              example: "2026-05-31"
            status:
              type: string
              example: active
            sendInvite:
              type: boolean
              example: true
    responses:
      201:
        description: Member created.
      400:
        description: Invalid input.
      403:
        description: User cannot create members.
      409:
        description: A member with this DNI already exists.
    """
    if not staff_required():
        return error_response("You do not have permission to create members.", 403)

    data = request.get_json(silent=True) or {}
    full_name = data.get("fullName", "").strip()
    email = normalize_email(data.get("email", "")) if data.get("email") else None
    phone = data.get("phone") or None
    send_invite = bool(data.get("sendInvite"))

    if not full_name:
        return error_response("Full name is required.", 400)

    if send_invite and not email:
        return error_response("Email is required to send an invite.", 400)

    if send_invite and not phone:
        return error_response("Phone is required to send an invite by WhatsApp.", 400)

    try:
        member = Member(
            full_name=full_name,
            dni=data.get("dni") or None,
            phone=phone,
            email=email,
            date_of_birth=parse_date(data.get("dateOfBirth")),
            address=data.get("address") or None,
            emergency_contact=data.get("emergencyContact") or None,
            medical_notes=data.get("medicalNotes") or None,
            join_date=parse_date(data.get("joinDate")) or date.today(),
            status=data.get("status") or "active",
        )

        db.session.add(member)
        db.session.flush()

        invite_url = None
        invite = None

        if send_invite and email:
            invite, token = create_member_invite(
                email=email,
                member_id=member.id,
                commit=False,
            )
            frontend_origin = current_app.config["PUBLIC_FRONTEND_ORIGIN"].rstrip("/")
            invite_url = f"{frontend_origin}/register?token={token}"

        db.session.commit()
    except ValueError:
        db.session.rollback()
        return error_response("One of the date fields is invalid.", 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("A member with this DNI already exists.", 409)

    whatsapp_delivery = None
    if invite_url:
        whatsapp_delivery = send_member_invite_whatsapp(member, invite_url)

    return (
        jsonify(
            {
                "member": member.to_dict(),
                "invite": invite.to_dict() if invite else None,
                "inviteUrl": invite_url,
                "whatsappDelivery": whatsapp_delivery,
            }
        ),
        201,
    )


@members_bp.post("/members/<int:member_id>/portal-invite")
@jwt_required()
def resend_member_portal_invite(member_id):
    """Create a fresh portal invite and send it to the member by WhatsApp.
    ---
    tags:
      - Members
    security:
      - cookieAuth: []
    responses:
      201:
        description: Fresh invite created and delivery attempted.
      400:
        description: Member is missing email or phone.
      403:
        description: User cannot send invites.
      404:
        description: Member was not found.
      409:
        description: Member already has a portal account.
    """
    if not staff_required():
        return error_response("You do not have permission to send invites.", 403)

    member = Member.query.get(member_id)
    if member is None:
        return error_response("Member was not found.", 404)

    if member.user_id is not None:
        return error_response("This member already has a portal account.", 409)

    if not member.email:
        return error_response("Member email is required to create an invite.", 400)

    if not member.phone:
        return error_response("Member phone is required to send the invite.", 400)

    invite, token = create_member_invite(
        email=member.email,
        member_id=member.id,
    )
    frontend_origin = current_app.config["PUBLIC_FRONTEND_ORIGIN"].rstrip("/")
    invite_url = f"{frontend_origin}/register?token={token}"
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
