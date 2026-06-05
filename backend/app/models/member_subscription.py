from datetime import date, datetime, timezone

from app.extensions import db


class MemberSubscription(db.Model):
    __tablename__ = "member_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(
        db.Integer, db.ForeignKey("members.id"), nullable=False, index=True
    )
    plan_id = db.Column(
        db.Integer, db.ForeignKey("membership_plans.id"), nullable=False, index=True
    )
    start_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
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

    member = db.relationship("Member", back_populates="subscriptions")
    plan = db.relationship("MembershipPlan", back_populates="subscriptions")

    @property
    def days_remaining(self):
        return (self.end_date - date.today()).days

    @property
    def computed_status(self):
        if self.status in {"cancelled", "frozen"}:
            return self.status

        return "expired" if self.end_date < date.today() else "active"

    @property
    def is_expiring_soon(self):
        return self.computed_status == "active" and 0 <= self.days_remaining <= 7

    def to_dict(self):
        return {
            "id": self.id,
            "memberId": self.member_id,
            "planId": self.plan_id,
            "plan": self.plan.to_dict() if self.plan else None,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "computedStatus": self.computed_status,
            "daysRemaining": self.days_remaining,
            "isExpiringSoon": self.is_expiring_soon,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
