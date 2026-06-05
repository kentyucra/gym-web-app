import Link from "next/link";

const sections = [
  { href: "/admin/members", label: "Members" },
  { href: "/admin/notifications", label: "Notifications" },
  { href: "/admin/plans", label: "Plans" },
  { href: "/admin/training", label: "Training" },
  { href: "/admin/muscles", label: "Muscles" },
  { href: "/admin/check-ins", label: "Check-ins" },
  { href: "/admin/attendance", label: "Attendance" },
];

export default function AdminPage() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto max-w-5xl space-y-6">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Staff workspace
          </p>
          <h1 className="text-3xl font-semibold">Admin dashboard</h1>
        </header>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-7">
          {sections.map((section) => (
            <Link
              key={section.href}
              href={section.href}
              className="rounded-lg border bg-card p-5 font-medium shadow-sm transition hover:border-primary"
            >
              {section.label}
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
