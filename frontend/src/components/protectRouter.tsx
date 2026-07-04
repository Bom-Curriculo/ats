import { getUser } from "@/api/user/get-user";
import { useQuery } from "@tanstack/react-query";
import { Navigate, Outlet } from "react-router-dom";

export function ProtectedRoute() {
  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: getUser,
    retry: false,
  });

  if (isLoading) {
    return <p>Loading...</p>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
