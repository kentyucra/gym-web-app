"""create auth tables

Revision ID: 20260531_0001
Revises:
Create Date: 2026-05-31 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260531_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_status"), "users", ["status"], unique=False)

    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("dni", sa.String(length=32), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("emergency_contact", sa.String(length=255), nullable=True),
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("join_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dni"),
    )
    op.create_index(op.f("ix_members_dni"), "members", ["dni"], unique=False)
    op.create_index(op.f("ix_members_email"), "members", ["email"], unique=False)
    op.create_index(op.f("ix_members_phone"), "members", ["phone"], unique=False)
    op.create_index(op.f("ix_members_status"), "members", ["status"], unique=False)
    op.create_index(op.f("ix_members_user_id"), "members", ["user_id"], unique=False)

    op.create_table(
        "member_invites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        op.f("ix_member_invites_email"), "member_invites", ["email"], unique=False
    )
    op.create_index(
        op.f("ix_member_invites_member_id"),
        "member_invites",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_member_invites_token_hash"),
        "member_invites",
        ["token_hash"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_member_invites_token_hash"), table_name="member_invites")
    op.drop_index(op.f("ix_member_invites_member_id"), table_name="member_invites")
    op.drop_index(op.f("ix_member_invites_email"), table_name="member_invites")
    op.drop_table("member_invites")

    op.drop_index(op.f("ix_members_user_id"), table_name="members")
    op.drop_index(op.f("ix_members_status"), table_name="members")
    op.drop_index(op.f("ix_members_phone"), table_name="members")
    op.drop_index(op.f("ix_members_email"), table_name="members")
    op.drop_index(op.f("ix_members_dni"), table_name="members")
    op.drop_table("members")

    op.drop_index(op.f("ix_users_status"), table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
