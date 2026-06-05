from datetime import date, timedelta

from app.models import MemberSubscription


def calculate_end_date(start_date, duration_days):
    return start_date + timedelta(days=duration_days - 1)


def active_subscription_query():
    return MemberSubscription.query.filter(MemberSubscription.status == "active")


def membership_reminder_candidates(days=7):
    today = date.today()
    soon = today + timedelta(days=days)
    subscriptions = (
        active_subscription_query()
        .filter(MemberSubscription.end_date <= soon)
        .order_by(MemberSubscription.end_date.asc())
        .all()
    )

    return [
        subscription
        for subscription in subscriptions
        if subscription.member and subscription.member.phone
    ]


def build_membership_reminder_message(subscription):
    member_name = subscription.member.full_name
    plan_name = subscription.plan.name if subscription.plan else "membership"
    days = subscription.days_remaining

    if subscription.computed_status == "expired":
        return (
            f"Hi {member_name}, your Site Fitness {plan_name} membership expired "
            f"on {subscription.end_date.isoformat()}. Please contact us to renew."
        )

    if days == 0:
        timing = "expires today"
    elif days == 1:
        timing = "expires tomorrow"
    else:
        timing = f"expires in {days} days"

    return (
        f"Hi {member_name}, your Site Fitness {plan_name} membership {timing}. "
        "Please renew to keep your access active."
    )
