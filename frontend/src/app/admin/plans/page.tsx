import { MembershipPlansPanel } from "@/components/memberships/membership-plans-panel";

export default function PlansPage() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Membership management
          </p>
          <h1 className="text-3xl font-semibold">Plans and subscriptions</h1>
        </header>
        <MembershipPlansPanel />
      </div>
    </main>
  );
}
