import { WhatsAppTestPanel } from "@/components/notifications/whatsapp-test-panel";

export default function NotificationsPage() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Notification tools
          </p>
          <h1 className="text-3xl font-semibold">Notifications</h1>
        </header>
        <WhatsAppTestPanel />
      </div>
    </main>
  );
}
