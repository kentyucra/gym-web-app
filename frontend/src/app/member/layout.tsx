import { ProtectedRoute } from "@/components/auth/protected-route";

export default function MemberLayout({ children }: { children: React.ReactNode }) {
  return <ProtectedRoute allowedRoles={["member"]}>{children}</ProtectedRoute>;
}
