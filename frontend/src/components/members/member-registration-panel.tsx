"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  CircleCheck,
  MailPlus,
  Send,
  UserPlus,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import {
  CreateMemberResponse,
  Member,
  PortalInviteResponse,
  createMember,
  getMembers,
  resendMemberPortalInvite,
} from "@/lib/api";
import { Button } from "@/components/ui/button";

type FormState = {
  fullName: string;
  dni: string;
  phone: string;
  email: string;
  dateOfBirth: string;
  address: string;
  emergencyContact: string;
  medicalNotes: string;
  joinDate: string;
  sendInvite: boolean;
};

const initialForm: FormState = {
  fullName: "",
  dni: "",
  phone: "",
  email: "",
  dateOfBirth: "",
  address: "",
  emergencyContact: "",
  medicalNotes: "",
  joinDate: new Date().toISOString().slice(0, 10),
  sendInvite: true,
};

function membershipStatus(member: Member) {
  const subscription = member.currentSubscription;
  if (!subscription) return "No plan";
  if (subscription.computedStatus === "expired") return "Expired";
  if (subscription.computedStatus === "frozen") return "Frozen";
  if (subscription.computedStatus === "cancelled") return "Cancelled";
  if (subscription.isExpiringSoon) return "Expiring soon";
  return "Active";
}

