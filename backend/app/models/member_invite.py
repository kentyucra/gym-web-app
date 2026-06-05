from datetime import datetime, timezone

from app.extensions import db


class MemberInvite(db.Model):
    __tablename__ = "member_invites"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(
        db.Integer, db.ForeignKey("members.id"), nullable=True, index=True
    )
    email = db.Column(db.String(255), nullable=False, index=True)
    token_hash = db.Column(db.String(128), unique=True, nullable=False, index=True)
    role = db.Column(db.String(32), nullable=False, default="member")
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    accepted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    member = db.relationship("Member", back_populates="invites")

    def to_dict(self):
        return {
            "id": self.id,
            "memberId": self.member_id,
            "email": self.email,
            "role": self.role,
            "expiresAt": self.expires_at.isoformat(),
            "acceptedAt": self.accepted_at.isoformat() if self.accepted_at else None,
        }

