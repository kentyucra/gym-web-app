import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import current_app


def normalize_whatsapp_chat_id(phone):
    if not phone:
        return None

    value = str(phone).strip()
    if value.endswith("@c.us"):
        return value

    digits = re.sub(r"\D", "", value)
    if digits.startswith("00"):
        digits = digits[2:]

    country_code = current_app.config["OPENWA_DEFAULT_COUNTRY_CODE"]
    if country_code and len(digits) == 9:
        digits = f"{country_code}{digits}"

    if not digits:
        return None

    return f"{digits}@c.us"


def openwa_is_configured():
    return bool(
        current_app.config["OPENWA_API_URL"]
        and current_app.config["OPENWA_API_KEY"]
        and current_app.config["OPENWA_SESSION_ID"]
    )


def send_whatsapp_text(phone, text):
    if not openwa_is_configured():
        return {"sent": False, "skipped": True, "reason": "OpenWA is not configured."}

    chat_id = normalize_whatsapp_chat_id(phone)
    if chat_id is None:
        return {"sent": False, "skipped": True, "reason": "Phone number is missing."}

    api_url = current_app.config["OPENWA_API_URL"]
    session_id = current_app.config["OPENWA_SESSION_ID"]
    timeout = current_app.config["OPENWA_TIMEOUT_SECONDS"]
    url = f"{api_url}/sessions/{session_id}/messages/send-text"
    payload = json.dumps({"chatId": chat_id, "text": text}).encode("utf-8")
    request = Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": current_app.config["OPENWA_API_KEY"],
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body) if body else {}
            return {"sent": True, "chatId": chat_id, "response": data}
    except HTTPError as error:
        body = error.read().decode("utf-8")
        current_app.logger.warning("OpenWA rejected WhatsApp message: %s", body)
        return {
            "sent": False,
            "chatId": chat_id,
            "error": body or str(error),
            "statusCode": error.code,
        }
    except (TimeoutError, URLError) as error:
        current_app.logger.warning("OpenWA WhatsApp message failed: %s", error)
        return {"sent": False, "chatId": chat_id, "error": str(error)}


def build_member_invite_message(member_name, email, invite_url):
    name = (member_name or "").strip() or "there"
    return (
        f"Welcome to Site Fitness, {name}!\n\n"
        "Your member portal is ready.\n"
        f"Login email: {email}\n\n"
        "Set up your password here:\n"
        f"{invite_url}\n\n"
        "After that, you can log in and manage your membership."
    )


def send_member_invite_whatsapp(member, invite_url):
    if member is None:
        return {"sent": False, "skipped": True, "reason": "Member was not found."}

    message = build_member_invite_message(member.full_name, member.email, invite_url)
    return send_whatsapp_text(member.phone, message)
