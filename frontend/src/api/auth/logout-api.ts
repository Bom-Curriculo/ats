import { APICONNECTBACKEND } from "@/helpers/api-connect";

export async function LogoutApi() {
  const token = localStorage.getItem("token");

  const response = await fetch(`${APICONNECTBACKEND}/auth/logout`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Logout failed");
  }

  localStorage.removeItem("token");

  return response.json();
}