export function MemberRegistrationPanel() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<FormState>(initialForm);
  const [lastResult, setLastResult] = useState<CreateMemberResponse | null>(null);
  const [inviteResult, setInviteResult] = useState<{
    memberName: string;
    result: PortalInviteResponse;
  } | null>(null);

  const membersQuery = useQuery({
    queryKey: ["members"],
    queryFn: getMembers,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createMember({
        fullName: form.fullName,
        dni: form.dni,
        phone: form.phone,
        email: form.email,
        dateOfBirth: form.dateOfBirth,
        address: form.address,
        emergencyContact: form.emergencyContact,
        medicalNotes: form.medicalNotes,
        joinDate: form.joinDate,
        status: "active",
        sendInvite: form.sendInvite,
    }),
    onSuccess: async (data) => {
      setLastResult(data);
      setForm(initialForm);
      await queryClient.invalidateQueries({ queryKey: ["members"] });
    },
  });

  const resendInviteMutation = useMutation({
    mutationFn: (member: Member) => resendMemberPortalInvite(member.id),
    onSuccess: async (data, member) => {
      setInviteResult({ memberName: member.fullName, result: data });
      await queryClient.invalidateQueries({ queryKey: ["members"] });
    },
  });

  const members = membersQuery.data?.members ?? [];
  const canSendInvite = useMemo(
    () => form.email.trim().length > 0 && form.phone.trim().length > 0,
    [form.email, form.phone],
  );
  const hasStartedInviteFields =
    form.email.trim().length > 0 || form.phone.trim().length > 0;

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.mutate();
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,420px)_1fr]">
      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <UserPlus className="h-5 w-5" />
          <h2 className="text-xl font-semibold">Register member</h2>
        </div>

        <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Full name</span>
            <input
              className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={form.fullName}
              onChange={(event) => updateField("fullName", event.target.value)}
              required
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-medium">DNI</span>
              <input
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                value={form.dni}
                onChange={(event) => updateField("dni", event.target.value)}
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-medium">Phone</span>
              <input
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                value={form.phone}
                onChange={(event) => updateField("phone", event.target.value)}
              />
            </label>
          </div>

          <label className="block space-y-2">
            <span className="text-sm font-medium">Email</span>
            <input
              className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              type="email"
              value={form.email}
              onChange={(event) => updateField("email", event.target.value)}
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-medium">Date of birth</span>
              <input
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                type="date"
                value={form.dateOfBirth}
                onChange={(event) =>
                  updateField("dateOfBirth", event.target.value)
                }
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-medium">Join date</span>
              <input
                className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
                type="date"
                value={form.joinDate}
                onChange={(event) => updateField("joinDate", event.target.value)}
              />
            </label>
          </div>

          <label className="block space-y-2">
            <span className="text-sm font-medium">Address</span>
            <input
              className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={form.address}
              onChange={(event) => updateField("address", event.target.value)}
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium">Emergency contact</span>
            <input
              className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={form.emergencyContact}
              onChange={(event) =>
                updateField("emergencyContact", event.target.value)
              }
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium">Medical notes</span>
            <textarea
              className="min-h-20 w-full rounded-md border bg-background px-3 py-2 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={form.medicalNotes}
              onChange={(event) =>
                updateField("medicalNotes", event.target.value)
              }
            />
          </label>

          <label className="flex items-center gap-3 rounded-md border p-3 text-sm">
            <input
              className="h-4 w-4"
              type="checkbox"
              checked={form.sendInvite}
              onChange={(event) =>
                updateField("sendInvite", event.target.checked)
              }
            />
            <span>Send member portal invite by WhatsApp</span>
          </label>

          {form.sendInvite && hasStartedInviteFields && !canSendInvite ? (
            <p className="text-sm text-amber-700">
              Add an email address and phone number to send the invite.
            </p>
          ) : null}

          {createMutation.error ? (
            <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {createMutation.error.message}
            </p>
          ) : null}

          <Button
            className="w-full"
            disabled={createMutation.isPending || (form.sendInvite && !canSendInvite)}
            type="submit"
          >
            <MailPlus />
            {createMutation.isPending ? "Registering" : "Register member"}
          </Button>
        </form>

        {lastResult ? (
          <div className="mt-5 rounded-md border bg-muted/40 p-3">
            <div className="space-y-3">
              <div className="flex items-start gap-2">
                <CircleCheck className="mt-0.5 h-4 w-4 text-emerald-600" />
                <div>
                  <p className="text-sm font-medium">Member created</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {lastResult.member.fullName} was added to the member list.
                  </p>
                </div>
              </div>

              {lastResult.inviteUrl ? (
                <div className="flex items-start gap-2">
                  <CircleCheck className="mt-0.5 h-4 w-4 text-emerald-600" />
                  <div>
                    <p className="text-sm font-medium">Portal invite generated</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      The password setup link was created for this member.
                    </p>
                  </div>
                </div>
              ) : null}

              {lastResult.whatsappDelivery ? (
                <div className="flex items-start gap-2">
                  {lastResult.whatsappDelivery.sent ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-600" />
                  ) : (
                    <AlertCircle className="mt-0.5 h-4 w-4 text-amber-700" />
                  )}
                  <div>
                    <p className="text-sm font-medium">
                      {lastResult.whatsappDelivery.sent
                        ? "WhatsApp invite sent"
                        : "WhatsApp invite not sent"}
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {lastResult.whatsappDelivery.sent
                        ? `Delivered to ${lastResult.whatsappDelivery.chatId}.`
                        : lastResult.whatsappDelivery.reason ||
                          lastResult.whatsappDelivery.error ||
                          "OpenWA did not confirm delivery."}
                    </p>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        {inviteResult ? (
          <div className="mt-5 rounded-md border bg-muted/40 p-3">
            <div className="flex items-start gap-2">
              {inviteResult.result.whatsappDelivery?.sent ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-600" />
              ) : (
                <AlertCircle className="mt-0.5 h-4 w-4 text-amber-700" />
              )}
              <div>
                <p className="text-sm font-medium">
                  {inviteResult.result.whatsappDelivery?.sent
                    ? "Portal invite resent"
                    : "Portal invite created"}
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {inviteResult.result.whatsappDelivery?.sent
                    ? `${inviteResult.memberName} received a fresh setup link at ${inviteResult.result.whatsappDelivery.chatId}.`
                    : inviteResult.result.whatsappDelivery?.reason ||
                      inviteResult.result.whatsappDelivery?.error ||
                      "WhatsApp delivery was not confirmed."}
                </p>
              </div>
            </div>
          </div>
        ) : null}

        {resendInviteMutation.error ? (
          <p className="mt-5 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {resendInviteMutation.error.message}
          </p>
        ) : null}
      </section>

      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <h2 className="text-xl font-semibold">Recent members</h2>
        <div className="mt-5 overflow-hidden rounded-md border">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/60 text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">DNI</th>
                <th className="px-3 py-2 font-medium">Email</th>
                <th className="px-3 py-2 font-medium">Plan</th>
                <th className="px-3 py-2 font-medium">Ends</th>
                <th className="px-3 py-2 font-medium">Membership</th>
                <th className="px-3 py-2 font-medium">Portal</th>
                <th className="px-3 py-2 font-medium">Invite</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id} className="border-t">
                  <td className="px-3 py-3 font-medium">{member.fullName}</td>
                  <td className="px-3 py-3 text-muted-foreground">
                    {member.dni || "-"}
                  </td>
                  <td className="px-3 py-3 text-muted-foreground">
                    {member.email || "-"}
                  </td>
                  <td className="px-3 py-3 text-muted-foreground">
                    {member.currentSubscription?.plan?.name || "-"}
                  </td>
                  <td className="px-3 py-3 text-muted-foreground">
                    {member.currentSubscription?.endDate || "-"}
                  </td>
                  <td className="px-3 py-3">
                    {membershipStatus(member)}
                    {member.currentSubscription ? (
                      <span className="block text-xs text-muted-foreground">
                        {member.currentSubscription.daysRemaining} days remaining
                      </span>
                    ) : null}
                  </td>
                  <td className="px-3 py-3">
                    {member.hasPortalAccount ? "Active" : "Not active"}
                  </td>
                  <td className="px-3 py-3">
                    {!member.hasPortalAccount ? (
                      <Button
                        size="sm"
                        type="button"
                        variant="outline"
                        disabled={resendInviteMutation.isPending}
                        onClick={() => resendInviteMutation.mutate(member)}
                      >
                        <Send />
                        Resend
                      </Button>
                    ) : (
                      <span className="text-sm text-muted-foreground">-</span>
                    )}
                  </td>
                </tr>
              ))}
              {!membersQuery.isLoading && members.length === 0 ? (
                <tr>
                  <td
                    className="px-3 py-8 text-center text-muted-foreground"
                    colSpan={8}
                  >
                    No members yet.
                  </td>
                </tr>
              ) : null}
              {membersQuery.isLoading ? (
                <tr>
                  <td
                    className="px-3 py-8 text-center text-muted-foreground"
                    colSpan={8}
                  >
                    Loading members
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
