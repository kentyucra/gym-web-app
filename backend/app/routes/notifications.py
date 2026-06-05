from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from app.routes.auth import error_response
from app.services.memberships import (
    build_membership_reminder_message,
    membership_reminder_candidates,
)
from app.services.openwa import send_whatsapp_text

notifications_bp = Blueprint("notifications", __name__)


def staff_required():
    return current_user.role in {"owner", "staff", "trainer"}


@notifications_bp.post("/notifications/whatsapp/test")
@jwt_required()
def send_test_whatsapp_message():
    """Send a test WhatsApp message through OpenWA.
    ---
    tags:
      - Notifications
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
            - phone
          properties:
            phone:
              type: string
              example: "948327856"
              description: Peru phone number, international number, or OpenWA chat ID.
            text:
              type: string
              example: "Hello from Site Fitness"
    responses:
      200:
        description: Test message request completed. Check delivery.sent for outcome.
      400:
        description: Phone is required.
      403:
        description: User cannot send test notifications.
    """
    if not staff_required():
        return error_response("You do not have permission to send notifications.", 403)

    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    text = data.get("text") or "Hello from Site Fitness"

    if not phone:
        return error_response("Phone is required.", 400)

    delivery = send_whatsapp_text(phone, text)

    return jsonify({"delivery": delivery})


@notifications_bp.get("/notifications/membership-reminders/preview")
@jwt_required()
def preview_membership_reminders():
    """Preview membership expiration reminders.
    ---
    tags:
      - Notifications
    security:
      - cookieAuth: []
    responses:
      200:
        description: Reminder candidates.
    """
    if not staff_required():
        return error_response("You do not have permission to view reminders.", 403)

    reminders = []
    for subscription in membership_reminder_candidates():
        reminders.append(
            {
                "member": subscription.member.to_dict(),
                "subscription": subscription.to_dict(),
                "message": build_membership_reminder_message(subscription),
            }
        )

    return jsonify({"reminders": reminders})


@notifications_bp.post("/notifications/membership-reminders/send")
@jwt_required()
def send_membership_reminders():
    """Send membership expiration reminders through OpenWA.
    ---
    tags:
      - Notifications
    security:
      - cookieAuth: []
    responses:
      200:
        description: Reminder delivery results.
    """
    if not staff_required():
        return error_response("You do not have permission to send reminders.", 403)

    results = []
    for subscription in membership_reminder_candidates():
        message = build_membership_reminder_message(subscription)
        delivery = send_whatsapp_text(subscription.member.phone, message)
        results.append(
            {
                "member": subscription.member.to_dict(),
                "subscription": subscription.to_dict(),
                "message": message,
                "delivery": delivery,
            }
        )

    return jsonify({"results": results})
