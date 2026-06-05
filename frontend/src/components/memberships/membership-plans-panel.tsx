"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarPlus, CreditCard, Send, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";

import {
  assignMemberSubscription,
  createMembershipPlan,
  getMembers,
  getMembershipPlans,
  previewMembershipReminders,
  sendMembershipReminders,
} from "@/lib/api";
import { Button } from "@/components/ui/button";

type PlanForm = {
  name: string;
  price: string;
  durationDays: string;
};

type AssignForm = {
  memberId: string;
  planId: string;
  startDate: string;
};

const initialPlanForm: PlanForm = {
  name: "",
  price: "",
  durationDays: "",
};

const initialAssignForm: AssignForm = {
  memberId: "",
  planId: "",
  startDate: new Date().toISOString().slice(0, 10),
};

const currency = new Intl.NumberFormat("es-PE", {
  style: "currency",
  currency: "PEN",
});

function statusLabel(status: string, daysRemaining: number) {
  if (status === "expired") return "Expired";
  if (status === "cancelled") return "Cancelled";
  if (status === "frozen") return "Frozen";
  if (daysRemaining <= 7) return "Expiring soon";
  return "Active";
}

export function MembershipPlansPanel() {
  const queryClient = useQueryClient();
  const [planForm, setPlanForm] = useState<PlanForm>(initialPlanForm);
  const [assignForm, setAssignForm] = useState<AssignForm>(initialAssignForm);
  const [sendResultCount, setSendResultCount] = useState<number | null>(null);

  const plansQuery = useQuery({
    queryKey: ["membership-plans"],
    queryFn: getMembershipPlans,
  });

  const membersQuery = useQuery({
    queryKey: ["members"],
    queryFn: getMembers,
  });

  const remindersQuery = useQuery({
    queryKey: ["membership-reminders"],
    queryFn: previewMembershipReminders,
  });

  const createPlanMutation = useMutation({
    mutationFn: () =>
      createMembershipPlan({
        name: planForm.name,
        priceCents: Math.round(Number(planForm.price) * 100),
        durationDays: Number(planForm.durationDays),
        isActive: true,
      }),
    onSuccess: async () => {
      setPlanForm(initialPlanForm);
      await queryClient.invalidateQueries({ queryKey: ["membership-plans"] });
    },
  });

  const assignMutation = useMutation({
    mutationFn: () =>
      assignMemberSubscription({
        memberId: Number(assignForm.memberId),
        planId: Number(assignForm.planId),
        startDate: assignForm.startDate,
        status: "active",
      }),
    onSuccess: async () => {
      setAssignForm(initialAssignForm);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["members"] }),
        queryClient.invalidateQueries({ queryKey: ["membership-reminders"] }),
      ]);
    },
  });

  const sendRemindersMutation = useMutation({
    mutationFn: sendMembershipReminders,
    onSuccess: async (data) => {
      setSendResultCount(data.results.length);
      await queryClient.invalidateQueries({ queryKey: ["membership-reminders"] });
    },
  });

  const plans = plansQuery.data?.plans ?? [];
  const members = membersQuery.data?.members ?? [];
  const reminders = remindersQuery.data?.reminders ?? [];
  const activePlans = plans.filter((plan) => plan.isActive);

  function handleCreatePlan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createPlanMutation.mutate();
  }

  function handleAssign(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    assignMutation.mutate();
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            <h2 className="text-xl font-semibold">Create plan</h2>
          </div>

          <form className="mt-5 space-y-4" onSubmit={handleCreatePlan}>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Name</span>
              <input
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                value={planForm.name}
                onChange={(event) =>
                  setPlanForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
                placeholder="Monthly"
                required
              />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block space-y-2">
                <span className="text-sm font-medium">Price</span>
                <input
                  className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                  value={planForm.price}
                  min="0"
                  step="0.01"
                  type="number"
                  onChange={(event) =>
                    setPlanForm((current) => ({
                      ...current,
                      price: event.target.value,
                    }))
                  }
                  placeholder="120"
                  required
                />
              </label>

              <label className="block space-y-2">
                <span className="text-sm font-medium">Duration days</span>
                <input
                  className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                  value={planForm.durationDays}
                  min="1"
                  type="number"
                  onChange={(event) =>
                    setPlanForm((current) => ({
                      ...current,
                      durationDays: event.target.value,
                    }))
                  }
                  placeholder="30"
                  required
                />
              </label>
            </div>

            {createPlanMutation.error ? (
              <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {createPlanMutation.error.message}
              </p>
            ) : null}

            <Button disabled={createPlanMutation.isPending} type="submit">
              <Sparkles />
              {createPlanMutation.isPending ? "Creating" : "Create plan"}
            </Button>
          </form>
        </section>

        <section className="rounded-lg border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <CalendarPlus className="h-5 w-5" />
            <h2 className="text-xl font-semibold">Assign plan</h2>
          </div>

          <form className="mt-5 space-y-4" onSubmit={handleAssign}>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Member</span>
              <select
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                value={assignForm.memberId}
                onChange={(event) =>
                  setAssignForm((current) => ({
                    ...current,
                    memberId: event.target.value,
                  }))
                }
                required
              >
                <option value="">Select member</option>
                {members.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.fullName}
                  </option>
                ))}
              </select>
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-medium">Plan</span>
              <select
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                value={assignForm.planId}
                onChange={(event) =>
                  setAssignForm((current) => ({
                    ...current,
                    planId: event.target.value,
                  }))
                }
                required
              >
                <option value="">Select plan</option>
                {activePlans.map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name} - {currency.format(plan.price)}
                  </option>
                ))}
              </select>
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-medium">Start date</span>
              <input
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                value={assignForm.startDate}
                type="date"
                onChange={(event) =>
                  setAssignForm((current) => ({
                    ...current,
                    startDate: event.target.value,
                  }))
                }
                required
              />
            </label>

            {assignMutation.error ? (
              <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {assignMutation.error.message}
              </p>
            ) : null}

            <Button disabled={assignMutation.isPending} type="submit">
              <CalendarPlus />
              {assignMutation.isPending ? "Assigning" : "Assign plan"}
            </Button>
          </form>
        </section>
      </div>

      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <h2 className="text-xl font-semibold">Plans</h2>
        <div className="mt-5 overflow-hidden rounded-md border">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/60 text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">Price</th>
                <th className="px-3 py-2 font-medium">Duration</th>
                <th className="px-3 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((plan) => (
                <tr key={plan.id} className="border-t">
                  <td className="px-3 py-3 font-medium">{plan.name}</td>
                  <td className="px-3 py-3">{currency.format(plan.price)}</td>
                  <td className="px-3 py-3">{plan.durationDays} days</td>
                  <td className="px-3 py-3">
                    {plan.isActive ? "Active" : "Inactive"}
                  </td>
                </tr>
              ))}
              {!plansQuery.isLoading && plans.length === 0 ? (
                <tr>
                  <td className="px-3 py-8 text-center text-muted-foreground" colSpan={4}>
                    No plans yet.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold">Reminder preview</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Members expired or expiring within 7 days.
            </p>
          </div>
          <Button
            disabled={sendRemindersMutation.isPending || reminders.length === 0}
            onClick={() => sendRemindersMutation.mutate()}
            type="button"
          >
            <Send />
            {sendRemindersMutation.isPending ? "Sending" : "Send reminders"}
          </Button>
        </div>

        {sendResultCount !== null ? (
          <p className="mt-4 rounded-md border bg-muted/40 px-3 py-2 text-sm">
            Sent reminder batch for {sendResultCount} member
            {sendResultCount === 1 ? "" : "s"}.
          </p>
        ) : null}

        <div className="mt-5 space-y-3">
          {reminders.map((reminder) => (
            <div key={reminder.subscription.id} className="rounded-md border p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-medium">{reminder.member.fullName}</p>
                <span className="text-sm text-muted-foreground">
                  {statusLabel(
                    reminder.subscription.computedStatus,
                    reminder.subscription.daysRemaining,
                  )}
                </span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                {reminder.message}
              </p>
            </div>
          ))}
          {!remindersQuery.isLoading && reminders.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No reminders due right now.
            </p>
          ) : null}
        </div>
      </section>
    </div>
  );
}
