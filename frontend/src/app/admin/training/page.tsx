import { TrainingProgramBrowser } from "@/components/training/training-program-browser";

export default function TrainingPage() {
  return (
    <main className="min-h-screen bg-muted/30 p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Exercise library
          </p>
          <h1 className="text-3xl font-semibold">Training programs</h1>
        </header>
        <TrainingProgramBrowser />
      </div>
    </main>
  );
}
