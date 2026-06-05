"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { getMySubscription } from "@/lib/api";

function statusLabel(status: string, isExpiringSoon: boolean) {
  if (status === "expired") return "Expired";
  if (status === "frozen") return "Frozen";
  if (status === "cancelled") return "Cancelled";
  if (isExpiringSoon) return "Expiring soon";
  return "Active";
}

export function MemberSubscriptionCard() {
  const subscriptionQuery = useQuery({
    queryKey: ["my-subscription"],
    queryFn: getMySubscription,
  });

  if (subscriptionQuery.isLoading) {
    return (
      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <p className="text-sm text-muted-foreground">Loading membership</p>
      </section>
    );
  }

  const subscription = subscriptionQuery.data?.subscription;

  if (!subscription) {
    return (
      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <h2 className="text-xl font-semibold">No active plan</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Your membership plan is not assigned yet. Please contact the front desk.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border bg-card p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            Current plan
          </p>
          <h2 className="text-2xl font-semibold">
            {subscription.plan?.name || "Membership"}
          </h2>
        </div>
        <span className="rounded-md border px-3 py-1 text-sm font-medium">
          {statusLabel(subscription.computedStatus, subscription.isExpiringSoon)}
        </span>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <div>
          <p className="text-sm text-muted-foreground">Start date</p>
          <p className="mt-1 font-medium">{subscription.startDate}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">End date</p>
          <p className="mt-1 font-medium">{subscription.endDate}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Days remaining</p>
          <p className="mt-1 font-medium">{subscription.daysRemaining}</p>
        </div>
      </div>

      <Link
        href="/member/attendance"
        className="mt-6 inline-flex rounded-lg border bg-background px-4 py-3 font-medium shadow-sm transition hover:border-primary"
      >
        View attendance
      </Link>
    </section>
  );
}
