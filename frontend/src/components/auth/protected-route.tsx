"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LogOut } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";

import { getMe, logout, UserRole } from "@/lib/api";
import { Button } from "@/components/ui/button";

type ProtectedRouteProps = {
  allowedRoles: UserRole[];
  children: ReactNode;
};

export function ProtectedRoute({ allowedRoles, children }: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const queryClient = useQueryClient();

  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    retry: false,
  });

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: async () => {
      await queryClient.clear();
      router.push("/login");
    },
  });

  const user = meQuery.data?.user;
  const isAllowed = user && allowedRoles.includes(user.role);

  useEffect(() => {
    if (meQuery.isError) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [meQuery.isError, pathname, router]);

  if (meQuery.isLoading || meQuery.isError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-muted/30 p-6">
        <p className="text-sm text-muted-foreground">Checking session</p>
      </main>
    );
  }

  if (!isAllowed) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-muted/30 p-6">
        <section className="w-full max-w-sm rounded-lg border bg-card p-6 text-center shadow-sm">
          <h1 className="text-xl font-semibold">Access denied</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            This account does not have permission to view this area.
          </p>
          <Button
            className="mt-6 w-full"
            variant="outline"
            onClick={() => logoutMutation.mutate()}
          >
            <LogOut />
            Sign out
          </Button>
        </section>
      </main>
    );
  }

  return (
    <div>
      <div className="border-b bg-background px-6 py-3">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium">{user.email}</p>
            <p className="text-xs text-muted-foreground">{user.role}</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => logoutMutation.mutate()}
            disabled={logoutMutation.isPending}
          >
            <LogOut />
            Sign out
          </Button>
        </div>
      </div>
      {children}
    </div>
  );
}

