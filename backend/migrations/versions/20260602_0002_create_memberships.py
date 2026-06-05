"""create memberships

Revision ID: 20260602_0002
Revises: 20260531_0001
Create Date: 2026-06-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260602_0002"
down_revision = "20260531_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "membership_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_membership_plans_is_active"),
        "membership_plans",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_membership_plans_name"),
        "membership_plans",
        ["name"],
        unique=False,
    )

    op.create_table(
        "member_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["membership_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_member_subscriptions_end_date"),
        "member_subscriptions",
        ["end_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_member_subscriptions_member_id"),
        "member_subscriptions",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_member_subscriptions_plan_id"),
        "member_subscriptions",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_member_subscriptions_start_date"),
        "member_subscriptions",
        ["start_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_member_subscriptions_status"),
        "member_subscriptions",
        ["status"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_member_subscriptions_status"), table_name="member_subscriptions")
    op.drop_index(
        op.f("ix_member_subscriptions_start_date"), table_name="member_subscriptions"
    )
    op.drop_index(op.f("ix_member_subscriptions_plan_id"), table_name="member_subscriptions")
    op.drop_index(
        op.f("ix_member_subscriptions_member_id"), table_name="member_subscriptions"
    )
    op.drop_index(op.f("ix_member_subscriptions_end_date"), table_name="member_subscriptions")
    op.drop_table("member_subscriptions")

    op.drop_index(op.f("ix_membership_plans_name"), table_name="membership_plans")
    op.drop_index(op.f("ix_membership_plans_is_active"), table_name="membership_plans")
    op.drop_table("membership_plans")
