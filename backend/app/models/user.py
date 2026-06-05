from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="member", index=True)
    status = db.Column(db.String(32), nullable=False, default="active", index=True)
    email_verified_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
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

    member_profile = db.relationship("Member", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "emailVerifiedAt": self.email_verified_at.isoformat()
            if self.email_verified_at
            else None,
            "lastLoginAt": self.last_login_at.isoformat()
            if self.last_login_at
            else None,
        }
