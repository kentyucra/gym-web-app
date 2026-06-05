import { MemberSubscriptionCard } from "@/components/memberships/member-subscription-card";

export default function MemberPage() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto max-w-5xl space-y-4">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Member portal
          </p>
          <h1 className="text-3xl font-semibold">My membership</h1>
        </header>
        <MemberSubscriptionCard />
      </div>
    </main>
  );
}
