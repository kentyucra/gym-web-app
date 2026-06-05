"use client";

import { useMutation } from "@tanstack/react-query";
import { ExternalLink, Image as ImageIcon, Search } from "lucide-react";
import { FormEvent, useState } from "react";

import { Button, buttonVariants } from "@/components/ui/button";
import { getMuscleImage, MuscleImage } from "@/lib/api";
import { cn } from "@/lib/utils";

function ResultCard({ muscle }: { muscle: MuscleImage }) {
  return (
    <section className="rounded-lg border bg-card p-5 shadow-sm">
      <div className="grid gap-5 lg:grid-cols-[360px_1fr]">
        <div className="overflow-hidden rounded-lg border bg-muted">
          {muscle.imageUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={muscle.imageUrl}
              alt={muscle.title ?? muscle.name}
              className="aspect-video w-full object-contain"
            />
          ) : (
            <div className="flex aspect-video items-center justify-center text-muted-foreground">
              <ImageIcon className="h-10 w-10" />
            </div>
          )}
        </div>

        <div className="min-w-0">
          <p className="text-sm font-medium text-muted-foreground">
            {muscle.description ?? "Muscle"}
          </p>
          <h2 className="mt-1 text-2xl font-semibold">
            {muscle.title ?? muscle.name}
          </h2>
          {muscle.matchedName && muscle.matchedName !== muscle.name ? (
            <p className="mt-2 text-sm text-muted-foreground">
              Matched from <span className="font-medium">{muscle.name}</span> to{" "}
              <span className="font-medium">{muscle.matchedName}</span>.
            </p>
          ) : null}
          {muscle.extract ? (
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              {muscle.extract}
            </p>
          ) : null}
          {muscle.pageUrl ? (
            <a
              className={cn(
                buttonVariants({ variant: "outline" }),
                "mt-5",
              )}
              href={muscle.pageUrl}
              target="_blank"
              rel="noreferrer"
            >
              <ExternalLink />
              Wikipedia
            </a>
          ) : null}
        </div>
      </div>
    </section>
  );
}

export function MuscleImageLookup() {
  const [muscleName, setMuscleName] = useState("Biceps brachii");
  const [result, setResult] = useState<MuscleImage | null>(null);

  const lookupMutation = useMutation({
    mutationFn: () => getMuscleImage(muscleName),
    onSuccess: (data) => setResult(data.muscle),
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    lookupMutation.mutate();
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <form className="grid gap-3 sm:grid-cols-[1fr_auto]" onSubmit={handleSubmit}>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Muscle name</span>
            <input
              className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={muscleName}
              onChange={(event) => setMuscleName(event.target.value)}
              placeholder="Biceps brachii"
              required
            />
          </label>

          <Button
            className="self-end"
            disabled={lookupMutation.isPending || !muscleName.trim()}
            type="submit"
          >
            <Search />
            {lookupMutation.isPending ? "Searching" : "Search"}
          </Button>
        </form>

        {lookupMutation.error ? (
          <p className="mt-4 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {lookupMutation.error.message}
          </p>
        ) : null}
      </section>

      {result ? <ResultCard muscle={result} /> : null}
    </div>
  );
}
