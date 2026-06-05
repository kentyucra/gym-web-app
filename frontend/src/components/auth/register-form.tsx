"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Eye, EyeOff } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { acceptMemberInvite, lookupMemberInvite } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const inviteQuery = useQuery({
    queryKey: ["member-invite", token],
    queryFn: () => lookupMemberInvite(token),
    enabled: Boolean(token),
    retry: false,
  });

  const mutation = useMutation({
    mutationFn: () => acceptMemberInvite(token, password),
    onSuccess: () => {
      router.push("/login");
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (password !== confirmPassword) {
      return;
    }
    mutation.mutate();
  }

  const passwordsMatch = password === confirmPassword;
  const invite = inviteQuery.data?.invite;

  return (
    <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
      {invite ? (
        <div className="rounded-md border bg-muted/40 px-3 py-2 text-sm">
          <p className="text-muted-foreground">Login email</p>
          <p className="mt-1 font-medium">{invite.email}</p>
        </div>
      ) : null}

      {inviteQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Checking invite</p>
      ) : null}

      {inviteQuery.error ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {inviteQuery.error.message}
        </p>
      ) : null}

      <label className="block space-y-2">
        <span className="text-sm font-medium">New password</span>
        <div className="relative">
          <input
            className="h-10 w-full rounded-md border bg-background px-3 pr-10 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
          />
          <button
            aria-label={showPassword ? "Hide password" : "Show password"}
            className="absolute right-2 top-1/2 inline-flex size-7 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground transition hover:bg-muted hover:text-foreground"
            type="button"
            onClick={() => setShowPassword((current) => !current)}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </label>

      <label className="block space-y-2">
        <span className="text-sm font-medium">Confirm password</span>
        <div className="relative">
          <input
            className="h-10 w-full rounded-md border bg-background px-3 pr-10 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
            type={showConfirmPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
          />
          <button
            aria-label={
              showConfirmPassword ? "Hide password" : "Show password"
            }
            className="absolute right-2 top-1/2 inline-flex size-7 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground transition hover:bg-muted hover:text-foreground"
            type="button"
            onClick={() => setShowConfirmPassword((current) => !current)}
          >
            {showConfirmPassword ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
      </label>

      {confirmPassword && !passwordsMatch ? (
        <p className="text-sm text-amber-700">Passwords do not match.</p>
      ) : null}

      {!token ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          Invite token is missing.
        </p>
      ) : null}

      {mutation.error ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {mutation.error.message}
        </p>
      ) : null}

      <Button
        className="w-full"
        disabled={
          !token ||
          !invite ||
          !passwordsMatch ||
          inviteQuery.isLoading ||
          mutation.isPending
        }
        type="submit"
      >
        {mutation.isPending ? "Creating account" : "Create account"}
      </Button>
    </form>
  );
}
