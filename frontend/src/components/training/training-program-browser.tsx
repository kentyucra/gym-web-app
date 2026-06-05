"use client";

import { useQuery } from "@tanstack/react-query";
import {
  ChevronDown,
  ChevronUp,
  Dumbbell,
  ExternalLink,
  Library,
  Loader2,
  Play,
} from "lucide-react";
import { useMemo, useState } from "react";

import {
  Exercise,
  getTrainingProgram,
  getTrainingPrograms,
  TrainingDay,
  TrainingDayExercise,
  TrainingWeek,
} from "@/lib/api";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const MINIO_PUBLIC_URL =
  process.env.NEXT_PUBLIC_MINIO_PUBLIC_URL ?? "http://localhost:9000";

function statValue(value: string | null | undefined) {
  return value && value !== "N/A" ? value : "-";
}

function browserMediaUrl(value: string | null | undefined) {
  if (!value) return null;
  if (value.startsWith("http://") || value.startsWith("https://")) {
    return value;
  }
  if (value.startsWith("s3://")) {
    const path = value.replace("s3://", "");
    return `${MINIO_PUBLIC_URL.replace(/\/$/, "")}/${path}`;
  }
  return value;
}

function localVideoUrl(exercise: Exercise) {
  const localVideo = exercise.media?.find(
    (media) => media.sourceType === "local_video" && media.localPath,
  );
  return browserMediaUrl(localVideo?.localPath);
}

function thumbnailUrl(exercise: Exercise) {
  const localVideo = exercise.media?.find(
    (media) => media.sourceType === "local_video" && media.thumbnailPath,
  );
  return browserMediaUrl(localVideo?.thumbnailPath);
}

function preferredVideoUrl(exercise: Exercise) {
  return localVideoUrl(exercise) ?? exercise.youtubeUrl;
}

function isBrowserUrl(value: string | null | undefined) {
  return Boolean(value?.startsWith("http://") || value?.startsWith("https://"));
}

function ExerciseThumbnail({
  exercise,
  isExpanded,
}: {
  exercise: Exercise;
  isExpanded: boolean;
}) {
  const thumbnail = thumbnailUrl(exercise);

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-md border bg-muted sm:w-40">
      {isBrowserUrl(thumbnail) ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={thumbnail as string}
          alt=""
          className="h-full w-full object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-muted-foreground">
          <Dumbbell className="h-8 w-8" />
        </div>
      )}
      <div className="absolute inset-0 flex items-center justify-center bg-black/10">
        <span className="inline-flex size-9 items-center justify-center rounded-full bg-background/90 shadow-sm">
          {isExpanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <Play className="ml-0.5 h-4 w-4" />
          )}
        </span>
      </div>
    </div>
  );
}

