import { MemberRegistrationPanel } from "@/components/members/member-registration-panel";

export default function MembersPage() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Member management
          </p>
          <h1 className="text-3xl font-semibold">Members</h1>
        </header>
        <MemberRegistrationPanel />
      </div>
    </main>
  );
}
