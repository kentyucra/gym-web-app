from datetime import datetime, timezone

from app.extensions import db


class MembershipPlan(db.Model):
    __tablename__ = "membership_plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    price_cents = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
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

    subscriptions = db.relationship("MemberSubscription", back_populates="plan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "priceCents": self.price_cents,
            "price": self.price_cents / 100,
            "durationDays": self.duration_days,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
