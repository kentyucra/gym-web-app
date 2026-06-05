import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import Member, MemberInvite, User


def normalize_email(email):
    return email.strip().lower()


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_member_invite(email, member_id=None, role="member", days_valid=7, commit=True):
    token = secrets.token_urlsafe(32)
    invite = MemberInvite(
        email=normalize_email(email),
        member_id=member_id,
        role=role,
        token_hash=hash_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=days_valid),
    )
    db.session.add(invite)
    if commit:
        db.session.commit()

    return invite, token


def get_valid_member_invite(token):
    invite = MemberInvite.query.filter_by(token_hash=hash_token(token)).first()

    if invite is None:
        return None, "Invite token is invalid."

    if invite.accepted_at is not None:
        return None, "Invite has already been accepted."

    if invite.expires_at < datetime.now(timezone.utc):
        return None, "Invite has expired."

    return invite, None


def accept_member_invite(token, password):
    invite, error = get_valid_member_invite(token)
    if error:
        return None, error

    existing_user = User.query.filter_by(email=invite.email).first()
    if existing_user is not None:
        return None, "A user with this email already exists."

    user = User(
        email=invite.email,
        role=invite.role,
        status="active",
        email_verified_at=datetime.now(timezone.utc),
    )
    user.set_password(password)

    if invite.member_id:
        member = Member.query.get(invite.member_id)
        if member:
            member.user = user

    invite.accepted_at = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()

    return user, None
