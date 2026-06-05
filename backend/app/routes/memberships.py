from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Member, MemberSubscription, MembershipPlan
from app.routes.auth import error_response
from app.services.memberships import calculate_end_date

memberships_bp = Blueprint("memberships", __name__)


def parse_date(value):
    if not value:
        return None

    return date.fromisoformat(value)


def staff_required():
    return current_user.role in {"owner", "staff", "trainer"}


@memberships_bp.get("/membership-plans")
@jwt_required()
def list_membership_plans():
    """List membership plans.
    ---
    tags:
      - Memberships
    security:
      - cookieAuth: []
    responses:
      200:
        description: Membership plans.
    """
    plans = MembershipPlan.query.order_by(MembershipPlan.created_at.desc()).all()
    return jsonify({"plans": [plan.to_dict() for plan in plans]})


@memberships_bp.post("/membership-plans")
@jwt_required()
def create_membership_plan():
    """Create a membership plan.
    ---
    tags:
      - Memberships
    security:
      - cookieAuth: []
    responses:
      201:
        description: Plan created.
    """
    if not staff_required():
        return error_response("You do not have permission to create plans.", 403)

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    price_cents = data.get("priceCents")
    duration_days = data.get("durationDays")

    if not name:
        return error_response("Plan name is required.", 400)

    try:
        price_cents = int(price_cents)
        duration_days = int(duration_days)
    except (TypeError, ValueError):
        return error_response("Price and duration are required.", 400)

    if price_cents < 0 or duration_days <= 0:
        return error_response("Price and duration must be positive.", 400)

    plan = MembershipPlan(
        name=name,
        price_cents=price_cents,
        duration_days=duration_days,
        is_active=bool(data.get("isActive", True)),
    )

    try:
        db.session.add(plan)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response("A plan with this name already exists.", 409)

    return jsonify({"plan": plan.to_dict()}), 201


@memberships_bp.post("/members/<int:member_id>/subscriptions")
@jwt_required()
def assign_member_subscription(member_id):
    """Assign a membership plan to a member.
    ---
    tags:
      - Memberships
    security:
      - cookieAuth: []
    responses:
      201:
        description: Subscription assigned.
    """
    if not staff_required():
        return error_response("You do not have permission to assign plans.", 403)

    data = request.get_json(silent=True) or {}
    member = Member.query.get(member_id)
    if member is None:
        return error_response("Member was not found.", 404)

    plan = MembershipPlan.query.get(data.get("planId"))
    if plan is None:
        return error_response("Plan was not found.", 404)

    start_date = parse_date(data.get("startDate")) or date.today()
    end_date = parse_date(data.get("endDate")) or calculate_end_date(
        start_date, plan.duration_days
    )

    subscription = MemberSubscription(
        member_id=member.id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=end_date,
        status=data.get("status") or "active",
    )
    db.session.add(subscription)
    member.status = "active"
    db.session.commit()

    return jsonify({"subscription": subscription.to_dict()}), 201


@memberships_bp.get("/member/subscription")
@jwt_required()
def my_member_subscription():
    """Get the current member portal subscription.
    ---
    tags:
      - Memberships
    security:
      - cookieAuth: []
    responses:
      200:
        description: Current member subscription.
    """
    member = current_user.member_profile
    if member is None:
        return error_response("This user is not linked to a member profile.", 404)

    subscription = member.subscriptions[-1] if member.subscriptions else None
    return jsonify(
        {
            "member": member.to_dict(),
            "subscription": subscription.to_dict() if subscription else None,
        }
    )
