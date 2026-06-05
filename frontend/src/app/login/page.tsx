import { Suspense } from "react";

import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-muted/30 p-6">
      <section className="w-full max-w-sm rounded-lg border bg-card p-6 shadow-sm">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">Sign in</h1>
          <p className="text-sm text-muted-foreground">
            Use your staff, owner, trainer, or member account.
          </p>
        </div>
        <Suspense>
          <LoginForm />
        </Suspense>
      </section>
    </main>
  );
}
