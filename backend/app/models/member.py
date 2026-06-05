from datetime import date, datetime, timezone

from app.extensions import db


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    full_name = db.Column(db.String(255), nullable=False)
    dni = db.Column(db.String(32), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(32), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(500), nullable=True)
    emergency_contact = db.Column(db.String(255), nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    join_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(32), nullable=False, default="active", index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="member_profile")
    invites = db.relationship("MemberInvite", back_populates="member")
    subscriptions = db.relationship(
        "MemberSubscription",
        back_populates="member",
        order_by="MemberSubscription.end_date",
    )

    def to_dict(self):
        latest_invite = self.invites[-1] if self.invites else None
        current_subscription = self.subscriptions[-1] if self.subscriptions else None

        return {
            "id": self.id,
            "userId": self.user_id,
            "fullName": self.full_name,
            "dni": self.dni,
            "phone": self.phone,
            "email": self.email,
            "dateOfBirth": self.date_of_birth.isoformat()
            if self.date_of_birth
            else None,
            "address": self.address,
            "emergencyContact": self.emergency_contact,
            "medicalNotes": self.medical_notes,
            "photoUrl": self.photo_url,
            "joinDate": self.join_date.isoformat() if self.join_date else None,
            "status": self.status,
            "hasPortalAccount": self.user_id is not None,
            "latestInvite": latest_invite.to_dict() if latest_invite else None,
            "currentSubscription": current_subscription.to_dict()
            if current_subscription
            else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
