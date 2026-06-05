import Link from "next/link";
import { Dumbbell, UserRoundCog, UsersRound } from "lucide-react";

import { ApiHealthCard } from "@/components/health/api-health-card";
import { buttonVariants } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header className="flex flex-col gap-5 rounded-lg border bg-card p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Dumbbell className="h-4 w-4" />
              Site Fitness
            </div>
            <div className="space-y-2">
              <h1 className="text-3xl font-semibold tracking-normal sm:text-4xl">
                Gym management MVP
              </h1>
              <p className="max-w-2xl text-muted-foreground">
                First phase scaffold for the staff dashboard, member portal,
                Flask API, and PostgreSQL connection.
              </p>
            </div>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Link href="/admin" className={buttonVariants()}>
              <UserRoundCog />
              Admin
            </Link>
            <Link
              href="/member"
              className={buttonVariants({ variant: "outline" })}
            >
              <UsersRound />
              Member
            </Link>
          </div>
        </header>

        <ApiHealthCard />

        <section className="grid gap-4 md:grid-cols-3">
          {[
            ["Frontend", "Next.js, shadcn/ui, and TanStack Query"],
            ["Backend", "Flask API with SQLAlchemy and migrations"],
            ["Database", "PostgreSQL configured through Docker Compose"],
          ].map(([title, description]) => (
            <div key={title} className="rounded-lg border bg-card p-5 shadow-sm">
              <h2 className="font-semibold">{title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                {description}
              </p>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