function ExerciseCard({
  item,
  expandedMediaKey,
  onToggleMedia,
}: {
  item: TrainingDayExercise;
  expandedMediaKey: string | null;
  onToggleMedia: (mediaKey: string) => void;
}) {
  const mainMediaKey = `main-${item.id}`;
  const isExpanded = expandedMediaKey === mainMediaKey;
  const mainLocalVideoUrl = localVideoUrl(item.exercise);
  const mainYouTubeUrl = item.exercise.youtubeUrl;
  const canShowInlineVideo = isBrowserUrl(mainLocalVideoUrl);
  const fallbackVideoUrl = preferredVideoUrl(item.exercise);
  const expandedSubstitution = item.substitutions.find(
    (substitution) => expandedMediaKey === `substitution-${substitution.id}`,
  );
  const expandedSubstitutionVideoUrl = expandedSubstitution
    ? localVideoUrl(expandedSubstitution.exercise)
    : null;

  return (
    <article className="rounded-lg border bg-card p-4 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
        <button
          className="shrink-0 text-left"
          type="button"
          onClick={() => onToggleMedia(mainMediaKey)}
          aria-expanded={isExpanded}
          aria-label={`${isExpanded ? "Hide" : "Show"} ${item.exercise.name} video`}
        >
          <ExerciseThumbnail exercise={item.exercise} isExpanded={isExpanded} />
        </button>

        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-medium uppercase text-muted-foreground">
                Exercise {item.exerciseOrder}
              </p>
              <h3 className="mt-1 text-xl font-semibold leading-tight">
                {item.exercise.name}
              </h3>
            </div>

            <div className="flex flex-wrap gap-2">
              {canShowInlineVideo || fallbackVideoUrl ? (
                <button
                  className={cn(
                    buttonVariants({ size: "sm", variant: "outline" }),
                  )}
                  type="button"
                  onClick={() => onToggleMedia(mainMediaKey)}
                  aria-expanded={isExpanded}
                >
                  {isExpanded ? <ChevronUp /> : <ChevronDown />}
                  {isExpanded ? "Hide video" : "Show video"}
                </button>
              ) : null}
              {!canShowInlineVideo && mainYouTubeUrl ? (
                <a
                  className={cn(buttonVariants({ size: "sm", variant: "outline" }))}
                  href={mainYouTubeUrl}
                  target="_blank"
                  rel="noreferrer"
                >
                  <ExternalLink />
                  YouTube
                </a>
              ) : null}
            </div>
          </div>
        </div>
      </div>

      {isExpanded ? (
        <div className="mt-4 overflow-hidden rounded-lg border bg-black">
          {canShowInlineVideo ? (
            <video
              className="aspect-video w-full bg-black"
              src={mainLocalVideoUrl as string}
              poster={
                isBrowserUrl(thumbnailUrl(item.exercise))
                  ? (thumbnailUrl(item.exercise) as string)
                  : undefined
              }
              controls
              loop
              muted
              playsInline
              preload="metadata"
            />
          ) : mainYouTubeUrl ? (
            <div className="flex min-h-40 flex-col items-center justify-center gap-3 p-6 text-center text-sm text-white">
              <p>Local video is not available yet.</p>
              <a
                className={cn(
                  buttonVariants({ size: "sm", variant: "secondary" }),
                )}
                href={mainYouTubeUrl}
                target="_blank"
                rel="noreferrer"
              >
                <ExternalLink />
                Open YouTube
              </a>
            </div>
          ) : (
            <div className="flex min-h-32 items-center justify-center p-6 text-sm text-white">
              No video available.
            </div>
          )}
        </div>
      ) : null}

      <dl className="mt-4 grid gap-3 sm:grid-cols-4">
        <div className="rounded-md bg-muted px-3 py-2">
          <dt className="text-xs text-muted-foreground">Warm-up</dt>
          <dd className="text-sm font-medium">{statValue(item.warmupSets)}</dd>
        </div>
        <div className="rounded-md bg-muted px-3 py-2">
          <dt className="text-xs text-muted-foreground">Working sets</dt>
          <dd className="text-sm font-medium">{statValue(item.workingSets)}</dd>
        </div>
        <div className="rounded-md bg-muted px-3 py-2">
          <dt className="text-xs text-muted-foreground">Reps</dt>
          <dd className="text-sm font-medium">{statValue(item.reps)}</dd>
        </div>
        <div className="rounded-md bg-muted px-3 py-2">
          <dt className="text-xs text-muted-foreground">Rest</dt>
          <dd className="text-sm font-medium">{statValue(item.rest)}</dd>
        </div>
      </dl>

      <dl className="mt-3 grid gap-3 sm:grid-cols-3">
        <div className="rounded-md border px-3 py-2">
          <dt className="text-xs text-muted-foreground">Early set RPE</dt>
          <dd className="text-sm font-medium">{statValue(item.earlySetRpe)}</dd>
        </div>
        <div className="rounded-md border px-3 py-2">
          <dt className="text-xs text-muted-foreground">Last set RPE</dt>
          <dd className="text-sm font-medium">{statValue(item.lastSetRpe)}</dd>
        </div>
        <div className="rounded-md border px-3 py-2">
          <dt className="text-xs text-muted-foreground">Intensity</dt>
          <dd className="text-sm font-medium">
            {statValue(item.lastSetIntensityTechnique)}
          </dd>
        </div>
      </dl>

      {item.substitutions.length > 0 ? (
        <div className="mt-4">
          <p className="text-sm font-medium">Substitutions</p>
          <div className="mt-2 grid gap-2 sm:grid-cols-2">
            {item.substitutions.map((substitution) => {
              const substitutionLocalVideoUrl = localVideoUrl(
                substitution.exercise,
              );
              const substitutionYouTubeUrl = substitution.exercise.youtubeUrl;
              const canShowSubstitutionInline = isBrowserUrl(
                substitutionLocalVideoUrl,
              );
              const substitutionThumbnail = thumbnailUrl(substitution.exercise);
              const substitutionMediaKey = `substitution-${substitution.id}`;
              const isSubstitutionExpanded =
                expandedMediaKey === substitutionMediaKey;

              return (
                <div
                  key={substitution.id}
                  className={`flex min-h-16 items-center justify-between gap-3 rounded-md border px-3 py-2 ${
                    isSubstitutionExpanded ? "border-primary" : ""
                  }`}
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <button
                      className="relative size-12 shrink-0 overflow-hidden rounded-md border bg-muted disabled:cursor-default"
                      type="button"
                      onClick={() => onToggleMedia(substitutionMediaKey)}
                      disabled={!canShowSubstitutionInline}
                      aria-expanded={isSubstitutionExpanded}
                      aria-label={`${isSubstitutionExpanded ? "Hide" : "Show"} ${substitution.exercise.name} video`}
                    >
                      {isBrowserUrl(substitutionThumbnail) ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={substitutionThumbnail as string}
                          alt=""
                          className="h-full w-full object-cover"
                          loading="lazy"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center text-muted-foreground">
                          <Dumbbell className="h-4 w-4" />
                        </div>
                      )}
                      {canShowSubstitutionInline ? (
                        <span className="absolute inset-0 flex items-center justify-center bg-black/10">
                          <span className="inline-flex size-6 items-center justify-center rounded-full bg-background/90 shadow-sm">
                            {isSubstitutionExpanded ? (
                              <ChevronUp className="h-3 w-3" />
                            ) : (
                              <Play className="ml-0.5 h-3 w-3" />
                            )}
                          </span>
                        </span>
                      ) : null}
                    </button>
                    <div className="min-w-0">
                      <p className="text-xs text-muted-foreground">
                        Option {substitution.substitutionOrder}
                      </p>
                      <p className="break-words text-sm font-medium">
                        {substitution.exercise.name}
                      </p>
                    </div>
                  </div>
                  {canShowSubstitutionInline ? (
                    <button
                      className={cn(
                        buttonVariants({ size: "icon-sm", variant: "ghost" }),
                      )}
                      type="button"
                      onClick={() => onToggleMedia(substitutionMediaKey)}
                      aria-expanded={isSubstitutionExpanded}
                      aria-label={`${isSubstitutionExpanded ? "Hide" : "Show"} ${substitution.exercise.name} video`}
                    >
                      {isSubstitutionExpanded ? <ChevronUp /> : <Play />}
                    </button>
                  ) : substitutionYouTubeUrl ? (
                    <a
                      className={cn(
                        buttonVariants({ size: "icon-sm", variant: "ghost" }),
                      )}
                      href={substitutionYouTubeUrl}
                      target="_blank"
                      rel="noreferrer"
                      aria-label={`${substitution.exercise.name} YouTube video`}
                    >
                      <ExternalLink />
                    </a>
                  ) : null}
                </div>
              );
            })}
          </div>

          {expandedSubstitution && isBrowserUrl(expandedSubstitutionVideoUrl) ? (
            <div className="mt-3 overflow-hidden rounded-lg border bg-black">
              <video
                className="aspect-video w-full bg-black"
                src={expandedSubstitutionVideoUrl as string}
                poster={
                  isBrowserUrl(thumbnailUrl(expandedSubstitution.exercise))
                    ? (thumbnailUrl(expandedSubstitution.exercise) as string)
                    : undefined
                }
                controls
                loop
                muted
                playsInline
                preload="metadata"
              />
            </div>
          ) : null}
        </div>
      ) : null}

      {item.notes ? (
        <p className="mt-4 rounded-md bg-muted px-3 py-2 text-sm leading-6 text-muted-foreground">
          {item.notes}
        </p>
      ) : null}
    </article>
  );
}

