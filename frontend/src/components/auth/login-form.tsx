"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { login } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const mutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: async ({ user }) => {
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      const next = searchParams.get("next");

      if (next?.startsWith("/")) {
        router.push(next);
        return;
      }

      router.push(user.role === "member" ? "/member" : "/admin");
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    mutation.mutate();
  }

  return (
    <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
      <label className="block space-y-2">
        <span className="text-sm font-medium">Email</span>
        <input
          className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
        />
      </label>

      <label className="block space-y-2">
        <span className="text-sm font-medium">Password</span>
        <input
          className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />
      </label>

      {mutation.error ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {mutation.error.message}
        </p>
      ) : null}

      <Button className="w-full" disabled={mutation.isPending} type="submit">
        {mutation.isPending ? "Signing in" : "Sign in"}
      </Button>
    </form>
  );
}

