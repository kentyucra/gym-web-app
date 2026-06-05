import { MuscleImageLookup } from "@/components/muscles/muscle-image-lookup";

export default function MusclesPage() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto max-w-5xl space-y-6">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Visual reference
          </p>
          <h1 className="text-3xl font-semibold">Muscle images</h1>
        </header>
        <MuscleImageLookup />
      </div>
    </main>
  );
}
