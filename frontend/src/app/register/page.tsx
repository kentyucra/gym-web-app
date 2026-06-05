import { Suspense } from "react";

import { RegisterForm } from "@/components/auth/register-form";

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-muted/30 p-6">
      <section className="w-full max-w-sm rounded-lg border bg-card p-6 shadow-sm">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">Create member account</h1>
          <p className="text-sm text-muted-foreground">
            Use the invite link sent by the gym to activate your portal access.
          </p>
        </div>
        <Suspense>
          <RegisterForm />
        </Suspense>
      </section>
    </main>
  );
}

