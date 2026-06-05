"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";

import { getHealth } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function ApiHealthCard() {
  const { data, error, isFetching, refetch } = useQuery({
    queryKey: ["api-health"],
    queryFn: getHealth,
  });

  const isConnected = data?.database === "connected";

  return (
    <section className="rounded-lg border bg-card p-5 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Activity className="h-4 w-4" />
            API connection
          </div>
          <h2 className="text-xl font-semibold">Flask health check</h2>
          <p className="max-w-xl text-sm text-muted-foreground">
            This confirms the Next.js frontend can call the Flask API and the
            backend can verify PostgreSQL connectivity.
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          <RefreshCw className={isFetching ? "animate-spin" : ""} />
          Refresh
        </Button>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-md border p-4">
          <p className="text-sm text-muted-foreground">API</p>
          <div className="mt-2 flex items-center gap-2 font-medium">
            {error ? (
              <AlertCircle className="h-4 w-4 text-destructive" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            )}
            {error ? "Unavailable" : data?.status ?? "Checking"}
          </div>
        </div>
        <div className="rounded-md border p-4">
          <p className="text-sm text-muted-foreground">Database</p>
          <div className="mt-2 flex items-center gap-2 font-medium">
            {isConnected ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            ) : (
              <AlertCircle className="h-4 w-4 text-amber-600" />
            )}
            {data?.database ?? "Checking"}
          </div>
        </div>
      </div>
    </section>
  );
}