function selectFirstDay(week: TrainingWeek | undefined) {
  return week?.days?.[0]?.dayNumber ?? null;
}

export function TrainingProgramBrowser() {
  const [selectedProgramId, setSelectedProgramId] = useState<number | null>(null);
  const [selectedWeekNumber, setSelectedWeekNumber] = useState<number | null>(null);
  const [selectedDayNumber, setSelectedDayNumber] = useState<number | null>(null);
  const [expandedMediaKey, setExpandedMediaKey] = useState<string | null>(null);

  const programsQuery = useQuery({
    queryKey: ["training-programs"],
    queryFn: getTrainingPrograms,
  });

  const programs = useMemo(
    () => programsQuery.data?.programs ?? [],
    [programsQuery.data?.programs],
  );
  const activeProgramId = selectedProgramId ?? programs[0]?.id ?? null;

  const programQuery = useQuery({
    queryKey: ["training-program", activeProgramId],
    queryFn: () => getTrainingProgram(activeProgramId as number),
    enabled: activeProgramId !== null,
  });

  const program = programQuery.data?.program;
  const weeks = useMemo(() => program?.weeks ?? [], [program?.weeks]);

  const selectedWeek = useMemo(
    () =>
      weeks.find((week) => week.weekNumber === selectedWeekNumber) ?? weeks[0],
    [selectedWeekNumber, weeks],
  );

  const days = useMemo(() => selectedWeek?.days ?? [], [selectedWeek?.days]);
  const selectedDay = useMemo(
    () => days.find((day) => day.dayNumber === selectedDayNumber) ?? days[0],
    [days, selectedDayNumber],
  );

  function handleProgramChange(programId: number) {
    setSelectedProgramId(programId);
    setSelectedWeekNumber(null);
    setSelectedDayNumber(null);
    setExpandedMediaKey(null);
  }

  function handleWeekChange(weekNumber: number) {
    const nextWeek = weeks.find((week) => week.weekNumber === weekNumber);
    setSelectedWeekNumber(weekNumber);
    setSelectedDayNumber(selectFirstDay(nextWeek));
    setExpandedMediaKey(null);
  }

  function handleDayChange(day: TrainingDay) {
    setSelectedDayNumber(day.dayNumber);
    setExpandedMediaKey(null);
  }

  if (programsQuery.isLoading) {
    return (
      <section className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading programs
        </span>
      </section>
    );
  }

  if (programsQuery.error) {
    return (
      <section className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
        {programsQuery.error.message}
      </section>
    );
  }

  if (programs.length === 0) {
    return (
      <section className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
        No training programs found.
      </section>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
          <label className="block space-y-2">
            <span className="text-sm font-medium">Program</span>
            <select
              className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={activeProgramId ?? ""}
              onChange={(event) => handleProgramChange(Number(event.target.value))}
            >
              {programs.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <div className="flex flex-wrap gap-2">
            {program?.level ? (
              <span className="rounded-md border px-3 py-2 text-sm capitalize">
                {program.level}
              </span>
            ) : null}
            {program?.sourceName ? (
              <span className="rounded-md border px-3 py-2 text-sm">
                {program.sourceName}
              </span>
            ) : null}
          </div>
        </div>
      </section>

      {programQuery.isLoading ? (
        <section className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading program
          </span>
        </section>
      ) : null}

      {programQuery.error ? (
        <section className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {programQuery.error.message}
        </section>
      ) : null}

      {program ? (
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <aside className="space-y-4">
            <section className="rounded-lg border bg-card p-4 shadow-sm">
              <div className="flex items-center gap-2">
                <Library className="h-4 w-4" />
                <h2 className="text-sm font-semibold">Weeks</h2>
              </div>
              <div className="mt-3 grid gap-2">
                {weeks.map((week) => (
                  <button
                    key={week.id}
                    className={`rounded-md border px-3 py-2 text-left text-sm transition ${
                      selectedWeek?.id === week.id
                        ? "border-primary bg-primary text-primary-foreground"
                        : "bg-background hover:bg-muted"
                    }`}
                    type="button"
                    onClick={() => handleWeekChange(week.weekNumber)}
                  >
                    <span className="font-medium">Week {week.weekNumber}</span>
                    {week.blockName ? (
                      <span className="mt-1 block text-xs opacity-75">
                        {week.blockName}
                      </span>
                    ) : null}
                  </button>
                ))}
              </div>
            </section>

            <section className="rounded-lg border bg-card p-4 shadow-sm">
              <div className="flex items-center gap-2">
                <Dumbbell className="h-4 w-4" />
                <h2 className="text-sm font-semibold">Days</h2>
              </div>
              <div className="mt-3 grid gap-2">
                {days.map((day) => (
                  <button
                    key={day.id}
                    className={`rounded-md border px-3 py-2 text-left text-sm transition ${
                      selectedDay?.id === day.id
                        ? "border-primary bg-primary text-primary-foreground"
                        : "bg-background hover:bg-muted"
                    }`}
                    type="button"
                    onClick={() => handleDayChange(day)}
                  >
                    <span className="font-medium">Day {day.dayNumber}</span>
                    <span className="mt-1 block text-xs opacity-75">
                      {day.dayLabel}
                    </span>
                  </button>
                ))}
              </div>
            </section>
          </aside>

          <section className="min-w-0 space-y-4">
            <header className="rounded-lg border bg-card p-5 shadow-sm">
              <p className="text-sm font-medium text-muted-foreground">
                Week {selectedWeek?.weekNumber ?? "-"} / Day{" "}
                {selectedDay?.dayNumber ?? "-"}
              </p>
              <h2 className="mt-1 text-2xl font-semibold">
                {selectedDay?.dayLabel ?? "No day selected"}
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">
                {selectedDay?.exercises?.length ?? 0} exercises
              </p>
            </header>

            {selectedDay?.exercises?.length ? (
              selectedDay.exercises.map((item) => (
                <ExerciseCard
                  key={item.id}
                  item={item}
                  expandedMediaKey={expandedMediaKey}
                  onToggleMedia={(mediaKey) =>
                    setExpandedMediaKey((current) =>
                      current === mediaKey ? null : mediaKey,
                    )
                  }
                />
              ))
            ) : (
              <section className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
                No exercises found for this day.
              </section>
            )}
          </section>
        </div>
      ) : null}
    </div>
  );
}
